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

class Motherboard():
    def __init__(self, romfile:str) -> None:

        cart = Cart(romfile)

        ram = RAM(0x2000)
        hram = RAM(126)
        memory_map:dict[tuple[int,int], MemoryRegion] = {
            (0x0000, 0x7FFF): cart.getMBC(),
            (0xC000, 0xDFFF): ram,
            (0xE000, 0xFDFF): ram,
            (0xFF80, 0xFFFE): hram,
        }

        self.memory:MemoryController = MemoryController(memory_map)
        self.cpu = CPU(self)

        pass

    def mainloop(self):
        cycles = self.cpu.step()
        pass