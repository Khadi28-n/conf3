#!/usr/bin/env python3
import sys
import struct
import math
from xml.etree import ElementTree as ET

class UVMMemory:
    def __init__(self, size=1024):
        self.data = [0] * size  # единое адресное пространство

    def load_program(self, binary: bytes):
        # Программа хранится отдельно — просто читаем инструкции из файла
        self.code = binary

    def __getitem__(self, addr: int):
        return self.data[addr]

    def __setitem__(self, addr: int, value):
        self.data[addr] = int(value)

class UVMInterpreter:
    def __init__(self):
        self.mem = UVMMemory()
        self.pc = 0  # program counter (индекс в бинарнике)

    def fetch_decode(self, binary: bytes) -> Tuple[int, List[int], int]:
        if self.pc >= len(binary):
            return -1, [], 0
        first = binary[self.pc]
        opcode = first & 0x7F
        if opcode == 118:  # LOAD
            word = int.from_bytes(binary[self.pc:self.pc+6], 'little')
            const = (word >> 7) & 0x7FFFFF
            addr = (word >> 30) & 0x3FFF
            return opcode, [const, addr], 6
        elif opcode == 6:  # READ
            word = int.from_bytes(binary[self.pc:self.pc+6], 'little')
            ptr_addr = (word >> 7) & 0x3FFF
            dst_addr = (word >> 21) & 0x3FFF
            offset = (word >> 35) & 0x7F
            return opcode, [ptr_addr, dst_addr, offset], 6
        elif opcode == 44:  # WRITE
            word = int.from_bytes(binary[self.pc:self.pc+5], 'little')
            src_addr = (word >> 7) & 0x3FFF
            dst_addr = (word >> 21) & 0x3FFF
            return opcode, [src_addr, dst_addr], 5
        elif opcode == 57:  # SQRT
            word = int.from_bytes(binary[self.pc:self.pc+5], 'little')
            dst_addr = (word >> 7) & 0x3FFF
            ptr_to_addr = (word >> 21) & 0x3FFF
            return opcode, [dst_addr, ptr_to_addr], 5
        else:
            raise ValueError(f"Неизвестный opcode {opcode} по адресу {self.pc}")

    def execute(self, opcode: int, args: List[int]):
        if opcode == 118:  # LOAD const, addr
            const, addr = args
            self.mem[addr] = const
        elif opcode == 6:  # READ ptr_addr, dst_addr, offset
            ptr_addr, dst_addr, offset = args
            src_val_addr = self.mem[ptr_addr] + offset
            self.mem[dst_addr] = self.mem[src_val_addr]
        elif opcode == 44:  # WRITE src_addr, dst_addr
            src_addr, dst_addr = args
            self.mem[dst_addr] = self.mem[src_addr]
        elif opcode == 57:  # SQRT dst_addr, ptr_to_addr
            dst_addr, ptr_to_addr = args
            val_addr = self.mem[ptr_to_addr]
            value = self.mem[val_addr]
            if value < 0:
                raise ValueError(f"sqrt от отрицательного числа ({value})")
            self.mem[dst_addr] = int(math.isqrt(value))  # целочисленный sqrt

    def run(self, binary: bytes):
        self.pc = 0
        while self.pc < len(binary):
            opcode, args, size = self.fetch_decode(binary)
            if opcode == -1:
                break
            self.execute(opcode, args)
            self.pc += size

    def dump_memory_xml(self, start: int, end: int, out_path: str):
        root = ET.Element("memory")
        for addr in range(start, end+1):
            cell = ET.SubElement(root, "cell", address=str(addr))
            cell.text = str(self.mem[addr])
        tree = ET.ElementTree(root)
        tree.write(out_path, encoding="utf-8", xml_declaration=True)
        print(f" Дамп памяти [{start}..{end}] сохранён в {out_path}")