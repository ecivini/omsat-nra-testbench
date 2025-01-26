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
                    timeout=self.timeout + 5
                )
                end_ts = time.time()

                err = process.stderr.decode()
                out = process.stdout.decode()

                if len(err) > 0:
                    if "unsat" in out:
                        result = "unsat"
                elif len(out) > 0:
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
                print("[-] Solver timed out with test case " + self.tasks[i])

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
        objectives_block = re.search(r"\(objectives\s*\n(.*?)\n\)", result, re.DOTALL)
    
        if not objectives_block:
            return []  # No objectives section found

        pattern = r"\(([\.\w]+) (\d+)\)"
        matches = re.findall(pattern, objectives_block.group(1))
        
        variables = {}
        for var, val in matches:
            variables[var] = val
        
        return variables