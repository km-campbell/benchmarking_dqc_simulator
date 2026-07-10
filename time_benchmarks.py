"""Benchmark time"""

import os
from pathlib import Path
from timeit import timeit

import pandas as pd

# get_fidelity is needed in the following but will show up in linter as unused because
# it appears as a string in timeit. Nonetheless, it will be fed to timeit using the 
# globals keyword argument and must not be removed
from setup import (
    get_fidelity, # NEED this despite what linter says (see above)
    save,
    get_circuit_filepaths,
    sort_circ_files_by_type_and_speed,
    find_circuit_name,
    find_num_qubits,
)

# Defining where to save the data
data_filepath = (str(Path.home()) +
                 "/research_data/data/dqc_simulator_benchmarks/time_benchmark_DM.csv"
                  )

if __name__ == "__main__":
    # Benchmarking time
    F_werner=0.99
    p_depolar_error_cnot=1e-03
    single_qubit_gate_error_prob=2e-05
    meas_error_prob=3e-03
    memory_depolar_rate=0.055
    num_iterations = 5
    # Choosing circuits to use (assuming the files are in the current working
    # directory)
    circuit_filepaths = get_circuit_filepaths()
    circuit_filepaths = sort_circ_files_by_type_and_speed(circuit_filepaths)
    # circuit_filepaths = [
    #     "circuits/ghz_5qubits.qasm",  # GHZ generation circuit
    #     "circuits/grover_5qubits.qasm",  # Grover algorithm
    #     "circuits/qft_5qubits.qasm",  # QFT
    # ]


    for circuit in circuit_filepaths:
        print("For circuit:", circuit)
        results = {
            "circuit_file": [], 
            "total_time (s)": [], 
            "num_iterations": [], 
            "average_time (s)": []
        }
        program_str = (
            "get_fidelity("
            "circuit,"
            f"F_werner={F_werner},"
            f"p_depolar_error_cnot={p_depolar_error_cnot},"
            f"single_qubit_gate_error_prob={single_qubit_gate_error_prob},"
            f"meas_error_prob={meas_error_prob},"
            f"memory_depolar_rate={memory_depolar_rate},"
            ")"
        )

        # Handling very slow Grover circuits
        if find_circuit_name(circuit) == "grover" and find_num_qubits(circuit) > 4:
            num_iterations = 1
        if find_circuit_name(circuit) == "grover" and find_num_qubits(circuit) > 8:
            break # 9 qubits takes a very long time. I have cut off at around 7 hours.

        # Running program_str `num_iterations` times and saving average
        total_time = timeit(program_str, number=num_iterations, globals=globals())
        average_time = total_time/num_iterations
        results["circuit_filename"].append(circuit)
        results["total_time (s)"].append(total_time)
        results["num_iterations"].append(num_iterations)
        results["average_time (s)"].append(average_time)
        print("Average time is ", average_time)
        data = pd.DataFrame(results)
        save(data, data_filepath)
