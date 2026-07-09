from matplotlib import pyplot as plt
import pandas as pd

from memory_benchmarks import data_filepath as data_filepath_mem
from setup import find_num_qubits, find_circuit_name
from time_benchmarks import data_filepath as data_filepath_time


def plot_memory_benchmarks_DM():
    filepath = data_filepath_mem
    data = pd.read_csv(filepath)
    fig, ax = plt.subplots()

    # TO DO: use find_num_qubits and find_circuit_name to iterate over the differnet circuit types
    # and plot num qubits for the number of circuit types
    num_qubits = [find_num_qubits(circuit) for circuit in data["circuit_file"]]
    ax.plot(num_qubits, data["max_memory_usage (MiB)"])
    

def plot_time_benchmarks_DM():
    pass


if __name__ == "__main__":
    plot_memory_benchmarks_DM()

    # plot_time_benchmarks_DM()