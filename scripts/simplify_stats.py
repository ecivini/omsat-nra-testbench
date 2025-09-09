import sys
import json

import matplotlib.pyplot as plt

CSV_SEPARATOR = ","
TESTED_BENCHMARK_INDEX = 3
NANO_SAT_INDEX = 4
TIME_INDEX = 5

NANO_CSV_INDEX_MAP = {
    "SMT": {
        "successful_exact_sub": 19,
        "successful_check_crosses": 21,
        "successful_epsilon_box": 23
    }, 
    "OMT": {
        "successful_exact_sub": 21,
        "successful_check_crosses": 23,
        "successful_epsilon_box": 25
    }
}

OMT_PARAMS_NUM = 27
SMT_PARAMS_NUM = 25

EXPECTED_RESULTS_PATH = "./data/expected_results.json"

NANO_CSV_HEADER = "exact_sub,check_crosses,epsilon_box,benchmark\n"
ONLY_CSV_HEADER = "benchmark\n"
BOTH_CSV_HEADER = "nano_time,vanilla_time,benchmark\n"

def get_problems_from_expected_result(result: str) -> dict:
    expected_results = {}
    with open(EXPECTED_RESULTS_PATH, "r") as expected_results_file:
        expected_results = json.load(expected_results_file)

    problems = []
    for problem, expected_result in expected_results.items():
        if expected_result == result:
            problems.append(problem)

    return problems

def create_scatter_plot(data: dict):
    timeout = 1000
    linthresh = 1  # Linear region from -1 to 1 (positive side only in this case)

    # Create figure
    fig, ax = plt.subplots(figsize=(7, 7))

    # Scatter plot
    ax.scatter(data["no_error"]["x"], data["no_error"]["y"],
               color='darkgreen', edgecolors='black', label="No errors", s=25, zorder=4, alpha=0.2)
    ax.scatter(data["error_both"]["x"], data["error_both"]["y"],
               color='yellow', edgecolors='black', label="Both errored", s=40, zorder=5)

    # Reference line y = x
    ax.plot([1e-2, timeout], [1e-2, timeout], 'k--', label="y = x", zorder=2)

    # Timeout lines (dashed)
    ax.axvline(timeout, linestyle='--', color='gray')
    ax.axhline(timeout, linestyle='--', color='gray')

    # Set symlog scale
    ax.set_xscale('symlog', linthresh=linthresh)
    ax.set_yscale('symlog', linthresh=linthresh)
    ax.set_aspect('equal')

    # Set limits
    ax.set_xlim(left=1e-2, right=timeout * 1.1)
    ax.set_ylim(bottom=1e-2, top=timeout * 1.1)

    # Labels
    ax.set_xlabel('MathSAT + NaNo', fontsize=12)
    ax.set_ylabel('MathSAT Only', fontsize=12)

    # Grid
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)

    # Legend
    ax.legend()

    # Show plot
    plt.tight_layout()
    plt.show()

def process_vanilla_line(line):
    benchmark = line[TESTED_BENCHMARK_INDEX]
    problem_result = line[NANO_SAT_INDEX]
    time = line[TIME_INDEX]
    
    return {
        "benchmark": benchmark,
        "time": time,
        "result": problem_result
    }

def process_nano_line(line: list, problem_type: str):
    benchmark = line[TESTED_BENCHMARK_INDEX]
    succ_exact_sub = line[NANO_CSV_INDEX_MAP[problem_type]["successful_exact_sub"]]
    succ_check_crosses = line[NANO_CSV_INDEX_MAP[problem_type]["successful_check_crosses"]]
    succ_epsilon_box = line[NANO_CSV_INDEX_MAP[problem_type]["successful_epsilon_box"]]
    problem_result = line[NANO_SAT_INDEX]
    time = line[TIME_INDEX]
    
    # at_least_one_nf = succ_exact_sub == "NF"
    # at_least_one_nf |= succ_check_crosses == "NF"
    # at_least_one_nf |= succ_epsilon_box == "NF"
    # if at_least_one_nf:
    #     return None

    # if int(succ_exact_sub) + int(succ_check_crosses) + int(succ_epsilon_box) == 0:
    #     return None

    return {
        "exact_sub": succ_exact_sub, 
        "check_crosses": succ_check_crosses,
        "epsilon_box": succ_epsilon_box,
        "benchmark": benchmark,
        "result": problem_result,
        "time": time
    }

