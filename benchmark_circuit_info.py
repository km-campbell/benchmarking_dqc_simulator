from pathlib import Path

import pandas
from dqc_simulator.qlib.remote_gate_scheme_info import get_scheme_info
from dqc_simulator.software.compiler_preprocessing import (
    preprocess_qasm_to_compilable_monolithic as preprocess,
)
from dqc_simulator.software.partitioner import (
    first_come_first_served_qubits_to_qpus as allocate,
    partition_gate_tuples as partition,
)
from setup import get_circuit_filepaths, sort_circ_files_by_type_and_speed, setup_hardware

home_dir = str(Path.home())

class CircuitInfo():
    """The info associated with the circuits to be benchmarked."""
    def __init__(self, dqc):
        self.info = {
        "num_epr_pairs": 0,
        "num_cnots": 0,
        "num_single_qubit_gates": 0,
        "num_measurements": 0,
        # "num_classical_comms": 0,
        }
        self.scheme = "cat"
        self.scheme_info = get_scheme_info()[self.scheme]
        self.dqc = dqc
        self.populate_circuit_info()

    def parse_gate_tuple(self, gate: tuple):
        if not isinstance(gate[0], tuple) and gate[0].name == "initialisation_op":
                    pass
        elif len(gate) == 3: # if single-qubit gate
            self.info["num_single_qubit_gates"]+=1
        elif gate[0].name == "cnot_gate":
            if gate[-1] == self.scheme:
                for resource in self.info:
                    self.info[resource]+=self.scheme_info[resource]
            else: # if CNOT is local
                self.info["num_cnots"]+=1

    def populate_circuit_info(self):

        # Choosing circuits to use (assuming the files are in the current working
        # directory)
        # circuit_filepaths = get_circuit_filepaths()
        # circuit_filepaths = sort_circ_files_by_type_and_speed(circuit_filepaths)
        circuit_filepaths = [
         "circuits/ghz_5qubits.qasm",  # GHZ generation circuit
         "circuits/grover_5qubits.qasm",  # Grover algorithm
         "circuits/qft_5qubits.qasm",  # QFT
        ]
     
        for circuit in circuit_filepaths:
            monolithic_circuit = preprocess(circuit, include_path="./circuits/")
            monolithic_circuit = monolithic_circuit.ops  # gate_tuples

            # Determine allocation of processing qubits to QPUs
            old_to_new_lookup, proc_qubit_allocation4each_qpu = allocate(
                monolithic_circuit, list(self.dqc.nodes.values())
            )

            # Partition according to the previously defined qubit allocation
            partitioned_gate_tuples = partition(
                monolithic_circuit,
                self.dqc,  # defined earlier in tutorial
                self.scheme,
                old_to_new_lookup,
                proc_qubit_allocation4each_qpu,
            ) 

            for gate in partitioned_gate_tuples:
                self.parse_gate_tuple(gate)

            # TO DO: right now circuit info is amalgamating all circuits. I want to create a new entry for each circuit



        



if __name__ == "__main__":
    # param choices should not matter for this
    dqc = setup_hardware(
        F_werner=1,
        p_depolar_error_cnot=0,
        single_qubit_gate_error_prob=0,
        meas_error_prob=0,
        memory_depolar_rate=0,
    )
    circuit_info = CircuitInfo(dqc)
    print(circuit_info.info)