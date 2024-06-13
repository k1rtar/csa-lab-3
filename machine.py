from __future__ import annotations

import logging
import sys

from controlunit import ControlUnit
from datapath import DataPath
from isa import read_code


def simulation(
    code: dict[str, list[int] | list[dict[str, str | int]]],
    input_tokens: list[str],
    data_memory_size: int,
    limit: int,
) -> tuple[str, int]:
    data_path = DataPath(data_memory_size, input_tokens)
    data_path.data_memory[: len(code["data"])] = code["data"]
    control_unit = ControlUnit(code, data_path)
    instr_counter = 0

    try:
        while instr_counter < limit:
            control_unit.step()
            instr_counter += 1
    except StopIteration:
        pass

    return "".join(data_path.output_port), instr_counter


def main(code_file: str | None = None, input_file: str | None = None):
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s :  %(message)s")

    if code_file is None or input_file is None:
        if len(sys.argv) != 3:
            print("Usage: machine.py <code_file> <input_file>")
            return
        code_file = sys.argv[1]
        input_file = sys.argv[2]

    program = read_code(code_file)
    with open(input_file) as f:
        input_tokens = list(f.read())

    output, instr_counter = simulation(program, input_tokens, 100, 1000)
    print("Output:", output)


if __name__ == "__main__":
    main()