def compute_solved_by_nano(nano_csv_path: str, vanilla_csv_path: str):
    nano_data = process_csv(nano_csv_path, True)
    
    if vanilla_csv_path:
        vanilla_data = process_csv(vanilla_csv_path, False)

        # Output problems solved by vanilla only
        vanilla_only_path = vanilla_csv_path[:-4] + "_only.csv"
        with open(vanilla_only_path, "w+") as vanilla_csv:
            vanilla_csv.write(ONLY_CSV_HEADER)
            for problem in vanilla_data["sat"]:
                if problem not in nano_data["sat"]:
                    line = problem + "\n"
                    vanilla_csv.write(line)
        
        # Output problems solved by both solvers
        both_short_path = vanilla_csv_path[:-4] + "_both.csv"
        with open(both_short_path, "w+") as both_csv:
            both_csv.write(BOTH_CSV_HEADER)
            for problem in vanilla_data["sat"]:
                if problem in nano_data["sat"]:
                    line = nano_data["time"][problem] + "," +\
                        vanilla_data["time"][problem] + "," +\
                        problem + "\n"
                    both_csv.write(line)

        # Output problems solved by nano only
        nano_only_path = nano_csv_path[:-4] + "_only.csv"
        with open(nano_only_path, "w+") as only_csv:
            only_csv.write(ONLY_CSV_HEADER)
            for problem in nano_data["sat"]:
                if problem not in vanilla_data["sat"]:
                    line = problem + "\n"
                    only_csv.write(line)

        x_not_error_times = [] # NaNo
        y_not_error_times = [] # Vanilla

        x_nano_error_only_times = [] # NaNo
        y_nano_error_only_times = [] # Vanilla

        x_error_both_times = [] # NaNo
        y_error_both_times = [] # Vanilla

        problems_of_expected_result = get_problems_from_expected_result("unknown") # sat, unsat, unknown

        counter = 0
        all_problems = vanilla_data["sat"] + vanilla_data["timeout"] + vanilla_data["unsat"]
        problems_of_interest = list(set(problems_of_expected_result) & set(all_problems))
        for problem in problems_of_interest:
            if problem in nano_data["error"]:
                # x_nano_error_only_times.append(float(nano_data["time"][problem]))
                # y_nano_error_only_times.append(float(vanilla_data["time"][problem]))
                continue
            else:
                nano_time = float(nano_data["time"][problem])
                nano_time = 1000.0 if nano_time >= 1000.0 or problem in nano_data["timeout"] else nano_time

                vanilla_time = float(vanilla_data["time"][problem])
                vanilla_time = 1000.0 if vanilla_time >= 1000.0 or problem in vanilla_data["timeout"] else vanilla_time

                x_not_error_times.append(nano_time)
                y_not_error_times.append(vanilla_time)

                if nano_time < 1000.0 and vanilla_time >= 999.9:
                    counter += 1
                    #print(counter, vanilla_time, nano_time, problem)

        for problem in problems_of_interest:
            if problem in nano_data["error"]:
                x_error_both_times.append(float(nano_data["time"][problem]))
                y_error_both_times.append(float(vanilla_data["time"][problem]))
            else:
                #print("There should be no problems erroring only MathSAT vanilla and not NaNo.", problem)
                pass 
        data = {
            "no_error": {
                "x": x_not_error_times,
                "y": y_not_error_times
            },
            "error_only_nano": {
                "x": x_nano_error_only_times,
                "y": y_nano_error_only_times
            },
            "error_both": {
                "x": x_error_both_times,
                "y": y_error_both_times
            }
        }

        create_scatter_plot(data)

