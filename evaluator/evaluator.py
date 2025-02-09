import subprocess
import time
import re
import json

class Evaluator:

    def __init__(self, name: str, cmd: str, params: str, timeout: int, kind: str, res_file):
        self.name = name 
        self.cmd = cmd
        self.params = params
        self.timeout = timeout
        self.res_file = res_file
        self.tasks = []
        self.next_id = 0
        self.kind = kind

    def add_task(self, test_case: str):
        self.tasks.append(test_case)

    def solve(self):
        for i in range(self.next_id, len(self.tasks)):
            result = "timeout"
            solve_time = 0
            optimum = "NF"
            partial = None
            model = None
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
                    print("Err: ", err)
                    result = "error"
                elif len(out) > 0:
                    # Parse eventual errors
                    if "(error \"" in out:
                        print("Error [" + self.tasks[i] + "]: " + self.get_error(out))
                        continue
                    # Check if unsat
                    elif "unsat" in out:
                        result = "unsat"
                    # Parse result
                    else:
                        result = "sat"
                        # TODO: Add support for multiple objectives
                        obj = self.get_objective(out)
                        if obj:
                            optimum = obj

                        partial = self.get_partial_result(out)
                        if partial != None:
                            result = "timeout"

                        model = self.get_model(out)
                        if model == None:
                            result = "timeout"

                # Parse statistics
                stats = self.parse_stats(out)
                
                solve_time = end_ts - start_ts
            except Exception as e:
                print("[-] Solver timed out with test case " + self.tasks[i] + ": " + str(e))

            # TODO: Avoid race conditions when updating result file
            file_line = self.kind + ","

            # solver name
            file_line += self.name + ","

            # timeout
            file_line += str(self.timeout) + ","

            # test case
            file_line += self.tasks[i] + ","

            # result
            file_line += result + ","

            # time
            file_line += str(round(solve_time, 4)) + ","

            # Create specific data
            if self.kind == "OMT":
                file_line += self.create_omt_result(optimum, partial)
            else:
                file_line += self.create_smt_result(model)

            # stats
            file_line += self.gen_stats_line(stats)

            file_line += "\n"

            self.res_file.write(file_line)

    def get_objective(self, output):
        start = None
        try:
            start = output.index(".cost0")
        except:
            return None
        
        # Parse from the first occurrence of `.cost0`
        parenthesis = 0
        obj = ""

        # len(".cost0 ") = 7
        for i in range(start + 7, len(output)):
            char = output[i]
            if char == '(':
                parenthesis += 1
                obj += char
            elif char == ')' and parenthesis > 0:
                parenthesis -= 1
                obj += char
            elif char == ')' and parenthesis == 0:
                break
            else:
                obj += char

        return obj

    def get_error(self, output):
        start = None
        try:
            start = output.index("(error \"")
        except:
            return None
        
        # Parse from the first occurrence of `.cost0`
        error = "(error \""
        parenthesis = 0

        # len(".cost0 ") = 7
        for i in range(start + 8, len(output)):
            char = output[i]
            error += char
            if char == '(':
                parenthesis += 1
            elif char == ')' and parenthesis > 0:
                parenthesis -= 1
            elif char == ')' and parenthesis == 0:
                break

        return error
    
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
    
    def get_model(self, output):
        blocks = []
        stack = []
        start = None

        for i, char in enumerate(output):
            if output[i:i+6] == "(model": 
                if not stack:
                    start = i 
                stack.append("(")
            elif char == "(" and stack:
                stack.append("(") 
            elif char == ")" and stack:
                stack.pop() 
                if not stack: 
                    block = output[start:i+1]
                    block = block.replace("\n", "\\n")
                    blocks.append(block)

        if len(blocks) == 0:
            return None

        return blocks[0]
    
    def get_partial_result(self, output):
        pattern = r"range: \[ ([^\]]+)\ ]"
        match = re.search(pattern, output)
        if match:
            return match.group(1)
        return None

    # TODO
    def create_omt_result(self, optimum: float, partial):
        # optimum,partial_lower,partial_higher,
        line = str(optimum) + ","

        if partial != None:
            line += str(partial).replace(", ", ",") + ","
        else:
            line += "NA,NA,"

        return line

    def create_smt_result(self, model):
        line = "NF,"
        if model:
            model = model.replace("\n", "\\n")
            line = model + ","
        return line

