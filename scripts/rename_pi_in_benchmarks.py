import os

BENCHMARKS_PATH = "benchmarks/"
PI_DECLARATION = "(declare-fun pi () Real)"
PI_REPLACEMENT = "pi_renamed"

PI_REPLACEMENT_MAP = {
    " pi)": " " + PI_REPLACEMENT + ")",
    " pi ": " " + PI_REPLACEMENT + " ",
    "(pi ": "(" + PI_REPLACEMENT + " ",
}

for base_path, dirs, files in os.walk(BENCHMARKS_PATH):
    for file in files:
        if file in [".", ".."]:
            continue

        benchmark = None

        full_path = os.path.join(base_path, file)
        with open(full_path, "r") as benchmark_file:
            benchmark = benchmark_file.read()
            if not PI_DECLARATION in benchmark:
                continue

            print("Updating", full_path)

            for original, replacement in PI_REPLACEMENT_MAP.items():
                benchmark = benchmark.replace(original, replacement)

        with open(full_path, "w") as benchmark_file:
            benchmark_file.write(benchmark)