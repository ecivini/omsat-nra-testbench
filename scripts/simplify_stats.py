import sys

CSV_SEPARATOR = ","
NUMBER_OF_FIELDS = 25
TESTED_BENCHMARK_INDEX = 3
TIME_INDEX = 5
NANO_SUCCESSFUL_EXACT_SUB_INDEX = 19
NANO_SUCCESSFUL_CHECK_CROSSES_INDEX = 21
NANO_SUCCESSFUL_EPSILON_BOX_INDEX = 23
NANO_SAT_INDEX = 4

NANO_CSV_HEADER = "exact_sub,check_crosses,epsilon_box,benchmark\n"
ONLY_CSV_HEAHER = "benchmark\n"
BOTH_CSV_HEADER = "nano_time,vanilla_time,benchmark\n"

def process_vanilla_line(line):
    benchmark = line[TESTED_BENCHMARK_INDEX]
    problem_sat = line[NANO_SAT_INDEX]
    time = line[TIME_INDEX]

    if problem_sat != "sat":
        return None 
    
    return {
        "benchmark": benchmark,
        "time": time
    }

def process_nano_line(line):
    benchmark = line[TESTED_BENCHMARK_INDEX]
    succ_exact_sub = line[NANO_SUCCESSFUL_EXACT_SUB_INDEX]
    succ_check_crosses = line[NANO_SUCCESSFUL_CHECK_CROSSES_INDEX]
    succ_epsilon_box = line[NANO_SUCCESSFUL_EPSILON_BOX_INDEX]
    time = line[TIME_INDEX]
    
    at_least_one_nf = succ_exact_sub == "NF"
    at_least_one_nf |= succ_check_crosses == "NF"
    at_least_one_nf |= succ_epsilon_box == "NF"
    if at_least_one_nf:
        return None

    if int(succ_exact_sub) + int(succ_check_crosses) + int(succ_epsilon_box) == 0:
        return None

    return {
        "exact_sub": succ_exact_sub, 
        "check_crosses": succ_check_crosses,
        "epsilon_box": succ_epsilon_box,
        "benchmark": benchmark,
        "time": time
    }

def compute_solved_by_nano(nano_csv_path: str, vanilla_csv_path: str):
    nano_sat_problems, nano_times = process_smt_csv(nano_csv_path, True)
    
    if vanilla_csv_path:
        vanilla_sat_problems, vanilla_times = process_smt_csv(vanilla_csv_path, False)

        # Output problems solved by vanilla only
        vanilla_only_path = vanilla_csv_path[:-4] + "_only.csv"
        with open(vanilla_only_path, "w+") as vanilla_csv:
            vanilla_csv.write(ONLY_CSV_HEAHER)
            for problem in vanilla_sat_problems:
                if problem not in nano_sat_problems:
                    line = problem + "\n"
                    vanilla_csv.write(line)
        
        # Output problems solved by both solvers
        both_short_path = vanilla_csv_path[:-4] + "_both.csv"
        with open(both_short_path, "w+") as both_csv:
            both_csv.write(BOTH_CSV_HEADER)
            for problem in vanilla_sat_problems:
                if problem in nano_sat_problems:
                    line = nano_times[problem] + "," +\
                        vanilla_times[problem] + "," +\
                        problem + "\n"
                    both_csv.write(line)

        # Output problems solved by nano only
        nano_only_path = nano_csv_path[:-4] + "_only.csv"
        with open(nano_only_path, "w+") as only_csv:
            only_csv.write(ONLY_CSV_HEAHER)
            for problem in nano_sat_problems:
                if problem not in vanilla_sat_problems:
                    line = problem + "\n"
                    only_csv.write(line)

def process_smt_csv(input_csv_path: str, is_nano: bool):
    sat_problems = []
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
        for index, line in enumerate(input_csv):
            if index == 0:
                continue
        
            line_vals = line.split(",")
            if len(line_vals) != NUMBER_OF_FIELDS:
                print("Incorrect number of fields at line", index + 1)
                break

            benchmark = None
            solving_time = None
            if is_nano:
                stats = process_nano_line(line_vals)
                if not stats:
                    continue

                if int(stats["exact_sub"]) > 0:
                    solved_by_exact_sub += 1
                elif int(stats["check_crosses"]) > 0:
                    solved_by_check_crosses += 1
                elif int( stats["epsilon_box"]) > 0:
                    solved_by_epsilon_box += 1

                out_line = stats["exact_sub"] + "," + stats["check_crosses"] + "," + \
                    stats["epsilon_box"] + "," + stats["benchmark"] + "\n"
                output_csv.write(out_line)

                benchmark = stats["benchmark"]
                solving_time = stats["time"]
            else:
                stats = process_vanilla_line(line_vals)

                if not stats:
                    continue

                benchmark = stats["benchmark"]
                solving_time = stats["time"]
            
            sat_problems.append(benchmark)
            solving_times[benchmark] = solving_time

        if is_nano:
            print("Problems solved:", len(sat_problems))
            print("Problems solved via exact substitution: ", solved_by_exact_sub)
            print("Problems solved via check crosses:", solved_by_check_crosses)
            print("Problems solved via epsilon box:", solved_by_epsilon_box)

    return sat_problems, solving_times

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
        print(vanilla_csv_file_path.endswith(".csv"))
        print("Please provide a vanilla .csv file:", vanilla_csv_file_path)
        sys.exit(3)

    # Open file and read all lines
    if is_smt:
        compute_solved_by_nano(nano_csv_file_path, vanilla_csv_file_path)
    else:
        print("Script currently supports only SMT benchmarks.")

if __name__ == "__main__":
    main()