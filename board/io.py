from __future__ import annotations
from memory.memory import MemoryRegion
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board.board import Motherboard

BIT_INDEXES = (
    9, #FREQ 0 - bit 9 high (1024 T-Cycles)
    3, #FREQ 1 - bit 3 high (16 T-Cycles)
    5, #FREQ 2 - bit 5 high (64 T-Cycles)
    7  #FREQ 3 - bit 7 high (256 T-Cycles)
)
class Timer():
    def __init__(self) -> None:
        self.tima = 0
        self.div = 0
        self.tac = 0
        self.tima = 0
        self.tma = 0

        self.master_counter = 0
        self.prev_signal = 0

    def timer_tick(self):
        self.tima += 1
        if self.tima > 0xFF:
            self.tima = self.tma
            return True
        return False
    def step(self, cycles) -> bool:
        irq = False
        for c in range(cycles):
            mc = (self.master_counter + 1) & 0xFFFF
            self.div = (mc >> 8) & 0xFF

            en = (self.tac >> 2) & 0b1
            freq = (self.tac) & 0b11

            bit_ind = BIT_INDEXES[freq]
            bit = (self.master_counter >> bit_ind) & 0b1

            if (not bit) and (self.prev_signal) and (en):
                irq = True if self.timer_tick() else irq

            self.prev_signal = bit
            self.master_counter = mc

        return irq            
    def get_timer_freq(self):
        match (self.tac & 0b11):
            case 0:
                return 1024
            case 1:
                return 16
            case 2:
                return 64
            case 3:
                return 256
        
    
class IO(MemoryRegion):
    def __init__(self, board:Motherboard, debug:bool=False) -> None:
        self.board = board
        self.debug = debug
        self.timer = Timer()
        self.buffer = 0

        #Before someone gets mad, yes this bytearray is AI generated
        #I feel it is a fair use of AI because it is just a bytearray that stores placeholders for IO registers
        #But oh well someone will probably use this to say the entire project is AI
        #(trust me not even ai can write code as bad as half of this project i really need to clean it up)
        self.read_buff = bytearray([
            # $FF00 - $FF0F: System & Timers
            0xCF, 0x00, 0x7E, 0xFF, 0xAB, 0x00, 0x00, 0xF8,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xE1,

            # $FF10 - $FF1F: Audio (NR10 - NR24)
            0x80, 0xBF, 0xF3, 0xFF, 0xBF, 0xFF, 0x3F, 0x00,
            0xFF, 0xBF, 0x7F, 0xFF, 0x9F, 0xFF, 0xBF, 0xFF,

            # $FF20 - $FF2F: Audio (NR30 - NR52) & Unused
            0xFF, 0x00, 0x00, 0xBF, 0x77, 0xF3, 0x80, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,

            # $FF30 - $FF3F: Wave Pattern RAM
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,

            # $FF40 - $FF4F: PPU / LCD Registers
            0x91, 0x85, 0x00, 0x00, 0x90, 0x00, 0xFF, 0xFC,
            0xFF, 0xFF, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,

            # $FF50 - $FF5F: Boot ROM Disable ($FF50 = 0x01) & CGB / Unmapped
            0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,

            # $FF60 - $FF6F: Unmapped I/O
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,

            # $FF70 - $FF7F: Unmapped I/O
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
        ])
        self.hram = bytearray([0xFF]*0x7F)
        self.intf:int = 0
    def write(self, offset: int, buffer: bytearray) -> None:
        count = len(buffer)
        cpu = self.board.cpu
        ppu = self.board.ppu
        for addr in range(offset, offset+count):
            val = buffer.pop(0)
            if (addr & 0x80) and addr != 0xFF:
                self.hram[addr - 0x80] = val
            else:
                match addr:
                    case 0x00:
                        ppu.joyp_select = val & 0x30
                    case 0x01:
                        self.buffer = val
                    case 0x02:
                        if val & 0x80 and not self.debug:
                            print(chr(self.buffer), end="", flush=True)
                    case 0x04:
                        self.timer.master_counter = 0
                    case 0x05:
                        self.timer.tima = val
                    case 0x06:
                        self.timer.tma = val
                    case 0x07:
                        self.timer.tac = val
                    case 0x0F:
                        cpu.intf = val | 0xE0
                    case 0x40:
                        ppu.lcdc = val
                    case 0x41:
                        ppu.stat = val
                    case 0x42:
                        ppu.scy = val
                    case 0x43:
                        ppu.scx = val
                    case 0x45:
                        ppu.lyc = val
                    case 0x46:
                        addr = (val << 8) & 0xDF00
                        data = self.board.memory.read(addr, 0xA0)
                        self.board.ppu.oam.write(0, data, True)
                    case 0xFF:
                        cpu.ie = val

    def read(self, offset: int, count: int) -> bytearray:
        buff = bytearray()
        cpu = self.board.cpu
        ppu = self.board.ppu
        for addr in range(offset, offset+count):
            if (addr & 0x80) and addr != 0xFF:
                buff.append(self.hram[addr - 0x80])
            elif addr != 0xFF:
                match addr:
                    case 0x00:
                        buff.append(ppu.poll_joyp())
                    case 0x04:
                        buff.append(self.timer.div)
                    case 0x05:
                        buff.append(self.timer.tima)
                    case 0x06:
                        buff.append(self.timer.tma)
                    case 0x07:
                        buff.append(self.timer.tac)
                    case 0x0F:
                        buff.append(cpu.intf)
                    case 0x40:
                        buff.append(ppu.lcdc)
                    case 0x41:
                        buff.append(ppu.stat)
                    case 0x44:
                        buff.append(ppu.ly)
                    case 0x45:
                        buff.append(ppu.lyc)
                    case _:
                        buff.append(self.read_buff[addr])
            else:
                buff.append(cpu.ie)

        return buff

    def step(self, cycles) -> bool:
        return self.timer.step(cycles)