# OMT Testbench

> This project is still under development and the results may not be accurate in some cases.

## Overview
The OMT Testbench is a tool for benchmarking and testing Optimization Modulo Theory (OMT) solvers. 

## Features
- **Multiple Solver Support:** Easily integrate and test multiple OMT solvers.
- **Benchmarking Tools:** Automated performance measurement and comparison.

## Requirements
- Python 3+
- Required packages listed in `requirements.txt`
- Solvers you want to test available in the PATH

## Installation
```bash
git clone https://github.com/ecivini/omt-testbench
cd omt-testbench
pip3 install -r requirements.txt
cp config.z3.yaml config.yaml
mkdir results
```

## Usage
In order to use the testbench, make sure to have a properly written config.yml file.
```bash
python3 testbench.py
```

### Configuration Options
Configuration of the testbench is done via the `config.yaml` file. You have to specify:
- `solver`: The solver you want to use (e.g., `optimathsat`, `z3`).
- `benchmarks`: Directoties containing the benchmarks (`.smt2 files`).

## Project Structure
- `benchmarks/`: Benchmark files taken from [omt-benchmarks](https://github.com/masinag/omt-benchmarks/releases) and are updated regularly.
- `requirements.txt`: List of Python dependencies.
- `testbench.py`: Main script for running tests.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for feedback and suggestions.

## License
This project is licensed under the MIT License. See the `LICENSE.md` file for details.

