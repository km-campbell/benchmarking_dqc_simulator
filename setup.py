"""This is similar to from_monolithic_circuit.py but has been adapted to collect data from multiple circuits"""

import itertools as it
import os
import re

import netsquid as ns
from netsquid.qubits import QFormalism, qubitapi as qapi
import pandas as pd

from dqc_simulator.hardware.connections import BlackBoxEntanglingQsourceConnection
from dqc_simulator.hardware.dqc_creation import DQC
from dqc_simulator.hardware.quantum_processors import NoisyQPU
from dqc_simulator.qlib.states import werner_state
from dqc_simulator.software.compilers import (
    sort_many_qpus_greedily_by_node_and_time as default_compiler,
)
from dqc_simulator.software.compiler_preprocessing import (
    preprocess_qasm_to_compilable_monolithic as preprocess,
)
from dqc_simulator.software.dqc_control import DQCMasterProtocol
from dqc_simulator.software.partitioner import (
    first_come_first_served_qubits_to_qpus as allocate,
    partition_gate_tuples as partition,
)
from dqc_simulator.util.helper import processify

def setup_hardware(
    F_werner=1,
    p_depolar_error_cnot=0,
    single_qubit_gate_error_prob=0,
    meas_error_prob=0,
    memory_depolar_rate=0,
):
    ent_dist_rate = 182  # Hz

    # Defining QPU
    qpu_class = NoisyQPU
    kwargs4qpu = {
        "p_depolar_error_cnot": p_depolar_error_cnot,
        "single_qubit_gate_error_prob": single_qubit_gate_error_prob,
        "meas_error_prob": meas_error_prob,
        "comm_qubit_depolar_rate": memory_depolar_rate,
        "proc_qubit_depolar_rate": memory_depolar_rate,
        "single_qubit_gate_time": 135 * 10**3,
        "two_qubit_gate_time": 600 * 10**3,
        "measurement_time": 600 * 10**4,
        "num_positions": 10,
        "num_comm_qubits": 2,
    }

    # Defining connection
    entangling_connection_class = BlackBoxEntanglingQsourceConnection
    kwargs4conn = {
        "delay": 1e9 / ent_dist_rate,  # 1e9 used because ent_dist_rate in Hz
        "state4distribution": werner_state(F_werner),
    }

    # Setting up the hardware
    num_qpus = 3
    quantum_topology = list(it.combinations(range(3), 2))
    classical_topology = list(it.combinations(range(3), 2))
    dqc = DQC(
        entangling_connection_class,
        num_qpus,
        quantum_topology,
        classical_topology,
        qpu_class=qpu_class,
        **kwargs4qpu,
        **kwargs4conn,
    )
    return dqc


def setup_sim(dqc, circuit_filepath):
    # Retrieving QPU nodes from DQC
    nodes = list(dqc.nodes.values())

    # import .qasm file and convert to gate_tuples for monolithic_circuit
    include_path = "./circuits/"  # assuming qelib1.inc is in current working directory
    monolithic_circuit = preprocess(circuit_filepath, include_path=include_path)
    monolithic_circuit = monolithic_circuit.ops  # gate_tuples

    # Determine allocation of processing qubits to QPUs
    old_to_new_lookup, proc_qubit_allocation4each_qpu = allocate(
        monolithic_circuit, list(dqc.nodes.values())
    )

    # Partition according to the previously defined qubit allocation
    scheme = "cat"  # the remote gate scheme to use
    partitioned_gate_tuples = partition(
        monolithic_circuit,
        dqc,  # defined earlier in tutorial
        scheme,
        old_to_new_lookup,
        proc_qubit_allocation4each_qpu,
    )
    # Setting up the software
    protocol = DQCMasterProtocol(
        partitioned_gate_tuples, nodes=dqc.nodes, compiler_func=default_compiler
    )
    return protocol, nodes


