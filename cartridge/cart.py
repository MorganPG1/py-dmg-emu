'''
DMG Gameboy Emulator Project - MorganPG

cartridge/cart.py

MBC (Memory Bank Controller) emulation
See: 
https://gbdev.io/pandocs/The_Cartridge_Header.html
'''
from memory.memory import MemoryRegion
from cartridge.mbc import *

MBC_CONTROLLERS = {
    0x0: MBC0,
    0x8: MBC0,
}

class Cart():
    def __init__(self, romfile:str) -> None:
        rom = bytearray(open(romfile, "rb").read())

        self.rom = rom
        self.title = self.rom[0x134:0x13F].decode()

        mbc = self.rom[0x147]

        if mbc in MBC_CONTROLLERS:
            self.mbc = MBC_CONTROLLERS[mbc](self.rom)
        else:
            raise NotImplementedError(f"MBC ({hex(mbc)}) unknown or not implemented. Load a different ROM and try again")

    def getMBC(self) -> MemoryRegion:
        return self.mbc