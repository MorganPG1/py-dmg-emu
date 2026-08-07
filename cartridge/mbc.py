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
        #raise Exception(f"WRITE TO ROM AT {hex(offset)}")
        return

class MBC1(MemoryRegion):
    '''
    2MB of banked ROM
    '''
    #FFR: this code was written at like 3 AM so like a lot of the code it should be reviewed or rewritten if necessary
    #somehow this works and i have no clue how
    #this code is held together by hopes and dreams
    def __init__(self, data:bytearray) -> None:
        self.data = data
        self.bank0 = data[:0x4000]
        self.bank = 1

    def read(self, offset: int, count: int) -> bytearray:
        data = bytearray()

        for addr in range(offset,offset+count):
            if addr < 0x4000:
                data.append(self.bank0[addr])
            else:
                phy_addr = (self.bank * 0x4000) + (addr - 0x4000)
                if phy_addr < len(self.data):
                    data.append(self.data[phy_addr])
                else:
                    data.append(0x00)

        return data
    def write(self, offset: int, buffer: bytearray) -> None:
        if 0x2000 <= offset <= 0x3fff:
            if (buffer[0] & 0x1F) == 0:
                self.bank = 1
            else:
                self.bank = buffer[0] & 0x1F