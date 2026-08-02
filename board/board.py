'''
DMG Gameboy Emulator Project - MorganPG

board/board.py

A 'motherboard' like structure, allows all major components to interact with each other
'''
from memory.memory import MemoryController, MemoryRegion
from memory.ram import RAM
from cpu.cpu import CPU

class Motherboard():
    def __init__(self, romfile:str) -> None:


        ram = RAM(0x2000)
        memory_map:dict[tuple[int,int], MemoryRegion] = {
            (0xC000, 0xDFFF): ram,
            (0xE000, 0xFDFF): ram,
        }

        self.memory:MemoryController = MemoryController(memory_map)
        self.cpu = CPU(self)
        
        pass

    def mainloop(self):
        pass