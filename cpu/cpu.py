'''
DMG Gameboy Emulator Project - MorganPG

cpu/cpy.py

Main CPU (SM83) emulation
See: 
https://rgbds.gbdev.io/docs/v1.0.3/gbz80.7#INSTRUCTION_REFERENCE 
https://gbdev.io/gb-opcodes/optables/
https://gbdev.io/pandocs/CPU_Registers_and_Flags.html
https://gbdev.io/pandocs/CPU_Instruction_Set.html
'''
from __future__ import annotations
from typing import TYPE_CHECKING
from memory.registers import Register, Register8b, Register16b, Register16b_uncombined, Register16b_mem, FlagRegister
from cpu.conditions import Conditional, NZ, Z, NC, C
if TYPE_CHECKING:
    from board.board import Motherboard

class CPU():
    def __init__(self, board:Motherboard) -> None:
        self.board = board
        self.cycles = 0

        self.flags = FlagRegister(0xB0)
        a = Register8b(0x01)
        b = Register8b(0x00)
        c = Register8b(0x13)
        d = Register8b(0x00)
        e = Register8b(0xD8)
        h = Register8b(0x01)
        l = Register8b(0x4D)

        af = Register16b(a,self.flags)
        bc = Register16b(b,c)
        de = Register16b(d,e)
        hl = Register16b(h,l)
        sp = Register16b_uncombined(0xFFFE)
        pc = Register16b_uncombined(0x0100)

        self.registers_8b:list[Register8b] = [
            b,
            c,
            d,
            e,
            h,
            l,
            Register16b_mem(hl, self.board.memory, 0),
            a
        ]
        
        self.registers_16b:list[Register16b|Register16b_uncombined] = [
            bc,de,hl,sp
        ]

        self.registers_16bstk:list[Register16b] = [
            bc,de,hl,af
        ]

        self.registers_16bmem:list[Register16b_mem] = [
            Register16b_mem(bc, self.board.memory, 0),
            Register16b_mem(de, self.board.memory, 0),
            Register16b_mem(hl, self.board.memory, 1),
            Register16b_mem(hl, self.board.memory, 2),   
        ]

        self.conditionals:list[Conditional] = [
            NZ(self.flags),
            Z(self.flags),
            NC(self.flags),
            C(self.flags)
        ]
        
        self.registers:dict[str,Register] = {
            "A": a,
            "B": b,
            "C": c,
            "D": d,
            "E": e,
            "F": self.flags,
            "H": h,
            "L": l,
            "AF": af,
            "BC": bc,
            "DE": de,
            "HL": hl,
            "SP": sp,
            "PC": pc
        }
    def read_next(self, count:int) -> bytearray:
        pc = self.registers["PC"]
        addr = pc.val

        data = self.board.memory.read(addr, count)
        pc.val += (addr + 1)

        return data

    def handle_stop(self, opcode:int, flags:str, cycles:list[int]):
        raise Exception("STOP")
    
    def handle_ld_r8_r8(self, opcode:int, flags:str, cycles:list[int]):
        source = self.registers_8b[opcode & 0b111]
        dest = self.registers_8b[(opcode >> 3) & 0b111]
        hl_mem = self.registers_8b[6]
        if source is hl_mem and dest is hl_mem:
            raise Exception("HALT")

        val = source.get()
        dest.set(val)

        self.cycles += cycles[0]
    
    def handle_inc_16b(self, opcode:int, is_dec:bool, flags:str, cycles:list[int]):
        operand = self.registers_16b[(opcode >> 4) & 0b11]

        if is_dec:
            operand.dec()
        else:
            operand.inc()

        self.cycles += cycles[0]

    def handle_ld_r16_imm16(self, opcode:int, flags:str, cycles:list[int]):
        dest = self.registers_16b[(opcode >> 4) & 0b11]
        val = int.from_bytes(self.read_next(2))

        dest.set(val)
        self.cycles += cycles[0]

    def handle_ld_r16mem_a(self, opcode:int, flags:str, cycles:list[int]):
        dest = self.registers_16bmem[(opcode >> 4) & 0b11]
        val = self.registers["A"].get()

        dest.set(val)
        self.cycles += cycles[0]

    def handle_ld_r8_imm8(self, opcode:int, flags:str, cycles:list[int]):
        dest = self.registers_8b[(opcode >> 3) & 0b111]
        val = self.read_next(1)[0]

        dest.set(val)
        self.cycles += cycles[0]

    def handle_ld_imm16_sp(self, opcode:int, flags:str, cycles:list[int]):
        val = self.registers["SP"].get()
        addr = int.from_bytes(self.read_next(2))

        self.board.memory.write(addr, bytearray([val]))
        self.cycles += cycles[0]

    def handle_ld_a_r16mem(self, opcode:int, flags:str, cycles:list[int]):
        dest = self.registers["A"]
        val = self.registers_16bmem[(opcode >> 4) & 0b11].get()

        dest.set(val)
        self.cycles += cycles[0]

    def handle_jr_imm8(self, opcode:int, is_conditional:bool, flags:str, cycles:list[int]):
        pass

    def handle_instruction(self, opcode):
        match opcode:
            case 0x00: #NOP
                pass
            case 0x01: #LD BC, n16
                self.handle_ld_r16_imm16(opcode, flags='----', cycles=[12])
            case 0x02: #LD [BC], A
                self.handle_ld_r16mem_a(opcode, flags='----', cycles=[8])
            case 0x03: #INC BC
                self.handle_inc_16b(opcode, False, flags='----', cycles=[8])
            case 0x04: #INC B
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[4])
            case 0x05: #DEC B
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[4])
            case 0x06: #LD B, n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[8])
            case 0x07: #RLCA
                self.handle_flags_etc(opcode, flags='000C', cycles=[4])
            case 0x08: #LD [a16], SP
                self.handle_ld_imm16_sp(opcode, flags='----', cycles=[20])
            case 0x09: #ADD HL, BC
                self.handle_add_hl_r16(opcode, flags='-0HC', cycles=[8])
            case 0x0A: #LD A, [BC]
                self.handle_ld_a_r16mem(opcode, flags='----', cycles=[8])
            case 0x0B: #DEC BC
                self.handle_inc_16b(opcode, True, flags='----', cycles=[8])
            case 0x0C: #INC C
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[4])
            case 0x0D: #DEC C
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[4])
            case 0x0E: #LD C, n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[8])
            case 0x0F: #RRCA
                self.handle_flags_etc(opcode, flags='000C', cycles=[4])
            case 0x10: #STOP n8
                self.handle_stop(opcode, flags='----', cycles=[4])
            case 0x11: #LD DE, n16
                self.handle_ld_r16_imm16(opcode, flags='----', cycles=[12])
            case 0x12: #LD [DE], A
                self.handle_ld_r16mem_a(opcode, flags='----', cycles=[8])
            case 0x13: #INC DE
                self.handle_inc_16b(opcode, False, flags='----', cycles=[8])
            case 0x14: #INC D
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[4])
            case 0x15: #DEC D
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[4])
            case 0x16: #LD D, n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[8])
            case 0x17: #RLA
                self.handle_flags_etc(opcode, flags='000C', cycles=[4])
            case 0x18: #JR e8
                self.handle_jr_imm8(opcode, False, flags='----', cycles=[12])
            case 0x19: #ADD HL, DE
                self.handle_add_hl_r16(opcode, flags='-0HC', cycles=[8])
            case 0x1A: #LD A, [DE]
                self.handle_ld_a_r16mem(opcode, flags='----', cycles=[8])
            case 0x1B: #DEC DE
                self.handle_inc_16b(opcode, True, flags='----', cycles=[8])
            case 0x1C: #INC E
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[4])
            case 0x1D: #DEC E
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[4])
            case 0x1E: #LD E, n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[8])
            case 0x1F: #RRA
                self.handle_flags_etc(opcode, flags='000C', cycles=[4])
            case 0x20: #JR NZ, e8
                self.handle_jr_imm8(opcode, True, flags='----', cycles=[12, 8])
            case 0x21: #LD HL, n16
                self.handle_ld_r16_imm16(opcode, flags='----', cycles=[12])
            case 0x22: #LD [HL+], A
                self.handle_ld_r16mem_a(opcode, flags='----', cycles=[8])
            case 0x23: #INC HL
                self.handle_inc_16b(opcode, False, flags='----', cycles=[8])
            case 0x24: #INC H
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[4])
            case 0x25: #DEC H
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[4])
            case 0x26: #LD H, n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[8])
            case 0x27: #DAA
                self.handle_flags_etc(opcode, flags='Z-0C', cycles=[4])
            case 0x28: #JR Z, e8
                self.handle_jr_imm8(opcode, True, flags='----', cycles=[12, 8])
            case 0x29: #ADD HL, HL
                self.handle_add_hl_r16(opcode, flags='-0HC', cycles=[8])
            case 0x2A: #LD A, [HL+]
                self.handle_ld_a_r16mem(opcode, flags='----', cycles=[8])
            case 0x2B: #DEC HL
                self.handle_inc_16b(opcode, True, flags='----', cycles=[8])
            case 0x2C: #INC L
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[4])
            case 0x2D: #DEC L
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[4])
            case 0x2E: #LD L, n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[8])
            case 0x2F: #CPL
                self.handle_flags_etc(opcode, flags='-11-', cycles=[4])
            case 0x30: #JR NC, e8
                self.handle_jr_imm8(opcode, True, flags='----', cycles=[12, 8])
            case 0x31: #LD SP, n16
                self.handle_ld_r16_imm16(opcode, flags='----', cycles=[12])
            case 0x32: #LD [HL-], A
                self.handle_ld_r16mem_a(opcode, flags='----', cycles=[8])
            case 0x33: #INC SP
                self.handle_inc_16b(opcode, False, flags='----', cycles=[8])
            case 0x34: #INC [HL]
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[12])
            case 0x35: #DEC [HL]
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[12])
            case 0x36: #LD [HL], n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[12])
            case 0x37: #SCF
                self.handle_flags_etc(opcode, flags='-001', cycles=[4])
            case 0x38: #JR C, e8
                self.handle_jr_imm8(opcode, True, flags='----', cycles=[12, 8])
            case 0x39: #ADD HL, SP
                self.handle_add_hl_r16(opcode, flags='-0HC', cycles=[8])
            case 0x3A: #LD A, [HL-]
                self.handle_ld_a_r16mem(opcode, flags='----', cycles=[8])
            case 0x3B: #DEC SP
                self.handle_inc_16b(opcode, True, flags='----', cycles=[8])
            case 0x3C: #INC A
                self.handle_inc_8b(opcode, False, flags='Z0H-', cycles=[4])
            case 0x3D: #DEC A
                self.handle_inc_8b(opcode, True, flags='Z1H-', cycles=[4])
            case 0x3E: #LD A, n8
                self.handle_ld_r8_imm8(opcode, flags='----', cycles=[8])
            case 0x3F: #CCF
                self.handle_flags_etc(opcode, flags='-00C', cycles=[4])
            case 0x40: #LD B, B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x41: #LD B, C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x42: #LD B, D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x43: #LD B, E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x44: #LD B, H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x45: #LD B, L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x46: #LD B, [HL]
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x47: #LD B, A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x48: #LD C, B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x49: #LD C, C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x4A: #LD C, D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x4B: #LD C, E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x4C: #LD C, H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x4D: #LD C, L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x4E: #LD C, [HL]
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x4F: #LD C, A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x50: #LD D, B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x51: #LD D, C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x52: #LD D, D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x53: #LD D, E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x54: #LD D, H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x55: #LD D, L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x56: #LD D, [HL]
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x57: #LD D, A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x58: #LD E, B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x59: #LD E, C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x5A: #LD E, D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x5B: #LD E, E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x5C: #LD E, H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x5D: #LD E, L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x5E: #LD E, [HL]
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x5F: #LD E, A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x60: #LD H, B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x61: #LD H, C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x62: #LD H, D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x63: #LD H, E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x64: #LD H, H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x65: #LD H, L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x66: #LD H, [HL]
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x67: #LD H, A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x68: #LD L, B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x69: #LD L, C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x6A: #LD L, D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x6B: #LD L, E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x6C: #LD L, H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x6D: #LD L, L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x6E: #LD L, [HL]
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x6F: #LD L, A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x70: #LD [HL], B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x71: #LD [HL], C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x72: #LD [HL], D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x73: #LD [HL], E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x74: #LD [HL], H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x75: #LD [HL], L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x76: #HALT
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x77: #LD [HL], A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x78: #LD A, B
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x79: #LD A, C
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x7A: #LD A, D
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x7B: #LD A, E
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x7C: #LD A, H
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x7D: #LD A, L
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x7E: #LD A, [HL]
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[8])
            case 0x7F: #LD A, A
                self.handle_ld_r8_r8(opcode, flags='----', cycles=[4])
            case 0x80: #ADD A, B
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x81: #ADD A, C
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x82: #ADD A, D
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x83: #ADD A, E
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x84: #ADD A, H
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x85: #ADD A, L
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x86: #ADD A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[8])
            case 0x87: #ADD A, A
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x88: #ADC A, B
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x89: #ADC A, C
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x8A: #ADC A, D
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x8B: #ADC A, E
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x8C: #ADC A, H
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x8D: #ADC A, L
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x8E: #ADC A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[8])
            case 0x8F: #ADC A, A
                self.handle_alu_8b(opcode, False, flags='Z0HC', cycles=[4])
            case 0x90: #SUB A, B
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x91: #SUB A, C
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x92: #SUB A, D
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x93: #SUB A, E
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x94: #SUB A, H
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x95: #SUB A, L
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x96: #SUB A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[8])
            case 0x97: #SUB A, A
                self.handle_alu_8b(opcode, False, flags='1100', cycles=[4])
            case 0x98: #SBC A, B
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x99: #SBC A, C
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x9A: #SBC A, D
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x9B: #SBC A, E
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x9C: #SBC A, H
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x9D: #SBC A, L
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0x9E: #SBC A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[8])
            case 0x9F: #SBC A, A
                self.handle_alu_8b(opcode, False, flags='Z1H-', cycles=[4])
            case 0xA0: #AND A, B
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[4])
            case 0xA1: #AND A, C
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[4])
            case 0xA2: #AND A, D
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[4])
            case 0xA3: #AND A, E
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[4])
            case 0xA4: #AND A, H
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[4])
            case 0xA5: #AND A, L
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[4])
            case 0xA6: #AND A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[8])
            case 0xA7: #AND A, A
                self.handle_alu_8b(opcode, False, flags='Z010', cycles=[4])
            case 0xA8: #XOR A, B
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xA9: #XOR A, C
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xAA: #XOR A, D
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xAB: #XOR A, E
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xAC: #XOR A, H
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xAD: #XOR A, L
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xAE: #XOR A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[8])
            case 0xAF: #XOR A, A
                self.handle_alu_8b(opcode, False, flags='1000', cycles=[4])
            case 0xB0: #OR A, B
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xB1: #OR A, C
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xB2: #OR A, D
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xB3: #OR A, E
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xB4: #OR A, H
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xB5: #OR A, L
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xB6: #OR A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[8])
            case 0xB7: #OR A, A
                self.handle_alu_8b(opcode, False, flags='Z000', cycles=[4])
            case 0xB8: #CP A, B
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0xB9: #CP A, C
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0xBA: #CP A, D
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0xBB: #CP A, E
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0xBC: #CP A, H
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0xBD: #CP A, L
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[4])
            case 0xBE: #CP A, [HL]
                self.handle_alu_8b(opcode, False, flags='Z1HC', cycles=[8])
            case 0xBF: #CP A, A
                self.handle_alu_8b(opcode, False, flags='1100', cycles=[4])
            case 0xC0: #RET NZ
                self.handle_ret(opcode, True, flags='----', cycles=[20, 8])
            case 0xC1: #POP BC
                self.handle_stack(opcode, True, flags='----', cycles=[12])
            case 0xC2: #JP NZ, a16
                self.handle_jp_imm16(opcode, True, flags='----', cycles=[16, 12])
            case 0xC3: #JP a16
                self.handle_jp_imm16(opcode, False, flags='----', cycles=[16])
            case 0xC4: #CALL NZ, a16
                self.handle_call_imm16(opcode, True, flags='----', cycles=[24, 12])
            case 0xC5: #PUSH BC
                self.handle_stack(opcode, False, flags='----', cycles=[16])
            case 0xC6: #ADD A, n8
                self.handle_alu_8b(opcode, True, flags='Z0HC', cycles=[8])
            case 0xC7: #RST $00
                self.handle_rst(opcode, flags='----', cycles=[16])
            case 0xC8: #RET Z
                self.handle_ret(opcode, True, flags='----', cycles=[20, 8])
            case 0xC9: #RET
                self.handle_ret(opcode, False, flags='----', cycles=[16])
            case 0xCA: #JP Z, a16
                self.handle_jp_imm16(opcode, True, flags='----', cycles=[16, 12])
            case 0xCB: #PREFIX
                self.handle_prefix(opcode, flags='----', cycles=[4])
            case 0xCC: #CALL Z, a16
                self.handle_call_imm16(opcode, True, flags='----', cycles=[24, 12])
            case 0xCD: #CALL a16
                self.handle_call_imm16(opcode, False, flags='----', cycles=[24])
            case 0xCE: #ADC A, n8
                self.handle_alu_8b(opcode, True, flags='Z0HC', cycles=[8])
            case 0xCF: #RST $08
                self.handle_rst(opcode, flags='----', cycles=[16])
            case 0xD0: #RET NC
                self.handle_ret(opcode, True, flags='----', cycles=[20, 8])
            case 0xD1: #POP DE
                self.handle_stack(opcode, True, flags='----', cycles=[12])
            case 0xD2: #JP NC, a16
                self.handle_jp_imm16(opcode, True, flags='----', cycles=[16, 12])
            case 0xD3: #ILLEGAL_D3
                raise NotImplementedError('Undefined opcode 0xD3')
            case 0xD4: #CALL NC, a16
                self.handle_call_imm16(opcode, True, flags='----', cycles=[24, 12])
            case 0xD5: #PUSH DE
                self.handle_stack(opcode, False, flags='----', cycles=[16])
            case 0xD6: #SUB A, n8
                self.handle_alu_8b(opcode, True, flags='Z1HC', cycles=[8])
            case 0xD7: #RST $10
                self.handle_rst(opcode, flags='----', cycles=[16])
            case 0xD8: #RET C
                self.handle_ret(opcode, True, flags='----', cycles=[20, 8])
            case 0xD9: #RETI
                self.handle_reti(opcode, flags='----', cycles=[16])
            case 0xDA: #JP C, a16
                self.handle_jp_imm16(opcode, True, flags='----', cycles=[16, 12])
            case 0xDB: #ILLEGAL_DB
                raise NotImplementedError('Undefined opcode 0xDB')
            case 0xDC: #CALL C, a16
                self.handle_call_imm16(opcode, True, flags='----', cycles=[24, 12])
            case 0xDD: #ILLEGAL_DD
                raise NotImplementedError('Undefined opcode 0xDD')
            case 0xDE: #SBC A, n8
                self.handle_alu_8b(opcode, True, flags='Z1HC', cycles=[8])
            case 0xDF: #RST $18
                self.handle_rst(opcode, flags='----', cycles=[16])
            case 0xE0: #LDH [a8], A
                self.handle_ldh_imm8_a(opcode, flags='----', cycles=[12])
            case 0xE1: #POP HL
                self.handle_stack(opcode, True, flags='----', cycles=[12])
            case 0xE2: #LDH [C], A
                self.handle_ldh_c_a(opcode, flags='----', cycles=[8])
            case 0xE3: #ILLEGAL_E3
                raise NotImplementedError('Undefined opcode 0xE3')
            case 0xE4: #ILLEGAL_E4
                raise NotImplementedError('Undefined opcode 0xE4')
            case 0xE5: #PUSH HL
                self.handle_stack(opcode, False, flags='----', cycles=[16])
            case 0xE6: #AND A, n8
                self.handle_alu_8b(opcode, True, flags='Z010', cycles=[8])
            case 0xE7: #RST $20
                self.handle_rst(opcode, flags='----', cycles=[16])
            case 0xE8: #ADD SP, e8
                self.handle_add_sp_imm8(opcode, flags='00HC', cycles=[16])
            case 0xE9: #JP HL
                self.handle_jp_hl(opcode, flags='----', cycles=[4])
            case 0xEA: #LD [a16], A
                self.handle_ld_imm16_a(opcode, flags='----', cycles=[16])
            case 0xEB: #ILLEGAL_EB
                raise NotImplementedError('Undefined opcode 0xEB')
            case 0xEC: #ILLEGAL_EC
                raise NotImplementedError('Undefined opcode 0xEC')
            case 0xED: #ILLEGAL_ED
                raise NotImplementedError('Undefined opcode 0xED')
            case 0xEE: #XOR A, n8
                self.handle_alu_8b(opcode, True, flags='Z000', cycles=[8])
            case 0xEF: #RST $28
                self.handle_rst(opcode, flags='----', cycles=[16])
            case 0xF0: #LDH A, [a8]
                self.handle_ldh_a_imm8(opcode, flags='----', cycles=[12])
            case 0xF1: #POP AF
                self.handle_stack(opcode, True, flags='ZNHC', cycles=[12])
            case 0xF2: #LDH A, [C]
                self.handle_ldh_a_c(opcode, flags='----', cycles=[8])
            case 0xF3: #DI
                self.handle_int_control(opcode, False, flags='----', cycles=[4])
            case 0xF4: #ILLEGAL_F4
                raise NotImplementedError('Undefined opcode 0xF4')
            case 0xF5: #PUSH AF
                self.handle_stack(opcode, False, flags='----', cycles=[16])
            case 0xF6: #OR A, n8
                self.handle_alu_8b(opcode, True, flags='Z000', cycles=[8])
            case 0xF7: #RST $30
                self.handle_rst(opcode, flags='----', cycles=[16])
            case 0xF8: #LD HL, SP+, e8
                self.handle_ld_hl_sp_imm8(opcode, flags='00HC', cycles=[12])
            case 0xF9: #LD SP, HL
                self.handle_ld_sp_hl(opcode, flags='----', cycles=[8])
            case 0xFA: #LD A, [a16]
                self.handle_ld_a_imm16(opcode, flags='----', cycles=[16])
            case 0xFB: #EI
                self.handle_int_control(opcode, True, flags='----', cycles=[4])
            case 0xFC: #ILLEGAL_FC
                raise NotImplementedError('Undefined opcode 0xFC')
            case 0xFD: #ILLEGAL_FD
                raise NotImplementedError('Undefined opcode 0xFD')
            case 0xFE: #CP A, n8
                self.handle_alu_8b(opcode, True, flags='Z1HC', cycles=[8])
            case 0xFF: #RST $38
                self.handle_rst(opcode, flags='----', cycles=[16])