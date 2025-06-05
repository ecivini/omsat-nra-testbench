from copy import deepcopy
import sys

BENCHMARK_RESULT_INDEX = 4

if len(sys.argv) != 2:
    print("Usage: python3 remove_errors_from_benchmark_result.py <benchmark result path>")
    sys.exit(0)

benchmark_path = sys.argv[1]

lines = []
with open(benchmark_path, "r") as benchmark_file:
    lines = benchmark_file.readlines()

for line in deepcopy(lines[1:]):
    fields = line.split(",")
    result = fields[BENCHMARK_RESULT_INDEX]

    if result == "error":
        lines.remove(line)

with open(benchmark_path, "w") as benchmark_file:
    content = "".join(lines)
    benchmark_file.write(content)