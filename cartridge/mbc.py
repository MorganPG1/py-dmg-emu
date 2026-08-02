'''
DMG Gameboy Emulator Project - MorganPG

cartridge/mbc.py

MBC (Memory Bank Controller) emulation
See: 
https://gbdev.io/pandocs/MBCs.html
'''
from memory.memory import MemoryRegion

class MBC0(MemoryRegion):
    '''
    No MBC, raw connection to unbanked rom between 0x0000 and 0x7FFF
    '''
    def __init__(self, data:bytearray) -> None:
        self.buffer = data

    def read(self, offset: int, count: int) -> bytearray:
        return self.buffer[offset:offset+count]

    def write(self, offset: int, buffer: bytearray) -> None:
        raise Exception(f"WRITE TO ROM AT {hex(offset)}")
        return