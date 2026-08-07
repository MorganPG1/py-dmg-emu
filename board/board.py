'''
DMG Gameboy Emulator Project - MorganPG

board/board.py

A 'motherboard' like structure, allows all major components to interact with each other
See:
https://gbdev.io/pandocs/Memory_Map.html
'''
from memory.memory import MemoryController, MemoryRegion
from memory.ram import RAM
from cpu.cpu import CPU
from cartridge.cart import Cart
from time import sleep
from board.io import IO
from board.ppu import PPU
from os.path import exists
from debug.symbols import SymbolParser
from cartridge.mbc import UnbankedMBC, BankedMBC, MBC
class Motherboard():
    def __init__(self, romfile:str, debug_symbols:str="") -> None:
        self.pc_last = 0
        self.cycles = 0
        self.debug = False
        self.syms = None
        if debug_symbols != "":
            self.debug = True
            self.syms = SymbolParser(debug_symbols)
        self.ppu = PPU()

        self.cart = Cart(romfile)
        self.mbc:MBC = self.cart.getMBC()
        ram = RAM(0x2000)
        vram = self.ppu.vram
        eram = RAM(0x2000)
        oam = self.ppu.oam
        self.io = IO(self, self.debug)
        
        memory_map:dict[tuple[int,int], MemoryRegion] = {
            (0x0000, 0x8000): self.mbc,
            (0x8000, 0xA000): vram,
            (0xA000, 0xC000): eram,
            (0xC000, 0xE000): ram,
            (0xE000, 0xFE00): ram,
            (0xFE00, 0xFF00): oam,
            (0xFF00, 0x10000): self.io,
        }

        self.memory:MemoryController = MemoryController(memory_map)
        self.cpu = CPU(self)

        pass

    def hexformat(self, val:int):
        return hex(val)[2:].rjust(2, "0").upper()
    def hexformat2b(self,val:int):
        return hex(val)[2:].rjust(4, "0").upper()
    def stepIo(self, cycles:int):
        irq = self.io.step(cycles)
        if irq:
            self.cpu.fire_interrupt(2)

        irqs = self.ppu.step(cycles)
        for irq in irqs:
            self.cpu.fire_interrupt(irq)

    def mainloop(self):
        if self.debug:
            '''
            a = self.cpu.registers["A"].get()
            f = self.cpu.flags.get()
            b = self.cpu.registers["B"].get()
            c = self.cpu.registers["C"].get()
            d = self.cpu.registers["D"].get()
            e = self.cpu.registers["E"].get()
            h = self.cpu.registers["H"].get()
            l = self.cpu.registers["L"].get()
            sp = self.cpu.registers["SP"].get()
            pc = self.cpu.registers["PC"].get()
            pcmem = self.memory.read(pc, 4)
            ime = self.cpu.ime
            intf = self.io.intf
            div = self.io.timer.div
            tima = self.io.timer.tima
            en = self.io.timer.tac & 0b100
            halt_bug = self.cpu.halt_bug
            ime = self.cpu.ime
            freq = self.io.timer.get_timer_freq()
            string = f"A:{self.hexformat(a)} F:{self.hexformat(f)} B:{self.hexformat(b)} C:{self.hexformat(c)} D:{self.hexformat(d)} E:{self.hexformat(e)} H:{self.hexformat(h)} L:{self.hexformat(l)} SP:{self.hexformat2b(sp)} PC:{self.hexformat2b(pc)} PCMEM:"
            for i,byte in enumerate(pcmem):
                if i > 0:
                    string += f",{self.hexformat(byte)}"
                else:
                    string += f"{self.hexformat(byte)}"
            string += f"IME: {ime} HALT_BUG: {halt_bug} TIMA: {tima} DIV: {div} TIMER_EN: {en} TIMER_FREQ: {freq} t-cycles/t"
            print(string)
            '''
            pc = self.cpu.pc.get()
            if self.pc_last != pc:
                if self.syms:
                    bank = self.mbc.bank if (pc >= 0x4000) and (isinstance(self.mbc, BankedMBC)) else 0
                    if not self.syms.is_same_symbol(bank, pc, self.pc_last):
                        print(f"EXCECUTION CHANGED TO: {pc:04X} ({self.syms.get_symbol(bank, pc)})")
                else:
                    print(f"PC CHANGED TO: {pc:04X}")
            self.pc_last = pc
        cycles = self.cpu.check_interrupt()
        instr = self.cpu.fetch()

        cycles += 4
        self.stepIo(cycles)

        c =  self.cpu.execute(instr) - 4
        self.stepIo(c)

        cycles += c
