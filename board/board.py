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
from debug.serial import Serial
class Motherboard():
    def __init__(self, romfile:str) -> None:
        self.pc_last = 0

        cart = Cart(romfile)

        ram = RAM(0x2000)
        hram = RAM(128)
        vram = RAM(0x2000)
        eram = RAM(0x2000)
        serial = Serial()
        memory_map:dict[tuple[int,int], MemoryRegion] = {
            (0x0000, 0x8000): cart.getMBC(),
            (0x8000, 0xA000): vram,
            (0xA000, 0xC000): eram,
            (0xC000, 0xE000): ram,
            (0xE000, 0xFE00): ram,
            (0xFF00, 0xFF80): serial,
            (0xFF80, 0xFFFF): hram,
        }

        self.memory:MemoryController = MemoryController(memory_map)
        self.cpu = CPU(self)

        pass

    def hexformat(self, val:int):
        return hex(val)[2:].rjust(2, "0").upper()
    def hexformat2b(self,val:int):
        return hex(val)[2:].rjust(4, "0").upper()
    def mainloop(self, debug:bool = False):
        if debug:
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

            string = f"A:{self.hexformat(a)} F:{self.hexformat(f)} B:{self.hexformat(b)} C:{self.hexformat(c)} D:{self.hexformat(d)} E:{self.hexformat(e)} H:{self.hexformat(h)} L:{self.hexformat(l)} SP:{self.hexformat2b(sp)} PC:{self.hexformat2b(pc)} PCMEM:"
            for i,byte in enumerate(pcmem):
                if i > 0:
                    string += f",{self.hexformat(byte)}"
                else:
                    string += f"{self.hexformat(byte)}"
            print(string)
        cycles = self.cpu.step()

        
        pass