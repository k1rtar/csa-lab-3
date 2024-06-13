from __future__ import annotations

import json
from enum import Enum


class Opcode(str, Enum):
    LDA = "LDA"
    STA = "STA"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    INC = "INC"
    DEC = "DEC"
    JMP = "JMP"
    JZ = "JZ"
    IN = "IN"
    OUT = "OUT"
    HLT = "HLT"


def write_code(filename: str, data: list[int], code: list[dict[str, str | int]]) -> None:
    program = {"data": data, "code": code}
    with open(filename, "w") as f:
        json.dump(program, f, indent=4)


def read_code(filename: str) -> dict[str, list[int] | list[dict[str, str | int]]]:
    with open(filename) as f:
        return json.load(f)
