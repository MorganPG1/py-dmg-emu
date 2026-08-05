'''
DMG Gameboy Emulator Project - MorganPG

board/ppu.py

The main graphical processor on the DMG. It handles everything displayed on screen.
See:

https://gbdev.io/pandocs/Graphics.html
https://gbdev.io/pandocs/Tile_Data.html
https://gbdev.io/pandocs/Tile_Maps.html
https://gbdev.io/pandocs/OAM.html
https://gbdev.io/pandocs/OAM_DMA_Transfer.html <- technically i could just make this instant even though it wont be accurate
https://gbdev.io/pandocs/Window.html <- probably i'll leave this for later it seems very confusing
https://gbdev.io/pandocs/LCDC.html
https://gbdev.io/pandocs/STAT.html
https://gbdev.io/pandocs/Scrolling.html
https://gbdev.io/pandocs/Palettes.html <- might be CGB only i'm not sure
https://gbdev.io/pandocs/Rendering.html
https://gbdev.io/pandocs/pixel_fifo.html
'''
# 05/08/26 20:36: i have not mentally prepared myself for this but procrastination is never going to help
# here we go i guess, worst case scenario i have to delete it all and restart like with the interrupts

from memory.memory import MemoryRegion

class VRAM(MemoryRegion):
    def __init__(self) -> None:
        super().__init__()

class OAM(MemoryRegion):
    def __init__(self) -> None:
        super().__init__()

class PPU():
    def __init__(self) -> None:
        self.lcdc = 0
        self.ly = 0
        self.lyc = 0
        self.stat = 0
        self.mode = -1 #-1 = disabled, 2 = search for OBJ, 3 = send pixels, 0 = wait for scanline, 1 = wait for frame
        #2 = 80 T-Cycles 
        #3 = 172 T-Cycles (technically can vary but fixed is easier)
        #0 = 204 T-Cycles (again can vary but easier to fix)
        #1 = 4560 T-Cycles
        pass

    def step(self, cycles:int):
        pass