def process_csv(input_csv_path: str, is_nano: bool):
    sat_problems = []
    unsat_problems = []
    timeout_problems = []
    error_problem = []
    solving_times = {}

    with open(input_csv_path, "r") as input_csv:
        output_path = input_csv_path[:-4] + "_short.csv"

        output_csv = None
        if is_nano:
            output_csv = open(output_path, "w+")
            output_csv.write(NANO_CSV_HEADER)

        solved_by_exact_sub = 0
        solved_by_check_crosses = 0
        solved_by_epsilon_box = 0
        problem_type = None
        expected_number_of_fields = 0
        for index, line in enumerate(input_csv):
            if index == 0:
                line_vals_num = len(line.split(","))
                if line_vals_num not in [OMT_PARAMS_NUM, SMT_PARAMS_NUM]:
                    break

                if line_vals_num == OMT_PARAMS_NUM:
                    problem_type = "OMT"
                    expected_number_of_fields = OMT_PARAMS_NUM
                elif line_vals_num == SMT_PARAMS_NUM:
                    problem_type = "SMT"
                    expected_number_of_fields = SMT_PARAMS_NUM
                continue
        
            line_vals = line.split(",")
            if len(line_vals) != expected_number_of_fields:
                print("Incorrect number of fields at line", index + 1)
                break

            benchmark = None
            solving_time = None
            if is_nano:
                stats = process_nano_line(line_vals, problem_type)
                if stats["result"] == "sat": 
                    if stats["exact_sub"] != "NF" and int(stats["exact_sub"]) > 0:
                        solved_by_exact_sub += 1
                    elif stats["check_crosses"] != "NF" and int(stats["check_crosses"]) > 0:
                        solved_by_check_crosses += 1
                    elif stats["epsilon_box"] != "NF" and int( stats["epsilon_box"]) > 0:
                        solved_by_epsilon_box += 1

                    out_line = stats["exact_sub"] + "," + stats["check_crosses"] + "," + \
                        stats["epsilon_box"] + "," + stats["benchmark"] + "\n"
                    output_csv.write(out_line)

                benchmark = stats["benchmark"]
                solving_time = stats["time"]
            else:
                stats = process_vanilla_line(line_vals)

                benchmark = stats["benchmark"]
                solving_time = stats["time"]
            
            if stats["result"] == "sat":
                sat_problems.append(benchmark)
            elif stats["result"] == "unsat":
                unsat_problems.append(benchmark)
            elif stats["result"] in ["timeout", "forced_timeout", "unhandled"]:
                timeout_problems.append(benchmark)
            else:
                error_problem.append(benchmark)

            solving_times[benchmark] = solving_time

        if is_nano:
            print("Problems solved:", len(sat_problems))
            print("Problems solved via exact substitution: ", solved_by_exact_sub)
            print("Problems solved via check crosses:", solved_by_check_crosses)
            print("Problems solved via epsilon box:", solved_by_epsilon_box)
            print("Problems solved by NaNo:", solved_by_exact_sub + solved_by_check_crosses + solved_by_epsilon_box)

    return {
        "sat": sat_problems, 
        "unsat": unsat_problems, 
        "timeout": timeout_problems, 
        "error": error_problem, 
        "time": solving_times
    }

def main():
    # Check cli args
    if len(sys.argv) not in [3, 4]:
        print("Usage: python3 simplify_stats.py <smt / omt> <path to nano .csv file> <optional path to vanilla .csv file>")
        sys.exit(1)
    
    is_smt = sys.argv[1].strip().lower() == "smt"
    nano_csv_file_path = sys.argv[2]
    vanilla_csv_file_path = None

    if len(sys.argv) == 4:
        vanilla_csv_file_path = sys.argv[3]

    if not nano_csv_file_path.endswith(".csv"):
        print("Please provide a nano .csv file:", nano_csv_file_path)
        sys.exit(2)

    if vanilla_csv_file_path and not vanilla_csv_file_path.endswith(".csv"):
        print("Please provide a vanilla .csv file:", vanilla_csv_file_path)
        sys.exit(3)

    # Open file and read all lines
    if is_smt:
        compute_solved_by_nano(nano_csv_file_path, vanilla_csv_file_path)
    else:
        print("Script currently supports only SMT benchmarks.")

if __name__ == "__main__":
    main()