import yaml
import os
import time
import threading

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

def main():
    config = get_config()
    solver_data = config["solver"]

    # Check kind
    if "kind" not in config or config["kind"] not in allowed_kinds:
        print("[-] Invalid kind")
        return

    # Create output file
    ts = int(time.time())
    base_path = config["results"]
    result_file_path = base_path + solver_data["name"] + "_" + str(ts) + ".csv"
    result_file = open(result_file_path, "w+")
    result_file.write(smt_csv_header if config["kind"] == "SMT" else omt_csv_header)

    # Create error file
    error_file_path = base_path + solver_data["name"] + "_" + str(ts) + "_errors.csv"
    error_file = open(error_file_path, "w+")
    error_file.write(error_csv_header)

    # Create evaluator instances
    evaluators = []
    processes = int(config["processes"])
    for _ in range(processes):
        evaluator = Evaluator(
            solver_data["name"], 
            solver_data["cmd"],
            solver_data["args"],
            int(config["timeout"]),
            config["kind"],
            result_file,
            error_file
        )
        evaluators.append(evaluator)

    # Run tests
    evaluator_id = 0
    for test_directory in config["benchmarks"]:
        # Check if it is effictively a directory
        if not os.path.isdir(test_directory):
            print("[-] Skipping test directory: invalid benchmark directory", test_directory)
            continue

        # Run all tests in the directory
        for test_case in os.listdir(test_directory):
            # Check if file is a test case
            if len(test_case) < 6 or test_case[-5:] != ".smt2":
                print("[-] Skipping test case: invalid file name", test_case)
                continue

            path = test_directory + "/" + test_case
            evaluator = evaluators[evaluator_id]
            evaluator.add_task(path)

            evaluator_id = (evaluator_id + 1) % processes

    # Start solving
    threads = []
    for i in range(processes):
        t = threading.Thread(target=evaluators[i].solve)
        threads.append(t)

    for i in range(processes):
        threads[i].start()

    # Wait for completion
    for i in range(processes):
        threads[i].join()
    
    # Close files
    result_file.close()
    error_file.close()

###############################################################################

if __name__ == "__main__":
    main()