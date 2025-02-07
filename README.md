# Opti / MathSAT NRA Testbench

## Overview
This testbench is a tool for benchmarking and testing the Opti / MathSAT solver with Satisfiability Modulo Theory (SMT) and Optimization Modulo Theory (OMT) NRA problems. 

## Requirements
- Python 3+
- Required packages listed in `requirements.txt`
- Solvers you want to test available in the PATH

## Installation
```bash
git clone https://github.com/ecivini/omsat-nra-testbench
cd omsat-nra-testbench
pip3 install -r requirements.txt
cp config.omsat.yaml config.yaml
mkdir results
```

## Usage
In order to use the testbench, make sure to have a properly written config.yml file.
```bash
python3 testbench.py
```

### Configuration Options
Configuration of the testbench is done via the `config.yaml` file. You have to specify:
- `solver`: The solver you want to use (e.g., `optimathsat`, `mathsat`).
- `benchmarks`: Directoties containing the benchmarks (`.smt2 files`).

## Project Structure
- `benchmarks/`: Benchmark files taken from [omt-benchmarks](https://github.com/masinag/omt-benchmarks/releases) and are updated regularly.
- `requirements.txt`: List of Python dependencies.
- `testbench.py`: Main script for running tests.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for feedback and suggestions.

## License
This project is licensed under the MIT License. See the `LICENSE.md` file for details.

