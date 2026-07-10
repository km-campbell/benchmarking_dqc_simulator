from matplotlib import pyplot as plt
import pandas as pd

from memory_benchmarks import data_filepath as data_filepath_mem
from setup import find_num_qubits, find_circuit_name
from time_benchmarks import data_filepath as data_filepath_time

def get_qubits_and_memory(data):
    circuit_files = list(data["circuit_file"])
    qubits4circuit = {"ghz": ([], []), "grover": ([], []), "qft": ([], [])}
    for file in circuit_files:
        circuit_type = find_circuit_name(file)

        num_qubits = find_num_qubits(file)
        qubits4circuit[circuit_type][0].append(num_qubits)

        # Add max memory usage
        idx = data.index[data["circuit_file"] == file]
        max_memory = data.iloc[idx]["max_memory_usage (MiB)"].item()
        qubits4circuit[circuit_type][1].append(max_memory)
    return qubits4circuit


def plot_memory_benchmarks_DM(show=True):
    filepath = data_filepath_mem
    data = pd.read_csv(filepath)
    qubits4circuit = get_qubits_and_memory(data)

    fig, ax = plt.subplots()
    for circuit, vals in qubits4circuit.items():
        num_qubits = vals[0]
        max_mem = vals[1]
        ax.plot(num_qubits, max_mem, label=circuit, linestyle='none', marker='x')
        # Should I plot logarithmically?

    ax.set_xlabel("# qubits")
    ax.set_ylabel("Max memory usage (MiB)")
    fig.legend()

    plt.show()


def plot_time_benchmarks_DM():
    pass


if __name__ == "__main__":
    plot_memory_benchmarks_DM(show=True)

    # plot_time_benchmarks_DM()