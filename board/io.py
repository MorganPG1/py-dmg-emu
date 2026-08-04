from __future__ import annotations
from memory.memory import MemoryRegion
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board.board import Motherboard

class IO(MemoryRegion):
    def __init__(self, board:Motherboard, debug:bool=False) -> None:
        self.board = board
        self.debug = debug
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
        for addr in range(offset, offset+count):
            if (addr & 0x80) and addr != 0xFF:
                self.hram[addr - 0x80] = buffer.pop(0)
            else:
                match addr:
                    case 0x01:
                        self.buffer = buffer.pop(0)
                    case 0x02:
                        v = buffer.pop(0)
                        if v & 0x80 and not self.debug:
                            print(chr(self.buffer), end="", flush=True)
                            
                    case 0x0F:
                        cpu.intf = buffer.pop(0)
                    case 0xFF:
                        cpu.ie = buffer.pop(0)

    def read(self, offset: int, count: int) -> bytearray:
        buff = bytearray()
        cpu = self.board.cpu
        for addr in range(offset, offset+count):
            if (addr & 0x80) and addr != 0xFF:
                buff.append(self.hram[addr - 0x80])
            elif addr != 0xFF:
                match addr:
                    case 0x0F:
                        buff.append(cpu.intf)
                    case _:
                        buff.append(self.read_buff[addr])
            else:
                buff.append(cpu.ie)

        return buff
        