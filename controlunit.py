from __future__ import annotations

import logging

from datapath import DataPath
from isa import Opcode


class ControlUnit:
    def __init__(self, program: dict[str, list[int] | list[dict[str, int | str]]], data_path: DataPath):
        self.program = program
        self.data_path = data_path
        self.pc: int = 0
        self.tick_count = 0
        self.instr_count = 0

    def info(self) -> None:
        instr = self.program["code"][self.pc] if self.pc < len(self.program["code"]) else {"opcode": "HLT", "arg": None}
        log_message = (
            f"TICK: {self.tick_count:<5} "
            f"INSTR_COUNT: {self.instr_count:<5} "
            f"PC: {self.pc:<4} "
            f"INSTR: {instr['opcode']:<4} {instr['arg'] if instr['arg'] is not None else '':<4} "
            f"AR: {self.data_path.ar:<4} "
            f"DR: {self.data_path.dr:<4} "
            f"ACC: {self.data_path.acc:<4} "
            f"Z-Flag: {self.data_path.zero_flag():<4} "
        )
        logging.debug(log_message)

    def execute_instruction(self, opcode: Opcode, arg: int | str | None) -> int:
        ticks = 2

        opcode_handlers = {
            Opcode.HLT: self.handle_hlt,
            Opcode.LDA: self.handle_lda,
            Opcode.STA: self.handle_sta,
            Opcode.ADD: self.handle_add,
            Opcode.SUB: self.handle_sub,
            Opcode.INC: self.handle_inc,
            Opcode.DEC: self.handle_dec,
            Opcode.MUL: self.handle_mul,
            Opcode.DIV: self.handle_div,
            Opcode.JMP: self.handle_jmp,
            Opcode.JZ: self.handle_jz,
            Opcode.IN: self.handle_in,
            Opcode.OUT: self.handle_out,
        }

        if opcode in opcode_handlers:
            ticks += opcode_handlers[opcode](arg)

        return ticks

    def handle_hlt(self, arg: int | str | None) -> int:
        raise StopIteration()

    def handle_lda(self, arg: int | str | None) -> int:
        ticks = 1
        if isinstance(arg, str):
            if arg.startswith("&"):
                address = int(arg[1:])
                self.data_path.signal_latch_addr(address)
                self.data_path.signal_oe()
                ticks += 1
                data = self.data_path.ar
                self.data_path.signal_latch_acc(data)
                ticks += 1
            elif arg.startswith("("):
                address = int(arg[1:-1])
                self.data_path.signal_latch_addr(address)
                self.data_path.signal_oe()
                ticks += 1
                indirect_address = self.data_path.dr
                if indirect_address >= len(self.data_path.data_memory):
                    raise IndirectAddressError()
                self.data_path.signal_latch_addr(indirect_address)
                self.data_path.signal_oe()
                ticks += 1
                data = self.data_path.dr
                self.data_path.signal_latch_acc(data)
                ticks += 1
        else:
            address = int(arg)
            self.data_path.signal_latch_addr(address)
            self.data_path.signal_oe()
            ticks += 1
            data = self.data_path.dr
            self.data_path.signal_latch_acc(data)
            ticks += 1
        return ticks

    def handle_sta(self, arg: int | str | None) -> int:
        ticks = 1
        if isinstance(arg, str) and arg.startswith("("):
            address = int(arg[1:-1])
            self.data_path.signal_latch_addr(address)
            self.data_path.signal_oe()
            ticks += 1
            indirect_address = self.data_path.dr
            if indirect_address >= len(self.data_path.data_memory):
                raise IndirectAddressError()
            self.data_path.signal_latch_addr(indirect_address)
            self.data_path.signal_latch_dr(self.data_path.acc)
            self.data_path.signal_wr()
            ticks += 1
        else:
            address = int(arg)
            self.data_path.signal_latch_addr(address)
            self.data_path.signal_latch_dr(self.data_path.acc)
            self.data_path.signal_wr()
            ticks += 1
        return ticks

    def handle_add(self, arg: int | str | None) -> int:
        ticks = 1
        address = int(arg)
        self.data_path.signal_latch_addr(address)
        self.data_path.signal_oe()
        ticks += 1
        op1 = self.data_path.dr
        op2 = self.data_path.acc
        result = self.data_path.alu_operation("ADD", op1, op2)
        self.data_path.signal_alu_to_acc(result)
        ticks += 1
        return ticks

    def handle_sub(self, arg: int | str | None) -> int:
        ticks = 1
        address = int(arg)
        self.data_path.signal_latch_addr(address)
        self.data_path.signal_oe()
        ticks += 1
        op1 = self.data_path.acc
        op2 = self.data_path.dr
        result = self.data_path.alu_operation("SUB", op1, op2)
        self.data_path.signal_alu_to_acc(result)
        ticks += 1
        return ticks

    def handle_inc(self, arg: int | str | None = None) -> int:
        op2 = self.data_path.acc
        result = self.data_path.alu_operation("ADD", op2, 1)
        self.data_path.signal_alu_to_acc(result)
        return 1

    def handle_dec(self, arg: int | str | None = None) -> int:
        op2 = self.data_path.acc
        result = self.data_path.alu_operation("SUB", op2, 1)
        self.data_path.signal_alu_to_acc(result)
        return 1

    def handle_mul(self, arg: int | str | None) -> int:
        ticks = 1
        address = int(arg)
        self.data_path.signal_latch_addr(address)
        self.data_path.signal_oe()
        ticks += 1
        op1 = self.data_path.dr
        op2 = self.data_path.acc
        result = self.data_path.alu_operation("MUL", op1, op2)
        self.data_path.signal_alu_to_acc(result)
        ticks += 1
        return ticks

    def handle_div(self, arg: int | str | None) -> int:
        ticks = 1
        address = int(arg)
        self.data_path.signal_latch_addr(address)
        self.data_path.signal_oe()
        ticks += 1
        op1 = self.data_path.acc
        op2 = self.data_path.dr
        result = self.data_path.alu_operation("DIV", op1, op2)
        self.data_path.signal_alu_to_acc(result)
        ticks += 1
        return ticks

    def handle_jmp(self, arg: int | str | None) -> int:
        self.pc = int(arg) - 1
        return 1

    def handle_jz(self, arg: int | str | None) -> int:
        if self.data_path.zero_flag():
            self.pc = int(arg) - 1
        return 1

    def handle_in(self, arg: int | str | None = None) -> int:
        try:
            self.data_path.signal_input()
        except EOFError:
            self.pc = len(self.program["code"])
        return 1

    def handle_out(self, arg: int | str | None = None) -> int:
        self.data_path.signal_output()
        return 1

    def step(self) -> None:
        if self.pc >= len(self.program["code"]):
            raise EndOfProgramError()

        instr = self.program["code"][self.pc]
        opcode = instr["opcode"]
        arg = instr.get("arg")

        self.info()
        self.tick_count += self.execute_instruction(opcode, arg)
        self.instr_count += 1
        self.pc += 1


class IndirectAddressError(Exception):
    def __init__(self, message: str = "Indirect address out of range"):
        super().__init__(message)


class EndOfProgramError(Exception):
    def __init__(self, message: str = "End of program reached"):
        super().__init__(message)
