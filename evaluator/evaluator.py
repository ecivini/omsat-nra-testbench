import subprocess
import time
import re

class Evaluator:

    def __init__(self, name: str, cmd: str, params: str, timeout: int, res_file):
        self.name = name 
        self.cmd = cmd
        self.params = params
        self.timeout = timeout
        self.res_file = res_file
        self.tasks = []
        self.next_id = 0

    def add_task(self, test_case: str):
        self.tasks.append(test_case)

    def solve(self):
        for i in range(self.next_id, len(self.tasks)):
            result = "timeout"
            solve_time = 0
            optimum = 0.0
            try:
                command = self.cmd
                if self.params != "":
                    command += " " + self.params
                command += " " + self.tasks[i]

                print("[+] Running " + command)
                command = command.split(" ")
                start_ts = time.time()
                process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    timeout=self.timeout + 5
                )
                end_ts = time.time()

                err = process.stderr.decode()
                out = process.stdout.decode()

                print(out)
                if len(err) > 0:
                    print(f'[-] Error: {err=}')
                    result="errored"
                else:
                    if "unsat" in out:
                        result = "unsat"
                    else:
                        result = "sat"
                        # TODO: Add support for multiple objectives
                        objs = self.parse_objectives(out)
                        for value in objs.values():
                            optimum = value
                
                solve_time = end_ts - start_ts
            except Exception as e:
                if "timed out" in str(e):
                    print("[-] Solver timed out with test case " + self.tasks[i])
                else:
                    # TODO: Check correctness
                    result = "unsat"
                    print("[-] Solver exception:", e)

            # TODO: Avoid race conditions when updating result file
            file_line = self.name + ","
            file_line += str(self.timeout) + ","
            file_line += self.tasks[i] + ","
            file_line += result + ","
            file_line += str(optimum) + ","
            file_line += str(round(solve_time, 4))
            file_line += "\n"

            self.res_file.write(file_line)

    def parse_objectives(self, result):
        variables = {}

        # First, find the objectives part
        objective_pattern = r'\(objectives\s*\((.*?)\)\)'  # Matches everything inside "(objectives ...)"
        objectives_match = re.search(objective_pattern, result, re.DOTALL)

        if objectives_match:
            # Extract the variables inside the objectives
            objectives_str = objectives_match.group(1).strip()
            # Look for variable definitions like (x 5)
            var_pattern = r'\((\w+)\s+([0-9\.]+)\)'  # Matches variable name and value
            var_matches = re.findall(var_pattern, objectives_str)

            for var, value in var_matches:
                variables[var] = float(value)  # Store as float since value is a number

        # Now, parse the definitions of variables
        define_pattern = r'\(define-fun\s+(\w+)\s*\(\)\s*Real\s*([0-9\.]+)\)'  # Matches definitions like (define-fun x () Real 5.0)
        define_matches = re.findall(define_pattern, result)

        for var, value in define_matches:
            variables[var] = value  # Overwrite with the defined value (if any)

        return variables