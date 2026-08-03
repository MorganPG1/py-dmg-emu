from memory.memory import MemoryRegion
class Serial(MemoryRegion):
    def __init__(self) -> None:
        self.buffer = 0
    def write(self, offset: int, buffer: bytearray) -> None:
        if offset == 0x01:
            self.buffer = buffer[0]
        if offset == 0x02 and buffer[0] == 0x81:
            print(chr(self.buffer), end="", flush=True)
            #print(f"SERIAL WRITE: {hex(self.buffer)}")
    def read(self, offset: int, count: int) -> bytearray:
        return bytearray([0xFF]*count)