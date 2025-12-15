# encode.py
import struct
from typing import List, Tuple

def encode_command(cmd: Tuple[int, ...]) -> bytes:
    opcode = cmd[0]
    if opcode == 118:  # LOAD
        _, const, addr = cmd
        # A (7 бит) | B (23 бита) | C (14 бит) → 43 бита = 6 байт
        word = (opcode & 0x7F)
        word |= ((const & 0x7FFFFF) << 7)
        word |= ((addr & 0x3FFF) << 30)
        return word.to_bytes(6, 'little')
    elif opcode == 6:  # READ
        _, ptr_addr, dst_addr, offset = cmd
        # A(7) | B(14) | C(14) | D(7) = 42 бита → дополняем 6 байт
        word = (opcode & 0x7F)
        word |= ((ptr_addr & 0x3FFF) << 7)
        word |= ((dst_addr & 0x3FFF) << 21)
        word |= ((offset & 0x7F) << 35)
        return word.to_bytes(6, 'little')
    elif opcode == 44:  # WRITE
        _, src_addr, dst_addr = cmd
        # A(7) | B(14) | C(14) = 35 бит → 5 байт
        word = (opcode & 0x7F)
        word |= ((src_addr & 0x3FFF) << 7)
        word |= ((dst_addr & 0x3FFF) << 21)
        return word.to_bytes(5, 'little')
    elif opcode == 57:  # SQRT
        _, dst_addr, ptr_to_addr = cmd
        word = (opcode & 0x7F)
        word |= ((dst_addr & 0x3FFF) << 7)
        word |= ((ptr_to_addr & 0x3FFF) << 21)
        return word.to_bytes(5, 'little')
    else:
        raise ValueError(f"Неизвестный opcode: {opcode}")

def encode_commands(cmds: List[Tuple[int, ...]]) -> bytes:
    buf = bytearray()
    for cmd in cmds:
        buf.extend(encode_command(cmd))
    return bytes(buf)

def decode_for_test(binary: bytes) -> List[str]:
    # Тестовый вывод в формате спецификации
    i = 0
    out = []
    while i < len(binary):
        first = binary[i]
        opcode = first & 0x7F
        if opcode == 118:
            word = int.from_bytes(binary[i:i+6], 'little')
            const = (word >> 7) & 0x7FFFFF
            addr = (word >> 30) & 0x3FFF
            out.append(f"0x{first:02X}, 0x{binary[i+1]:02X}, 0x{binary[i+2]:02X}, "
                       f"0x{binary[i+3]:02X}, 0x{binary[i+4]:02X}, 0x{binary[i+5]:02X}")
            i += 6
        elif opcode == 6:
            word = int.from_bytes(binary[i:i+6], 'little')
            out.append(", ".join(f"0x{b:02X}" for b in binary[i:i+6]))
            i += 6
        elif opcode in (44, 57):
            out.append(", ".join(f"0x{b:02X}" for b in binary[i:i+5]))
            i += 5
    return out