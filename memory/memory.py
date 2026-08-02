'''
DMG Gameboy Emulator Project - MorganPG

memory/memory.py

Memory-related classes
'''
from collections.abc import Iterable

class MemoryRegion():
    '''
    Base class for a region in memory space
    '''
    def __init__(self) -> None:

        pass

    def read(self, offset:int, count:int) -> bytearray:
        '''
        Reads data from the MemoryRegion

        :param self: The MemoryRegion object
        :param offset: The base address to begin reading from
        :param count: The number of bytes to read
        :type offset: int
        :type count: int
        :return: The data read from the MemoryRegion
        :rtype: bytearray
        '''
        pass

    def write(self, offset:int, buffer:bytearray) -> None:
        '''
        Writes data to the MemoryRegion

        :param self: The MemoryRegion object
        :param offset: The base address to begin writing to
        :param buffer: The data to write
        :type offset: int
        :type buffer: bytearray
        '''
        pass

class MemoryController():
    '''
    A controller of memory regions\n
    Allows for reading from the entire memory space
    '''
    def __init__(self, memoryMap:dict[tuple[int, int], MemoryRegion]) -> None:
        self.mem_regions:dict[tuple[int,int], MemoryRegion] = memoryMap

        pass
    
    def read(self, offset:int, count:int) -> bytearray:
        '''
        Reads data from memory

        :param self: The MemoryController object
        :param offset: The base address to start reading from
        :type offset: int
        :param count: The number of bytes to read
        :type count: int
        :return: The data read from memory
        :rtype: bytearray
        '''
        curr_addr = offset
        remaining = count
        data = bytearray()

        while remaining > 0:
            for mapping, mem_region in self.mem_regions.items():
                start = mapping[0]
                end = mapping[1]

                if start <= curr_addr < end:
                    n = min(remaining, end - curr_addr)
                    b = mem_region.read(curr_addr-start, n)

                    data.extend(b)
                    
                    curr_addr += n
                    remaining -= n
                    break
            else:
                raise ValueError(f"Unmapped address during read from {hex(curr_addr)}")
    
        return data

    def write(self, offset:int, buffer:bytearray) -> None:
        '''
        Writes data to memory

        :param self: The MemoryController object
        :param offset: The base address to start writing to
        :type offset: int
        :param buffer: The data to write
        :type buffer: bytearray
        '''

        curr_addr = offset
        
        b = bytearray()
        b.extend(buffer)

        while len(b) > 0:
            for mapping, mem_region in self.mem_regions.items():
                start = mapping[0]
                end = mapping[1]

                if start <= curr_addr < end:
                    n = min(len(b), end - curr_addr)
                    mem_region.write(curr_addr - start, b[:n])
                    b = b[n:]

                    curr_addr += n
                    break
            else:
                raise ValueError(f"Unmapped address during write to {hex(curr_addr)}")
    