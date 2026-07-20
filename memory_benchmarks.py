"""Memory benchmarks"""

from pathlib import Path

from memory_profiler import memory_usage
import pandas as pd

from setup import (
    get_fidelity, 
    save, 
    get_circuit_filepaths,
    sort_circ_files_by_type_and_speed,
    sort_files_by_circ_type,
)

home_dir = str(Path.home())
# data_filepath = home_dir + "/research_data/data/dqc_simulator_benchmarks/mem_benchmark_DM.csv"
data_filepath = home_dir + "/research_data/data/dqc_simulator_benchmarks/mem_benchmark_STAB.csv"

if __name__ == "__main__":
    F_werner=0.99
    p_depolar_error_cnot=1e-03
    single_qubit_gate_error_prob=2e-05
    meas_error_prob=3e-03
    memory_depolar_rate=0.055

    # Choosing circuits to use (assuming the files are in the current working
    # directory)
    circuit_filepaths = get_circuit_filepaths()
    circuit_filepaths = sort_files_by_circ_type(circuit_filepaths)
    # Only Cliffords work for stabilser formalism
    circuit_filepaths = circuit_filepaths["ghz"]  
    # circuit_filepaths = sort_circ_files_by_type_and_speed(circuit_filepaths)
    # circuit_filepaths = [
    #      "circuits/ghz_9qubits.qasm",  # GHZ generation circuit
    #      "circuits/grover_5qubits.qasm",  # Grover algorithm
    #      "circuits/qft_5qubits.qasm",  # QFT
    # ]

    for circuit in circuit_filepaths:
        results = {"circuit_file": [], "max_memory_usage (MiB)": []}
        print("For circuit:", circuit)
        stuff2profile = (get_fidelity, (circuit,), {
                    "F_werner" : F_werner,
                    "p_depolar_error_cnot" : p_depolar_error_cnot,
                    "single_qubit_gate_error_prob" : single_qubit_gate_error_prob,
                    "meas_error_prob" : meas_error_prob,
                    "memory_depolar_rate" : memory_depolar_rate,
                    },
                )
        mem_usage = memory_usage(stuff2profile, include_children=True)
        max_usage = max(mem_usage)
        print("Max RAM used is: ", max_usage, "MiB")
        results["circuit_file"].append(circuit)
        results["max_memory_usage (MiB)"].append(max_usage)
        data = pd.DataFrame(results)
        save(data, data_filepath)



