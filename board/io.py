from memory.memory import MemoryRegion
class IE(MemoryRegion):
    def __init__(self) -> None:
        self.state = 0
    def read(self, offset: int, count: int) -> bytearray:
        return bytearray([self.state])
    def write(self, offset: int, buffer: bytearray) -> None:
        self.state = buffer[0]
class IO(MemoryRegion):
    def __init__(self) -> None:
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
        self.intf:int = 0
        self.ie = IE()
        self.div = 0
        self.tima = 0
        self.timer_mod = 0
        self.cycles_per_inc = 256
        self.timer_enabled = 0

        self.cycle_timer0 = 0
        self.cycle_timer1 = 0
        self.cycle_timer2 = 0
    def write(self, offset: int, buffer: bytearray) -> None:
        if offset == 0x01:
            self.buffer = buffer[0]
        if offset == 0x02 and buffer[0] == 0x81:
            #print(chr(self.buffer), end="", flush=True)
            #print(f"SERIAL WRITE: {hex(self.buffer)}")
            pass

        match offset:
            case 0x04:
                self.div = 0
            case 0x06:
                self.timer_mod = buffer[0]
            case 0x07:
                val = buffer[0]
                clock = val & 0b11
                self.timer_enabled = (val >> 2) & 1
                match clock:
                    case 0:
                        self.cycles_per_inc = 1024
                    case 1:
                        self.cycles_per_inc = 16
                    case 2:
                        self.cycles_per_inc = 64
                    case 3:
                        self.cycles_per_inc = 256
            case 0xF:
                self.intf = buffer[0]
    def read(self, offset: int, count: int) -> bytearray:
        data = bytearray()
        for addr in range(offset, offset+count):
            match addr:
                case 0x04:
                    data.append(self.div)
                case 0x05:
                    data.append(self.tima)
                case 0x06:
                    data.append(self.timer_mod)
                case 0x07:
                    clock = 0
                    match self.cycles_per_inc:
                        case 1024:
                            clock = 0
                        case 16:
                            clock = 1
                        case 64:
                            clock = 2
                        case 256:
                            clock = 3

                    byte = (self.timer_enabled << 2) | clock
                    data.append(byte) 
                case 0xF:
                    data.append(self.intf)
                case _:
                    return self.read_buff[offset:offset+count]
        return data
    
    def tick(self, cycles:int):
        if self.timer_enabled:
            self.cycle_timer0 += cycles
            while self.cycle_timer0 >= self.cycles_per_inc:
                self.cycle_timer0 -= self.cycles_per_inc
                self.tima += 1

                if self.tima > 0xFF:
                    self.tima = self.timer_mod
                    self.intf |= 0b100

        self.cycle_timer1 += cycles
        if self.cycle_timer1 >= 256:
            self.cycle_timer1 = 0
            self.div = (self.div + 1) & 0xFF

        self.cycle_timer2 += cycles
        if self.cycle_timer2 >= 70000:
            self.cycle_timer2 = 0
            self.intf |= 0b1
        
    def check_int(self):
        int_to_process = self.ie.state & self.intf
        for bit in range(0,4):
            is_set = (int_to_process >> bit) & 1
            if is_set: return bit
        return -1

    def int_ack(self, interrupt:int):
        self.intf &= ~(0b1 << interrupt)