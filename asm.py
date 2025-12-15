#!/usr/bin/env python3
import sys
import re
from typing import List, Tuple, Union

# Промежуточное представление: список кортежей (opcode, args...)
Command = Tuple[int, ...]

def parse_asm_line(line: str) -> Union[Command, None]:
    line = line.strip()
    if not line or line.startswith(';'):
        return None

    parts = re.split(r'[, \t]+', line)
    mnemonic = parts[0].upper()
    args = [int(x) for x in parts[1:] if x]

    if mnemonic == 'LOAD':
        # LOAD const, addr → A=118, B=const, C=addr
        const, addr = args
        return (118, const, addr)
    elif mnemonic == 'READ':
        # READ ptr_addr, dst_addr, offset → A=6, B=ptr_addr, C=dst_addr, D=offset
        ptr_addr, dst_addr, offset = args
        return (6, ptr_addr, dst_addr, offset)
    elif mnemonic == 'WRITE':
        # WRITE src_addr, dst_addr → A=44, B=src_addr, C=dst_addr
        src_addr, dst_addr = args
        return (44, src_addr, dst_addr)
    elif mnemonic == 'SQRT':
        # SQRT dst_addr, ptr_to_addr → A=57, B=dst_addr, C=ptr_to_addr
        dst_addr, ptr_to_addr = args
        return (57, dst_addr, ptr_to_addr)
    else:
        raise ValueError(f"Неизвестная команда: {mnemonic}")

def assemble_to_ir(asm_lines: List[str]) -> List[Command]:
    ir = []
    for i, line in enumerate(asm_lines, 1):
        cmd = parse_asm_line(line)
        if cmd:
            ir.append(cmd)
    return ir

def print_ir_debug(ir: List[Command]):
    print("Промежуточное представление:")
    for i, cmd in enumerate(ir):
        print(f"[{i:2}] {cmd}")

def main():
    if len(sys.argv) < 3:
        print("Использование: python asm.py <input.asm> <output.bin> [--test]")
        sys.exit(1)

    in_path = sys.argv[1]
    out_path = sys.argv[2]
    test_mode = '--test' in sys.argv

    with open(in_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    ir = assemble_to_ir(lines)

    if test_mode:
        print_ir_debug(ir)
        print("\nТестирование соответствия спецификации:")
        # Проверим 4 тестовые команды
        expected = [
            (118, 522, 70),
            (6, 499, 771, 53),
            (44, 229, 336),
            (57, 807, 863)
        ]
        assert ir[:4] == expected, f"Ожидалось: {expected}, получено: {ir[:4]}"
        print("Все тесты из спецификации пройдены.")

    # Этап 2: запись в бинарный файл (см. ниже)
    from encode import encode_commands
    binary = encode_commands(ir)
    with open(out_path, 'wb') as f:
        f.write(binary)
    print(f" Ассемблировано {len(ir)} команд(ы). Результат записан в {out_path}")

if __name__ == "__main__":
    main()