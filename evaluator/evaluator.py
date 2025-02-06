import subprocess
import time
import re
import json

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
            stats = {}
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

                # Parse statistics
                stats = self.parse_stats(out)
                
                solve_time = end_ts - start_ts
            except Exception as e:
                print("[-] Solver timed out with test case " + self.tasks[i] + ": " + str(e))

            # TODO: Avoid race conditions when updating result file
            # solver,timeout,test case,result,optimum,time,nano_time,opt_time,check_exact_time,check_crosses_time,check_espilon_time,sol_found_by
            file_line = self.name + ","

            # timeout
            file_line += str(self.timeout) + ","

            # test case
            file_line += self.tasks[i] + ","

            # result
            file_line += result + ","

            # optimum
            file_line += str(optimum) + ","

            # time
            file_line += str(round(solve_time, 4)) + ","

            # stats
            file_line += self.gen_stats_line(stats)

            file_line += "\n"

            self.res_file.write(file_line)

    def parse_objectives(self, result):
        objectives_block = re.search(r"\(objectives\s*\n(.*?)\n\)", result, re.DOTALL)
    
        if not objectives_block:
            return {}  # No objectives section found

        pattern = r"\(([\.\w]+) (\d+)\)"
        matches = re.findall(pattern, objectives_block.group(1))
        
        variables = {}
        for var, val in matches:
            variables[var] = val
        
        return variables
    
    def parse_stats(self, result):
        # Initialize an empty dictionary to store the parsed data
        parsed_data = {}

        # Regular expression to match the key-value pairs
        pattern = r':([\w-]+)\s+([0-9\.]+)'
        
        # Find all matches in the input string
        matches = re.findall(pattern, result)
        
        # Populate the dictionary with key-value pairs
        for key, value in matches:
            # Convert value to int if possible, else to float
            if '.' in value:
                parsed_data[key] = float(value)
            else:
                parsed_data[key] = int(value)
                
        return parsed_data

    def gen_stats_line(self, stats):
        nano_metrics = [
            "nano-total-calls",
            "nano-complete-calls",
            "nano-conflicts",
            "nano-implications",
            "nano-explanations",
            "nano-total-time-check",
            "nano-total-time-opt",
            "nano-total-time-sat-check-exact-substitution",
            "nano-total-time-sat-check-crosses",
            "nano-total-time-sat-check-epsilon-box",
            "nano-successful-opt",
            "nano-total-opt",
            "nano-successful-sat-check-exact-substitution",
            "nano-total-sat-check-exact-substitution",
            "nano-successful-sat-check-crosses",
            "nano-total-sat-check-crosses",
            "nano-successful-sat-check-epsilon-box",
            "nano-total-sat-check-epsilon-box"
        ]

        line = ""
        for metric in nano_metrics:
            if metric in stats:
                line += str(stats[metric])
            else:
                line += "NA"

            line += ","

        return line[:-1]

