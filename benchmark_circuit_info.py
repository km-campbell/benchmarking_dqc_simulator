from pathlib import Path

import pandas as pd
from dqc_simulator.qlib.remote_gate_scheme_info import get_scheme_info
from dqc_simulator.software.compiler_preprocessing import (
    preprocess_qasm_to_compilable_monolithic as preprocess,
)
from dqc_simulator.software.partitioner import (
    first_come_first_served_qubits_to_qpus as allocate,
    partition_gate_tuples as partition,
)
from setup import (
    get_circuit_filepaths,
    sort_circ_files_by_type_and_speed,
    setup_hardware, 
    save
    )


class CircuitInfo():
    """The info associated with the circuits to be benchmarked."""
    def __init__(self, dqc):
        self.scheme = "cat"
        self.scheme_info = get_scheme_info()[self.scheme]
        self.dqc = dqc
        info = []
        info = self.populate_info(info)
        self.dataframe = pd.DataFrame(info)


    def parse_gate_tuple(self, gate: tuple, circuit_info:dict):
        if not isinstance(gate[0], tuple) and gate[0].name == "initialisation_op":
                    pass
        elif len(gate) == 3: # if single-qubit gate
            circuit_info["num_single_qubit_gates"]+=1
        elif gate[0].name == "cnot_gate":
            if gate[-1] == self.scheme:
                for resource in circuit_info:
                    circuit_info[resource]+=self.scheme_info[resource]
            else: # if CNOT is local
                circuit_info["num_cnots"]+=1
        return circuit_info

    def populate_info(self, info):

        # Choosing circuits to use (assuming the files are in the current working
        # directory)
        circuit_filepaths = get_circuit_filepaths()
        circuit_filepaths = sort_circ_files_by_type_and_speed(circuit_filepaths)
        # circuit_filepaths = [
        #  "circuits/ghz_5qubits.qasm",  # GHZ generation circuit
        #  "circuits/grover_5qubits.qasm",  # Grover algorithm
        #  "circuits/qft_5qubits.qasm",  # QFT
        # ]
     
        default_circuit_info = {
        "num_epr_pairs": 0,
        "num_cnots": 0,
        "num_single_qubit_gates": 0,
        "num_measurements": 0,
        # "num_classical_comms": 0,
        }

        circuit_info = dict(default_circuit_info)
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
                circuit_info = self.parse_gate_tuple(gate, circuit_info)

            circuit_info["circuit"] = circuit
            info.append(circuit_info)
            # Reset circuit_info to default for next iteration
            circuit_info = dict(default_circuit_info)
        return info



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
    df = circuit_info.dataframe
    
    # Saving (will overwrite any file with the same name and path)
    home_dir = str(Path.home())
    filepath = (home_dir + 
                "/research_data/data/dqc_simulator_benchmarks/benchmark_circuit_info.csv")
    df.to_csv(filepath)
    

    