def take_experimental_shot(
    circuit_filepath,
    F_werner=1,
    p_depolar_error_cnot=0,
    single_qubit_gate_error_prob=0,
    meas_error_prob=0,
    memory_depolar_rate=0,
):
    # Setting the formalism used to the density matrix formalism
    ns.set_qstate_formalism(QFormalism.DM)

    # Restting the state of the simulation (this is good practice)
    ns.sim_reset()

    # Setting up the hardware, software and data collection
    dqc = setup_hardware(
        F_werner=F_werner,
        p_depolar_error_cnot=p_depolar_error_cnot,
        single_qubit_gate_error_prob=single_qubit_gate_error_prob,
        meas_error_prob=meas_error_prob,
        memory_depolar_rate=memory_depolar_rate,
    )
    protocol, nodes = setup_sim(dqc, circuit_filepath)

    # Running the circuit
    protocol.start()
    ns.sim_run()

    qubits_2b_checked = []
    for node in nodes:
        positions = node.qmemory.processing_qubit_positions
        qubits = node.qmemory.pop(positions)
        qubits_2b_checked += [qubit for qubit in qubits if qubit is not None]
    return qubits_2b_checked

@processify
def get_fidelity(
                 circuit, 
                 F_werner,
                 p_depolar_error_cnot,
                 single_qubit_gate_error_prob,
                 meas_error_prob,
                 memory_depolar_rate):
    # Run ideal shot
    ideal_qubits = take_experimental_shot(circuit)
    actual_qubits = take_experimental_shot(
        circuit,
        F_werner=F_werner,
        p_depolar_error_cnot=p_depolar_error_cnot,
        single_qubit_gate_error_prob=single_qubit_gate_error_prob,
        meas_error_prob=meas_error_prob,
        memory_depolar_rate=memory_depolar_rate,
    )
    desired_state = qapi.reduced_dm(ideal_qubits)
    fidelity = qapi.fidelity(actual_qubits, desired_state, squared=True)
    return fidelity


def save(data: pd.DataFrame,
         filename: str # should include path to file
):
    # if file does not exist write data with header
    if not os.path.isfile(filename):
        data.to_csv(filename)
    else:  # if file already exists, append without writing header
        data.to_csv(filename, mode="a", header=False)

def find_num_qubits(
    filename: str # should be for circuit file. Can be name or path
):
    # Regular expression to match a number only if it is followed by the word qubits
    regex = re.compile(r'(\d+)(?=qubits\.qasm)')

    # Search filename for the number of qubits using the regular expression
    try:
        num_qubits = int(regex.search(filename).group(0))
    except AttributeError:
        num_qubits = None
    return num_qubits
    
def find_circuit_name(
    filename: str, # should be for circuit file. Can be name or path
) -> str | None:
    # Regular expression to match a group of lower case letters 
    # only if they are followed by _<an integer>qubits.qasm
    regex = re.compile(r'[a-z]+(?=_(\d+)qubits\.qasm)')

    # Search filename for the circuit name using the regular expression
    try:
        circuit_name = regex.search(filename).group(0)
    except AttributeError:
        circuit_name = None
    return circuit_name

def sort_files_by_circ_type(circuit_filepaths) -> {str: [str]}:
    # Ordering fastest to slowest to simulate
    sorted_files = {"ghz": [], "qft": [], "grover": []}
    circuit_filepaths.sort()
    for file in circuit_filepaths:
        try:
            circuit_type = find_circuit_name(file)
            sorted_files[circuit_type].append(file)
        except KeyError: # handling qelib1.inc, which isn't circuit
            pass
    return sorted_files

def get_circuit_filepaths():
    return ["circuits/" + filename for filename in os.listdir("circuits/")]

def sort_circ_files_by_type_and_speed(circuit_filepaths) -> [str]:
    """Ad hoc sorting by execution speed (based on my experience of how long they take to run)"""
    sorted_files = sort_files_by_circ_type(circuit_filepaths)
    print(sorted_files)
    sorted_files = list(sorted_files.values())
    return list(it.chain.from_iterable(sorted_files))

def sort_circuits_by_qubit_size(circuit_filepaths):
    qubits4circuit = sort_files_by_circ_type(circuit_filepaths)

    max_iterations = 100
    sorted_filepaths = []
    finished_circuit_types = []
    ii = 0
    while True:
        for circuit in qubits4circuit:
            try:
                sorted_filepaths.append(qubits4circuit[circuit][ii])
            except KeyError: # due to qelib1.inc not being circuit
                pass
            except IndexError:
                finished_circuit_types.append(circuit)   
            if len(finished_circuit_types) == len(qubits4circuit.keys()):
                return sorted_filepaths
        ii+=1
        if ii > max_iterations:
            break
