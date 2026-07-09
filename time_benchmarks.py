"""Benchmark time"""

from pathlib import Path
from timeit import timeit

import pandas as pd

from setup import get_fidelity

# Defining where to save the data
data_filepath = str(Path.home()) + "/research_data/data/dqc_simulator_benchmarks/time_benchmark_test.csv"

# Benchmarking time
F_werner=0.99
p_depolar_error_cnot=1e-03
single_qubit_gate_error_prob=2e-05
meas_error_prob=3e-03
memory_depolar_rate=0.055
num_iterations = 5
# Choosing circuits to use (assuming the files are in the current working
# directory)
circuit_filepaths = [
    "circuits/ghz_5qubits.qasm",  # GHZ generation circuit
    "circuits/grover_5qubits.qasm",  # Grover algorithm
    "circuits/qft_5qubits.qasm",  # QFT
]

results = {}
for circuit in circuit_filepaths:
    program_str = (
        "take_experimental_shot("
        "circuit,"
        f"F_werner={F_werner},"
        f"p_depolar_error_cnot={p_depolar_error_cnot},"
        f"single_qubit_gate_error_prob={single_qubit_gate_error_prob},"
        f"meas_error_prob={meas_error_prob},"
        f"memory_depolar_rate={memory_depolar_rate},"
        ")"
    )


    # Running program_str `num_iterations` times and saving average
    total_time = timeit(program_str, number=num_iterations, globals=globals())
    results[circuit] = [total_time/num_iterations]
print("results are ", results)