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
import numpy as np
import time
import pygame
SCREEN_W = 160
SCREEN_H = 144

class VRAM(MemoryRegion):
    def __init__(self) -> None:
        self.b = bytearray(0x1000)

    def read(self, offset: int, count: int, is_ppu:bool=False) -> bytearray:
        #TODO: implement VRAM inaccessibility
        return self.b[offset:offset+count]
    
    def write(self, offset: int, buffer: bytearray, is_ppu:bool=False) -> None:
        #TODO: implement VRAM inaccessibility
        self.b[offset:offset+len(buffer)] = buffer
class OAM(MemoryRegion):
    def __init__(self) -> None:
        self.b = bytearray(0xA0)

    def read(self, offset: int, count: int, is_ppu:bool=False) -> bytearray:
        #TODO: implement OAM inaccessibility
        return self.b[offset:offset+count]
    
    def write(self, offset: int, buffer: bytearray, is_ppu:bool=False) -> None:
        #TODO: implement OAM inaccessibility
        self.b[offset:offset+len(buffer)] = buffer
class PPU():
    def __init__(self) -> None:
        pygame.init()

        self.fb = np.zeros((SCREEN_H, SCREEN_W, 3), dtype=np.uint8)
        self.pg = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.oam = OAM()
        self.vram = VRAM()

        self.lcdc = 0x80
        self.ly = 0
        self.lyc = 0
        self.stat = 0
        self.cycles = 0
        self.mode = -1 #-1 = disabled, 2 = search for OBJ, 3 = send pixels, 0 = wait for scanline, 1 = wait for frame
        self.objs_on_line = []
        self.mode2_handler_run= False
        self.mode3_handler_run= False
        self.frame_rendered = False
        self.last_vblank = 0
        #2 = 80 T-Cycles 
        #3 = 172 T-Cycles (technically can vary but fixed is easier)
        #0 = 204 T-Cycles (again can vary but easier to fix)
        #1 = 4560 T-Cycles
        pass

    def scan(self, obj_size, obj_en):
        if not obj_en: return

        oam_d = self.oam.read(0, 0xA0, True)
        for obj in range(40):
            start_addr = 4 * obj
            y = oam_d[start_addr]
            x = oam_d[start_addr + 1]
            ind = oam_d[start_addr + 1]
            attr = oam_d[start_addr + 1]
            if (x!=0) or (y!=0) or (ind!=0) or (attr!=0):
                print(y,x,ind,attr)
            start_line = y - 16
            if obj_size: #8x16
                if start_line <= self.ly < start_line + 16:
                    self.objs_on_line.append((x, y, ind, attr))
            else:
                if start_line <= self.ly < start_line + 8:
                    self.objs_on_line.append((x, y, ind, attr))

        if len(self.objs_on_line) > 0:
            print(self.objs_on_line)
        pass

    def render_scanline(self):
        pass

    def step(self, cycles:int) -> int:
        lcd_en = self.lcdc & 0x80
        window_en = self.lcdc & 0x20
        bg_data_area = self.lcdc & 0x10
        bg_tile_map_area = self.lcdc & 0x8
        obj_size = self.lcdc & 0x4
        obj_en = self.lcdc & 0x2
        bg_en = self.lcdc & 0x1
        irq = -1

        #if window_en:
            #print("ROM enables window which is currently not implemented")
        if lcd_en:
            self.mode = 2 if self.mode == -1 else self.mode #go to OAM scan if switching from disabled to enabled
            for cycle in range(cycles):
                self.cycles += 1
                match self.mode:
                    case 2:
                        if not self.mode2_handler_run:
                            self.scan(obj_size, obj_en)
                        if self.cycles >= 80:
                            self.cycles = 0
                            self.mode = 3
                            self.mode2_handler_run = False
                    case 3:
                        if not self.mode3_handler_run:
                            self.render_scanline()
                        if self.cycles >= 172:
                            self.cycles = 0
                            self.mode = 0
                            self.mode3_handler_run = False
                    case 0:
                        if self.cycles >= 204:
                            self.cycles = 0
                            self.ly += 1
                            if self.ly < 144:
                                self.mode = 2
                            else:
                                self.mode = 1
                                irq = 0
                    case 1:
                        if self.cycles >= 456:
                            self.cycles = 0
                            self.ly += 1
                        if self.ly > 153:
                            c = time.perf_counter()
                            #print(f"time since last vblank: {c-self.last_vblank}")
                            self.last_vblank = c
                            self.ly = 0
                            self.mode = 2
                            self.objs_on_line = []
                            pygame.display.update()
        else:
            self.cycles = 0
            self.ly = 0
            self.mode = -1
        return irq