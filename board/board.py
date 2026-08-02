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
class Motherboard():
    def __init__(self, romfile:str) -> None:
        self.pc_last = 0

        cart = Cart(romfile)

        ram = RAM(0x2000)
        hram = RAM(126)
        vram = RAM(0x2000)
        memory_map:dict[tuple[int,int], MemoryRegion] = {
            (0x0000, 0x8000): cart.getMBC(),
            (0x8000, 0xA000): vram,
            (0xC000, 0xE000): ram,
            (0xE000, 0xFE00): ram,
            (0xFF80, 0xFFFF): hram,
        }

        self.memory:MemoryController = MemoryController(memory_map)
        self.cpu = CPU(self)

        pass

    def mainloop(self, debug:bool = False):
        if debug:
            pc = self.cpu.registers["PC"].get()
            af = self.cpu.registers["AF"].get()
            hl = self.cpu.registers["HL"].get()
            if pc != self.pc_last:
                print(f"PC: {hex(pc)}, AF: {hex(af)}, HL:{hex(hl)}")
            self.pc_last = pc
        cycles = self.cpu.step()

        
        pass