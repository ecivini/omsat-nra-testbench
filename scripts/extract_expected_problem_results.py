import json
import os
import re

BENCHMARKS_PATH = "benchmarks/"
RESULT_OUTPUT_PATH = "./data/expected_results.json"
LATEST_BENCHMARK = "./data/latest_benchmark.csv"

EXPECTED_RESULT_PATTERN = r"\(set-info\s+:status\s+(sat|unsat|unknown)\)"

BENCHMARK_PATH_INDEX = 3
BENCHMARK_RESULT_INDEX = 4

expected_results = {}
missing_or_unknown_result = []

if os.path.isfile(RESULT_OUTPUT_PATH):
    print("Loading previously computed expected results.")
    with open(RESULT_OUTPUT_PATH, "r") as output_file:
        expected_results = json.load(output_file)

for base_path, dirs, files in os.walk(BENCHMARKS_PATH):
    for file in files:
        if file in [".", ".."]:
            continue

        path = os.path.join(base_path, file)
        if expected_results.get(path) in ["unsat", "sat"]:
            continue

        with open(path, "r") as test_case:
            content = test_case.read()
            result = re.search(EXPECTED_RESULT_PATTERN, content)
            if not result:
                missing_or_unknown_result.append(file)
                print("No matches found for ", path)
                result = "unknown"
            else:
                result = result.group(1)
                if result == "unknown":
                    missing_or_unknown_result.append(file)

            expected_results[path] = result

if len(missing_or_unknown_result) > 0:
    results_from_benchmark = {}
    with open(LATEST_BENCHMARK, "r") as benchmark_file:
        for line in benchmark_file.readlines()[1:]:
            fields = line.split(",")
            
            path = fields[BENCHMARK_PATH_INDEX]
            result = fields[BENCHMARK_RESULT_INDEX]
            useful_result_found = result in ["unsat", "sat"]

            if useful_result_found and (
                path not in expected_results 
                or expected_results.get(path) == "unknown"
            ):
                print("Adding result from benchmark for ", path)
                expected_results[path] = result

with open(RESULT_OUTPUT_PATH, "w+") as output_file:
    json.dump(expected_results, output_file, indent=2)