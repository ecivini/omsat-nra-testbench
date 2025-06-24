import matplotlib.pyplot as plt
import numpy as np

import sys
import json
import os

EXPECTED_RESULTS_PATH = "./data/expected_results.json"

NANO_TIMEOUT = 1000
TIMEOUT_BUFFER = 15

BENCHMARK_PATH_INDEX = 3
BENCHMARK_RESULT_INDEX = 4
BENCHMARK_TIME_INDEX = 5

CACTUS_EXPECTED_SAT_LABEL = "Number of SAT Problems Solved"
CACTUS_EXPECTED_UNSAT_LABEL = "Number of UNSAT Problems Solved"
CACTUS_EXPECTED_UNKNOWN_LABEL = "Number of UNKOWN Problems Solved"

def read_expected_results() -> dict:
    """
    Reads and extracts the expected results from EXPECTED_RESULTS_PATH. It returns
    a dictionary in the form <benchmark path> -> sat/unsat/unknown.
    """
    with open(EXPECTED_RESULTS_PATH, "r") as expected_results_file:
        return json.load(expected_results_file)

def extract_data_from_benchmark(benchmark_path: str, expected_results: dict) -> dict:
    """
    This function assumes that expected_results contains up to date data.
    Before running this script, make sure to update EXPECTED_RESULTS_PATH file
    by running the extract_expected_problem_results.py with the latest benchmark.
    """

    data = {}

    sat_times = []
    unsat_times = []
    unknown_times = []

    with open(benchmark_path, "r") as benchmark:
        for line in benchmark.readlines()[1:]:
            fields = line.split(",")
            path = fields[BENCHMARK_PATH_INDEX]
            result = fields[BENCHMARK_RESULT_INDEX]
            time = float(fields[BENCHMARK_TIME_INDEX])

            # Ignore errors
            if result == "error":
                continue

            # Uniformize timeout results
            if result == "forced_timeout":
                result = "timeout"

            if expected_results[path] == "sat" and result in ["sat", "timeout"]:
                sat_times.append(time)

            elif expected_results[path] == "unsat" and result in ["unsat", "timeout"]:
                unsat_times.append(time)

            else:
                unknown_times.append(time)

            data[path] = {
                "time": time,
                "result": result
            }

        sat_times.sort()
        unsat_times.sort()
        unknown_times.sort()

        return {
            "problems": data,
            "sat_times": sat_times,
            "unsat_times": unsat_times,
            "unknown_times": unknown_times
        }

def create_and_save_plot(nano_times: list, vanilla_times: list, save_path: str, label: str):
    cutoff = NANO_TIMEOUT + NANO_TIMEOUT
    nano = [t for t in nano_times if t <= cutoff]
    vanilla = [t for t in vanilla_times if t <= cutoff]
    virtual_best = [min(t_nano, t_vanilla) for t_nano, t_vanilla in zip(nano, vanilla)]

    x1 = np.arange(1, len(nano) + 1)
    x2 = np.arange(1, len(vanilla) + 1)
    x3 = np.arange(1, len(virtual_best) + 1)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(x1, nano, label="NaNo", marker='o', markersize=2)
    plt.plot(x2, vanilla, label="Vanilla", marker='^', markersize=2)
    plt.plot(x3, virtual_best, label="Virtual Best", marker='s', markersize=1)

    plt.xlabel(label)
    plt.ylabel("Time (s)")
    plt.title("Solvers comparison")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)

def generate_cactus_plots(nano_benchmark_path: str, vanilla_benchmark_path: str, plots_path: str):
    expected_results = read_expected_results()
    nano_data = extract_data_from_benchmark(nano_benchmark_path, expected_results)
    vanilla_data = extract_data_from_benchmark(vanilla_benchmark_path, expected_results)

    # SAT plot
    sat_output_path = os.path.join(plots_path, "cactus_sat.png")
    create_and_save_plot(nano_data["sat_times"], vanilla_data["sat_times"], sat_output_path, CACTUS_EXPECTED_SAT_LABEL)

    # UNSAT plot
    unsat_output_path = os.path.join(plots_path, "cactus_unsat.png")
    create_and_save_plot(nano_data["unsat_times"], vanilla_data["unsat_times"], unsat_output_path, CACTUS_EXPECTED_UNSAT_LABEL)

    # UNKNOWN plot
    unknown_output_path = os.path.join(plots_path, "cactus_unknown.png")
    create_and_save_plot(nano_data["unknown_times"], vanilla_data["unknown_times"], unknown_output_path, CACTUS_EXPECTED_UNKNOWN_LABEL)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 generate_cactus_plots.py <nano benchmark path> <vanilla benchmark path> <plots output path>")
        sys.exit(0)

    nano_benchmark_path = sys.argv[1]
    vanilla_benchmark_path = sys.argv[2]
    plots_output_path = sys.argv[3]
    generate_cactus_plots(nano_benchmark_path, vanilla_benchmark_path, plots_output_path)