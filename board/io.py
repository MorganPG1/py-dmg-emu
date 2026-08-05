from __future__ import annotations
from memory.memory import MemoryRegion
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board.board import Motherboard

class Timer():
    def __init__(self) -> None:
        self.tima = 0
        self.div = 0
        self.tma = 0
        self.tac = 0
        self.cycles = 0
        pass
    def get_timer_freq(self) -> int:
        frq = self.tac & 0b11
        match frq:
            case 0:
                return 1024
            case 1:
                return 16
            case 2:
                return 64
            case 3:
                return 256
        return 1024
    def inc_div(self):
        self.div = (self.div + 1) & 0xFF
    def inc_timer(self) -> bool:
        self.tima += 1
        if self.tima > 0xFF:
            self.tima = self.tma
            return True
        return False
    
    def step(self, cycles) -> bool:
        #Div: every 256 T cycles
        total_c = self.cycles
        cycles_for_t = self.get_timer_freq() 
        irq = False
        for c in range(cycles):
            total_c += 1
            if (total_c % 256) == 0:
                self.inc_div()
            if (total_c % cycles_for_t) == 0 and (self.tac & 0b100):
                irq = True if self.inc_timer() else irq

        self.cycles = total_c
        return irq
    
class IO(MemoryRegion):
    def __init__(self, board:Motherboard, debug:bool=False) -> None:
        self.board = board
        self.debug = debug
        self.timer = Timer()
        self.buffer = 0
        self.read_buff = bytearray([
            # $FF00 - $FF0F: System & Timers
            0xCF, 0x00, 0x7E, 0xFF, 0xAB, 0x00, 0x00, 0xF8,
            0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xE1,

            # $FF10 - $FF1F: Audio (NR10 - NR24)
            0x80, 0xBF, 0xF3, 0xFF, 0xBF, 0xFF, 0x3F, 0x00,
            0xFF, 0xBF, 0x7F, 0xFF, 0x9F, 0xFF, 0xBF, 0xFF,

            # $FF20 - $FF2F: Audio (NR30 - NR52) & Unused
            0xFF, 0x00, 0x00, 0xBF, 0x77, 0xF3, 0xF1, 0xFF,
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
        self.div = 0
        self.tima = 0
        self.timer_mod = 0
        self.cycles_per_inc = 256
        self.timer_enabled = 0

        self.cycle_timer0 = 0
        self.cycle_timer1 = 0
        self.cycle_timer2 = 0

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
                    case 0x01:
                        self.buffer = val
                    case 0x02:
                        if val & 0x80 and not self.debug:
                            print(chr(self.buffer), end="", flush=True)
                    case 0x04:
                        self.timer.div = 0
                    case 0x05:
                        self.timer.tima = 0
                    case 0x06:
                        self.timer.tma = val
                    case 0x07:
                        self.timer.tac = val
                    case 0x0F:
                        cpu.intf = val
                    case 0x40:
                        ppu.lcdc = val
                    case 0x41:
                        ppu.stat = val
                    case 0x45:
                        ppu.lyc = val
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