from __future__ import annotations


class DataPath:
    def __init__(self, data_memory_size: int, input_port: list[str]):
        self.data_memory: list[int] = [0] * data_memory_size
        self.input_port: list[str] = input_port
        self.output_port: list[str] = []
        self.acc: int = 0
        self.ar: int = 0
        self.dr: int = 0
        self.is_char_output: bool = False

    def signal_latch_addr(self, addr: int) -> None:
        if 0 <= addr < len(self.data_memory):
            self.ar = addr
        else:
            raise AddressOutOfRangeError(addr)

    def signal_latch_dr(self, value: int) -> None:
        self.dr = value

    def signal_latch_acc(self, value: int) -> None:
        self.acc = value

    def signal_oe(self) -> None:
        if 0 <= self.ar < len(self.data_memory):
            self.dr = self.data_memory[self.ar]
        else:
            raise AddressOutOfRangeError(self.ar)

    def signal_wr(self) -> None:
        if 0 <= self.ar < len(self.data_memory):
            self.data_memory[self.ar] = self.dr
        else:
            raise AddressOutOfRangeError(self.ar)

    def signal_output(self) -> None:
        if 0 <= self.acc < 128:
            self.output_port.append(chr(self.acc))
        else:
            self.output_port.append(str(self.acc))

    def signal_input(self) -> None:
        if not self.input_port:
            self.acc = 0
            return
        self.acc = ord(self.input_port.pop(0))

    def zero_flag(self) -> bool:
        return self.acc == 0

    def sel_op1(self, control_signal: str) -> int:
        if control_signal == "DR":
            return self.dr
        if control_signal == "ARG":
            return self.ar
        return 0

    def sel_op2(self, control_signal: str) -> int:
        if control_signal == "ACC":
            return self.acc
        return 0

    def alu_operation(self, operation: str, op1: int, op2: int) -> int:
        if operation == "ADD":
            return op1 + op2
        if operation == "SUB":
            return op1 - op2
        if operation == "MUL":
            return op1 * op2
        if operation == "DIV":
            return op1 // op2 if op2 != 0 else 0
        return op1

    def signal_alu_to_acc(self, alu_result: int) -> None:
        self.acc = alu_result


class AddressOutOfRangeError(Exception):
    def __init__(self, address: int):
        super().__init__(f"Address {address} out of range")
