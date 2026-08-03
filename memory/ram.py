'''
DMG Gameboy Emulator Project - MorganPG

memory/ram.py:

RAM Implementation using MemoryRegion base class
'''

from memory.memory import MemoryRegion

class RAM(MemoryRegion):
    def __init__(self, size:int) -> None:
        if not isinstance(size, int):
            raise ValueError("Size must be an integer")
        
        self.memory = bytearray([0xFF]*size)

    def read(self, offset: int, count: int) -> bytearray:
        #Validation
        if (offset + count) > len(self.memory):
            raise ValueError(f"End address (0x{hex(offset+count)}) of read ({count} byte(s) from 0x{hex(offset)}) exceeds end of RAM buffer")
        elif (offset < 0) or (count < 0):
            raise ValueError("Offset and count must be positive")      
        elif not (isinstance(offset,int) and isinstance(count, int)):
            raise ValueError("Offset and count must be integers")
      
        return self.memory[offset:offset+count]
    
    def write(self, offset: int, buffer: bytearray) -> None:
        c = len(buffer)

        #More validation
        if (offset + c) > len(self.memory):
            raise ValueError(f"End address ({hex(offset+c)}) of write ({c} byte(s) to {hex(offset)}) exceeds end of RAM buffer")
        elif offset < 0:
            raise ValueError("Offset must be positive")        
        elif not isinstance(offset, int):
            raise ValueError("Offset must be an integer")
        
        self.memory[offset:offset+c] = buffer
