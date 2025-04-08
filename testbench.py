from typing import Generator
import yaml
import os
import csv
from multiprocessing import Pool
import random

from evaluator.evaluator import Evaluator

###############################################################################

CONFIG_FILE = "config.yaml"

allowed_kinds = ["SMT", "OMT"]

smt_csv_header = ("kind,solver,timeout,test_case,result,time,model,"
        + "nano-total-calls,nano-complete-calls,nano-conflicts,nano-implications,"
        + "nano-explanations,nano-total-time-check,nano-total-time-opt,"
        + "nano-total-time-sat-check-exact-substitution,nano-total-time-sat-check-crosses,"
        + "nano-total-time-sat-check-epsilon-box,nano-successful-opt,nano-total-opt,"
        + "nano-successful-sat-check-exact-substitution,nano-total-sat-check-exact-substitution,"
        + "nano-successful-sat-check-crosses,nano-total-sat-check-crosses,"
        + "nano-successful-sat-check-epsilon-box,nano-total-sat-check-epsilon-box\n")

omt_csv_header = ("kind,solver,timeout,test_case,result,time,optimum,partial_lower,partial_upper,"
        + "nano-total-calls,nano-complete-calls,nano-conflicts,nano-implications,"
        + "nano-explanations,nano-total-time-check,nano-total-time-opt,"
        + "nano-total-time-sat-check-exact-substitution,nano-total-time-sat-check-crosses,"
        + "nano-total-time-sat-check-epsilon-box,nano-successful-opt,nano-total-opt,"
        + "nano-successful-sat-check-exact-substitution,nano-total-sat-check-exact-substitution,"
        + "nano-successful-sat-check-crosses,nano-total-sat-check-crosses,"
        + "nano-successful-sat-check-epsilon-box,nano-total-sat-check-epsilon-box\n")

error_csv_header = ("test_case,error\n")

###############################################################################

"""
Reads and loads the current configuration from the default configuration file.
"""
def get_config():
    config = None

    with open(CONFIG_FILE, "r") as config_file:
        config = yaml.safe_load(config_file)
        
    return config

###############################################################################
def check_ext(file_path: str, ext: str = ".smt2") -> bool:
    _, fext = os.path.splitext(file_path)
    return fext == ext


def get_test_cases(paths: list[str], computed: list[str]) -> Generator[str, None, None]:
    for path in paths:
        if os.path.isfile(path):
            if path in computed:
                print("[-] Skipping test case: already computed", path)
                continue

            if check_ext(path):
                yield path
            else:
                print("[-] Skipping test case: invalid file name", path)

        for root, _, files in os.walk(path):
            for file_path in files:
                test_case = os.path.join(root, file_path)

                if test_case in computed:
                    print("[-] Skipping test case: already computed", test_case)
                    continue

                if check_ext(test_case):
                    yield test_case
                else:
                    print("[-] Skipping test case: invalid file name", test_case)

def get_already_computed_benchmarks(base_path: str) -> list[str]:
    if not os.path.isfile(base_path):
        print("[+] No results file for solver found.")
        return []
    
    computed = []
    with open(base_path) as csvfile:
        benchmark = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in benchmark:
            cols = row[0].split(",")
            computed.append(cols[3])

    return computed[1:]

def solve_task(eval_data: dict) -> None:
    evaluator = Evaluator(
        eval_data["name"], 
        eval_data["cmd"],
        eval_data["args"],
        eval_data["timeout"],
        eval_data["kind"],
        eval_data["memory_limit"],
        eval_data["result_file"],
        eval_data["error_file"]
    )

    evaluator.add_task(eval_data["test_case"])
    evaluator.solve()

def main():
    config = get_config()
    solver_data = config["solver"]

    # Check kind
    if "kind" not in config or config["kind"] not in allowed_kinds:
        print("[-] Invalid kind")
        return

    # Create output file
    base_path = config["results"]
    result_file_path = base_path + solver_data["name"] + "_" + config["kind"] + ".csv"

    already_computed = get_already_computed_benchmarks(result_file_path)

    result_file = open(result_file_path, "a+")
    if len(already_computed) == 0:
        result_file.write(smt_csv_header if config["kind"] == "SMT" else omt_csv_header)
    result_file.close()

    # Create error file
    error_file_path = base_path + solver_data["name"] + "_" + config["kind"] + "_errors.csv"
    error_file = open(error_file_path, "a+")
    if len(already_computed) == 0:
        error_file.write(error_csv_header)
    error_file.close()

    processes = int(config["processes"])

    # Run tests
    evals_data = []
    for test_case in get_test_cases(config["benchmarks"], already_computed):
        eval_config = {
            "name": solver_data["name"], 
            "cmd": solver_data["cmd"],
            "args": solver_data["args"],
            "timeout": int(config["timeout"]),
            "kind": config["kind"],
            "memory_limit": config["memory"],
            "result_file": result_file_path,
            "error_file": error_file_path,
            "test_case": test_case
        }
        evals_data.append(eval_config)

    random.shuffle(evals_data)
    with Pool(processes=processes) as pool:
        for _ in pool.imap_unordered(solve_task, evals_data):
            continue
    
    # Close files
    result_file.close()
    error_file.close()

###############################################################################

if __name__ == "__main__":
    main()
