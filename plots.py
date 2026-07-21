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

def get_circuit_info():
    filepath = (home_dir + 
                "/research_data/data/dqc_simulator_benchmarks/benchmark_circuit_info.csv")
    return pd.read_csv(filepath)

def get_num_gates_and_ydata(data, ydata_category: str):
    circuit_info = get_circuit_info()

    circuit_files = list(data["circuit_file"])
    xydata = {"ghz": ([], []), "grover": ([], []), "qft": ([], [])}
    for file in circuit_files:
        circuit_type = find_circuit_name(file)

        file_info = circuit_info[circuit_info["circuit"] == file]
        num_gates = file_info["num_cnots"] + file_info["num_single_qubit_gates"]
        xydata[circuit_type][0].append(num_gates)

        # Add max memory usage
        idx = data.index[data["circuit_file"] == file]
        ydata = data.iloc[idx][ydata_category].item()
        xydata[circuit_type][1].append(ydata)
    return xydata





def plot_memory_benchmarks_wrt_num_qubits(show=True, save=False):
    filepath = data_filepath_mem
    ydata_category = "max_memory_usage (MiB)"
    data_DM = pd.read_csv(filepath)
    xydata_DM = get_qubits_and_ydata(data_DM, ydata_category)
    data_STAB = pd.read_csv(filepath.replace("DM", "STAB"))
    xydata_STAB = get_qubits_and_ydata(data_STAB, ydata_category)

    fig, ax = plt.subplots()

    # For DM
    for circuit, vals in xydata_DM.items():
        num_qubits = vals[0]
        max_mem = vals[1]
        ax.plot(num_qubits, max_mem, label=circuit, marker='x')

    # For stabilisers
    vals = xydata_STAB["ghz"]
    num_qubits = vals[0]
    max_mem = vals[1]
    ax.plot(num_qubits, max_mem, label="ghz (STAB)", marker='x', 
            linestyle="dashed")

    ax.set_xlabel("# qubits")
    ax.set_ylabel("Max memory usage (MiB)")
    fig.legend(loc="upper left", bbox_to_anchor=(0.2, 0.8))

    if save:
        savepath = plot_dir + "num_qubits_vs_mem.pdf"
        print("Saving plot to ", savepath)
        fig.savefig(savepath)

    if show:
        plt.show()


def plot_memory_benchmarks_DM_wrt_num_gates(show=True, save=False):
    data_DM = pd.read_csv(data_filepath_mem)
    ydata_category = "max_memory_usage (MiB)"
    xydata_DM = get_num_gates_and_ydata(data_DM, ydata_category)
    data_STAB = pd.read_csv(data_filepath_mem.replace("DM", "STAB"))
    xydata_STAB = get_num_gates_and_ydata(data_STAB, ydata_category)

    fig, ax = plt.subplots()
    # For DM
    for circuit, vals in xydata_DM.items():
        num_gates = vals[0]
        max_mem = vals[1]
        ax.plot(num_gates, max_mem, label=circuit, marker="x")
    
    # For stabilisers
    vals = xydata_STAB["ghz"]
    num_qubits = vals[0]
    max_mem = vals[1]
    ax.plot(num_qubits, max_mem, label="ghz (STAB)", marker='x', 
            linestyle="dashed")

    ax.set_xscale("log")
    # ax.set_yscale("log")
    ax.set_xlabel("# gates")
    ax.set_ylabel("Max memory usage (MiB)")
    fig.legend(loc="upper left", bbox_to_anchor=(0.2, 0.8))

    if save:
        savepath = plot_dir + "num_gates_vs_mem.pdf"
        print("Saving plot to ", savepath)
        fig.savefig(savepath)

    if show:
        plt.show()



def plot_time_benchmarks_DM_wrt_num_qubits(show=True, save=False):
    filepath = data_filepath_time
    ydata_category = "average_time (s)"
    data_DM = pd.read_csv(filepath)
    xydata_DM = get_qubits_and_ydata(data_DM, ydata_category)
    data_STAB = pd.read_csv(filepath.replace("DM", "STAB"))
    xydata_STAB = get_qubits_and_ydata(data_STAB, ydata_category)

    fig, ax = plt.subplots()
    # For DMs
    for circuit, vals in xydata_DM.items():
        num_qubits = vals[0]
        avg_time = vals[1]
        ax.plot(num_qubits, avg_time, label=circuit, marker='x')

    # For stabilisers
    vals = xydata_STAB["ghz"]
    num_qubits = vals[0]
    max_runtime = vals[1]
    ax.plot(num_qubits, max_runtime, label="ghz (STAB)", marker='x', 
            linestyle="dashed")

    ax.set_yscale("log")
    ax.set_xlabel("# qubits")
    ax.set_ylabel("Runtime (s)")
    fig.legend(loc="upper left", bbox_to_anchor=(0.2, 0.8))

    if save:
        savepath = plot_dir + "num_qubits_vs_runtime.pdf"
        print("saving plot to ", savepath)
        fig.savefig(savepath)
    
    if show:
        plt.show()

def plot_time_benchmarks_DM_wrt_num_gates(show=True, save=False):
    data_DM = pd.read_csv(data_filepath_time)
    xydata_DM = get_num_gates_and_ydata(data_DM, "average_time (s)")
    data_STAB = pd.read_csv(data_filepath_time.replace("DM", "STAB"))
    xydata_STAB = get_num_gates_and_ydata(data_STAB, "average_time (s)")

    fig, ax = plt.subplots()
    for circuit, vals in xydata_DM.items():
        num_gates = vals[0]
        max_mem = vals[1]
        ax.plot(num_gates, max_mem, label=circuit, marker="x")

    # For stabilisers
    vals = xydata_STAB["ghz"]
    num_qubits = vals[0]
    max_runtime = vals[1]
    ax.plot(num_qubits, max_runtime, label="ghz (STAB)", marker='x', 
            linestyle="dashed")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("# gates")
    ax.set_ylabel("Runtime (s)")
    fig.legend(loc="upper left", bbox_to_anchor=(0.2, 0.8))

    if save:
        savepath = plot_dir + "num_gates_vs_runtime.pdf"
        print("Saving plot to ", savepath)
        fig.savefig(savepath)

    if show:
        plt.show()

if __name__ == "__main__":
    plot_memory_benchmarks_wrt_num_qubits(show=False, save=True)

    plot_time_benchmarks_DM_wrt_num_qubits(show=False, save=True)

    plot_memory_benchmarks_DM_wrt_num_gates(show=False, save=True)

    plot_time_benchmarks_DM_wrt_num_gates(show=False, save=True)