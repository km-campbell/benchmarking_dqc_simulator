from pathlib import Path

from matplotlib import pyplot as plt
import pandas as pd

from memory_benchmarks import data_filepath as data_filepath_mem
from setup import find_num_qubits, find_circuit_name
from time_benchmarks import data_filepath as data_filepath_time

home_dir = str(Path.home())
plot_dir = home_dir + "/research_plots/dqc_simulator_paper/benchmarks/"

def get_qubits_and_ydata(data, ydata_category: str):
    # ydata_category should match column name in dataframe

    circuit_files = list(data["circuit_file"])
    xydata = {"ghz": ([], []), "grover": ([], []), "qft": ([], [])}
    for file in circuit_files:
        circuit_type = find_circuit_name(file)

        num_qubits = find_num_qubits(file)
        xydata[circuit_type][0].append(num_qubits)

        # Add max memory usage
        idx = data.index[data["circuit_file"] == file]
        ydata = data.iloc[idx][ydata_category].item()
        xydata[circuit_type][1].append(ydata)
    return xydata


def plot_memory_benchmarks_DM(show=True, save=False):
    filepath = data_filepath_mem
    data = pd.read_csv(filepath)
    xydata = get_qubits_and_ydata(data, "max_memory_usage (MiB)")

    fig, ax = plt.subplots()
    for circuit, vals in xydata.items():
        num_qubits = vals[0]
        max_mem = vals[1]
        ax.plot(num_qubits, max_mem, label=circuit, linestyle='none', marker='x')
        # Should I plot logarithmically?

    ax.set_xlabel("# qubits")
    ax.set_ylabel("Max memory usage (MiB)")
    fig.legend()

    if save:
        savepath = plot_dir + "num_qubits_vs_mem.pdf"
        print("Saving plot to ", savepath)
        fig.savefig(savepath)

    if show:
        plt.show()



def plot_time_benchmarks_DM(show=True, save=False):
    filepath = data_filepath_time
    data = pd.read_csv(filepath)
    xydata = get_qubits_and_ydata(data, "average_time (s)")

    fig, ax = plt.subplots()
    for circuit, vals in xydata.items():
        num_qubits = vals[0]
        avg_time = vals[1]
        ax.plot(num_qubits, avg_time, label=circuit, linestyle='none', marker='x')

    ax.set_xlabel("# qubits")
    ax.set_ylabel("Runtime (s)")

    if save:
        savepath = plot_dir + "num_qubits_vs_runtime.pdf"
        print("saving plot to ", savepath)
        fig.savefig(savepath)
    
    if show:
        plt.show()

if __name__ == "__main__":
    plot_memory_benchmarks_DM(show=False, save=False)

    plot_time_benchmarks_DM(show=False, save=False)