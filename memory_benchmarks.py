"""Memory benchmarks"""

from pathlib import Path

from memory_profiler import memory_usage

from setup import take_experimental_shot

data_filepath = str(Path.home()) + "/research_data/data/dqc_simulator_benchmarks/mem_benchmark_test.csv"

F_werner=0.99
p_depolar_error_cnot=1e-03
single_qubit_gate_error_prob=2e-05
meas_error_prob=3e-03
memory_depolar_rate=0.055

# Choosing circuits to use (assuming the files are in the current working
# directory)
circuit_filepaths = [
    "ghz_5qubits.qasm",  # GHZ generation circuit
    "grover_5qubits.qasm",  # Grover algorithm
    "qft_5qubits.qasm",  # QFT
]

results = {}
for circuit in circuit_filepaths:
    stuff2profile = (take_experimental_shot, (circuit,), {
                "F_werner" : F_werner,
                "p_depolar_error_cnot" : p_depolar_error_cnot,
                "single_qubit_gate_error_prob" : single_qubit_gate_error_prob,
                "meas_error_prob" : meas_error_prob,
                "memory_depolar_rate" : memory_depolar_rate,
                },
            )
    mem_usage = memory_usage(stuff2profile)
    results[circuit] = [mem_usage]
print("Results are:", results)

