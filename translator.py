from __future__ import annotations

import json
import sys


def read_code(filename: str) -> dict:
    with open(filename) as f:
        lines = f.readlines()

    data_section = []
    code_section = []
    labels = {}
    current_address = 0
    in_data_section = False
    in_code_section = False

    for line in lines:
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if line == ".data":
            in_data_section = True
            in_code_section = False
            continue
        if line == ".code":
            in_data_section = False
            in_code_section = True
            continue

        if in_data_section:
            current_address = handle_data_section(line, labels, data_section, current_address)
        elif in_code_section:
            handle_code_section(line, labels, code_section)

    resolve_labels(code_section, labels)

    return {"data": data_section, "code": code_section}


def handle_data_section(line: str, labels: dict, data_section: list, current_address: int) -> int:
    if ":" in line:
        label, value = line.split(":", 1)
        label = label.strip()
        value = value.strip()
        if value.startswith("RESERVE"):
            _, reserve_size = value.split()
            reserve_size = int(reserve_size)
            labels[label] = current_address
            data_section.extend([0] * reserve_size)
            current_address += reserve_size
        elif value.isnumeric():
            labels[label] = current_address
            data_section.append(int(value))
            current_address += 1
        elif value.startswith("'") and value.endswith("'"):
            labels[label] = current_address
            data_section.append(ord(value[1]))
            current_address += 1
        elif value.startswith('"') and value.endswith('"'):
            labels[label] = current_address
            i = 0
            value = value[1:-1]
            while i < len(value):
                if value[i] == "\\" and i + 1 < len(value) and value[i + 1] == "n":
                    data_section.append(10)
                    current_address += 1
                    i += 2
                else:
                    data_section.append(ord(value[i]))
                    current_address += 1
                    i += 1
    elif line.isnumeric():
        data_section.append(int(line))
        current_address += 1
    return current_address


def handle_code_section(line: str, labels: dict, code_section: list) -> None:
    if ":" in line:
        label, _ = line.split(":", 1)
        label = label.strip()
        labels[label] = len(code_section)
    else:
        parts = line.split()
        opcode = parts[0]
        arg = parts[1] if len(parts) > 1 else None
        if arg and arg in labels:
            arg = labels[arg]
        if opcode in ["INC", "DEC", "HLT", "OUT", "IN"]:
            arg = None
        code_section.append({"opcode": opcode, "arg": arg})


def resolve_labels(code_section: list, labels: dict) -> None:
    for instruction in code_section:
        if instruction["opcode"] in ["JZ", "JMP"]:
            label_name = instruction["arg"]
            if isinstance(label_name, str):
                instruction["arg"] = labels.get(label_name, 0)
        elif (
            instruction["opcode"] == "LDA"
            and isinstance(instruction["arg"], str)
            and instruction["arg"].startswith("&")
        ):
            label_name = instruction["arg"][1:]
            if label_name in labels:
                instruction["arg"] = f"&{labels[label_name]}"
        elif (
            instruction["opcode"] == "LDA"
            and isinstance(instruction["arg"], str)
            and instruction["arg"].startswith("(")
        ):
            label_name = instruction["arg"][1:-1]
            if label_name in labels:
                instruction["arg"] = f"({labels[label_name]})"
        elif (
            instruction["opcode"] == "STA"
            and isinstance(instruction["arg"], str)
            and instruction["arg"].startswith("(")
        ):
            label_name = instruction["arg"][1:-1]
            if label_name in labels:
                instruction["arg"] = f"({labels[label_name]})"


def main(input_file: str | None = None, output_file: str | None = None):
    if input_file is None or output_file is None:
        if len(sys.argv) != 3:
            print("Usage: python translator.py <input_file> <output_file>")
            return
        input_file = sys.argv[1]
        output_file = sys.argv[2]

    program = read_code(input_file)

    with open(output_file, "w") as f:
        json.dump(program, f, indent=4)


if __name__ == "__main__":
    main()
