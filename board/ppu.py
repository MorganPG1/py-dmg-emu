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

# Imports 
from memory.memory import MemoryRegion
import numpy as np
import time
import pygame

# Constants
SCREEN_W = 160
SCREEN_H = 144
PALETTE = (
    (255,255,255),
    (211,211,211),
    (169,169,169),
    (0,0,0),
)
KEYMAP_ACTION = {
    pygame.K_z: 1,
    pygame.K_x: 2,
    pygame.K_RETURN: 4,
    pygame.K_RSHIFT: 8,
}

KEYMAP_DIRECTION = {
    pygame.K_RIGHT: 1,
    pygame.K_LEFT: 2,
    pygame.K_UP: 4,
    pygame.K_DOWN: 8,
}


class VRAM(MemoryRegion):
    def __init__(self) -> None:
        self.b = bytearray(0x2000)

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
        self.pg = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED | pygame.RESIZABLE)
        self.oam = OAM()
        self.vram = VRAM()

        self.joyp_select = 0x30
        self.lcdc = 0x00
        self.ly = 0
        self.lyc = 0
        self.stat = 0
        self.cycles = 0
        self.scx = 0
        self.scy = 0
        self.wy = 0
        self.wx = 0
        self.mode = -1 #-1 = disabled, 2 = search for OBJ, 3 = send pixels, 0 = wait for scanline, 1 = wait for frame
        self.objs_on_line = []
        self.frame_rendered = False
        self.last_vblank = 0
        #2 = 80 T-Cycles 
        #3 = 172 T-Cycles (technically can vary but fixed is easier)
        #0 = 204 T-Cycles (again can vary but easier to fix)
        #1 = 4560 T-Cycles
        pass
    def poll_joyp(self): #yes joypad is implemented inside PPU, its the easiest way to do it even though it looks a bit stupid
        keys = pygame.key.get_pressed()
        normal = 0
        dir = 0
        for k, bit in KEYMAP_ACTION.items():
            if keys[k]:
                normal |= bit

        for k, bit in KEYMAP_DIRECTION.items():
            if keys[k]:
                dir |= bit

        selected = (self.joyp_select >> 4) & 0b11

        low = 0
        high = (self.joyp_select & 0x30)
        match selected:
            case 0:
                low = (normal & dir) 
            case 1:
                low = (normal) 
            case 2:
                low = (dir)
            case 3:
                low = (0xF)
        return ((~low) | high) & 0xFF
    def scan(self, obj_size, obj_en):
        if not obj_en: return

        oam_d = self.oam.read(0, 0xA0, True)
        for obj in range(40):
            start_addr = 4 * obj
            y = oam_d[start_addr]
            x = oam_d[start_addr + 1]
            ind = oam_d[start_addr + 2]
            attr = oam_d[start_addr + 3]
            start_line = y - 16
            if obj_size: #8x16
                if (start_line) <= self.ly < (start_line + 16):
                    self.objs_on_line.append((obj_size,x, y, ind, attr))
            else:
                if (start_line) <= self.ly < (start_line + 8):
                    self.objs_on_line.append((obj_size,x, y, ind, attr))

            if len(self.objs_on_line) >= 10:
                break

        pass

    def get_pixel_2bpp(self, vram:bytearray, tile_addr:int, row:int, column:int, h_flip:bool=False):
        b1 = vram[tile_addr + (row * 2)]
        b2 = vram[tile_addr + (row * 2) + 1]

        bitpos = column if h_flip else 7 - column

        bit0 = (b1 >> bitpos) & 0x01
        bit1 = (b2 >> bitpos) & 0x01

        pxl = (bit1 << 1) | bit0
        return pxl

    def render_scanline(self, bg_en, bg_tile_map_area, data_area, window_en, window_tile_map_area):
        tm = 0x1C00 if bg_tile_map_area else 0x1800
        window_tm = 0x1C00 if window_tile_map_area else 0x1800
        line = self.fb[self.ly]
        vram_data = self.vram.read(0, 0x2000, True)        
        bg_y = (self.ly + self.scy) & 0xFF
        wind_y = (self.ly - self.wy) & 0xFF
        row = bg_y % 8
        wrow = wind_y % 8
        for i in range(160):
            if bg_en:
                bg_x = (i + self.scx) & 0xFF

                offset = tm + ((bg_y // 8) * 32) + (bg_x // 8) 
                ind = vram_data[offset]

                if data_area:
                    tile_addr = ind * 16
                else:
                    if ind > 127 : ind -= 256
                    tile_addr = 0x1000 + (ind * 16)

                column = bg_x % 8

                b1 = vram_data[tile_addr + (row * 2)]
                b2 = vram_data[tile_addr + (row * 2) + 1]

                bitpos = 7 - column

                bit0 = (b1 >> bitpos) & 0x01
                bit1 = (b2 >> bitpos) & 0x01

                pxl = (bit1 << 1) | bit0
                line[i] = PALETTE[pxl]
            else:
                line[i] = PALETTE[0]

            if window_en and bg_en and (i >= self.wx-7) and (self.ly >= self.wy):
                wind_x = (i - (self.wx-7)) & 0xFF
                offset = window_tm + ((wind_y // 8) * 32) + (wind_x // 8) 
                ind = vram_data[offset]

                if data_area:
                    tile_addr = ind * 16
                else:
                    if ind > 127 : ind -= 256
                    tile_addr = 0x1000 + (ind * 16)

                column = wind_x % 8

                b1 = vram_data[tile_addr + (wrow * 2)]
                b2 = vram_data[tile_addr + (wrow * 2) + 1]

                bitpos = 7 - column

                bit0 = (b1 >> bitpos) & 0x01
                bit1 = (b2 >> bitpos) & 0x01

                pxl = (bit1 << 1) | bit0
                line[i] = PALETTE[pxl]
        for obj in self.objs_on_line:
            is_16px = obj[0]
            x = obj[1]-8
            y = obj[2]-16
            ind = obj[3] * 16            
            attr = obj[4]
            bank = attr & 0b1000
            priority = attr & 0b10000000
            x_flip = attr & 0b100000
            y_flip = attr & 0b1000000
            h = 16 if is_16px else 8
            if bank: ind += 0x400
            row = self.ly-y

            if y_flip: row = (h - 1) - row
            
            for tx in range(8):
                scr_x = x + tx

                if scr_x < 0 or scr_x >= 160:
                    continue

                if not priority or not (self.fb[self.ly,scr_x].all() == 255):
                    pxl = self.get_pixel_2bpp(vram_data, ind, row, tx, x_flip)
                    if pxl == 0:
                        continue
                    self.fb[self.ly, scr_x] = PALETTE[pxl]
                                
                
                #print(ind, row, column)
                
        pass

    def step(self, cycles:int) -> list[int]:
        
        lcd_en = self.lcdc & 0x80
        window_tile_map_area = self.lcdc & 0x40
        window_en = self.lcdc & 0x20
        bg_data_area = self.lcdc & 0x10
        bg_tile_map_area = self.lcdc & 0x8
        obj_size = self.lcdc & 0x4
        obj_en = self.lcdc & 0x2
        bg_en = self.lcdc & 0x1
        irq = []

        #if window_en:
            #print("ROM enables window which is currently not implemented")
        if lcd_en:
            self.mode = 2 if self.mode == -1 else self.mode #go to OAM scan if switching from disabled to enabled
            for cycle in range(cycles):
                self.cycles += 1
                match self.mode:
                    case 2:
                        if self.cycles == 1:
                            self.objs_on_line = []
                            self.scan(obj_size, obj_en)
                        if self.cycles >= 80:
                            self.cycles = 0
                            self.mode = 3
                    case 3:
                        if self.cycles == 1:
                            self.render_scanline(bg_en, bg_tile_map_area, bg_data_area, window_en, window_tile_map_area)
                        if self.cycles >= 172:
                            self.cycles = 0
                            self.mode = 0
                    case 0:
                        if self.cycles >= 204:
                            self.cycles = 0
                            self.ly += 1
                            if self.ly < 144:
                                self.mode = 2
                            else:
                                self.mode = 1
                                irq.append(0)
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

                            surface_array = np.transpose(self.fb, (1, 0, 2))
                            pygame.surfarray.blit_array(self.pg, surface_array)
                            pygame.display.update()

                            events = pygame.event.get()
                            for event in events:
                                if event.type == pygame.QUIT:
                                    exit()
                                elif event.type == pygame.KEYDOWN:
                                    if event.key in KEYMAP_ACTION or event.key in KEYMAP_DIRECTION:
                                        irq.append(4)
                            self.fb.fill(0)
        else:
            if self.mode != -1:
                self.fb.fill(255)
                surface_array = np.transpose(self.fb, (1, 0, 2))
                pygame.surfarray.blit_array(self.pg, surface_array)
            self.cycles = 0
            self.ly = 0
            self.mode = -1
            
        return irq