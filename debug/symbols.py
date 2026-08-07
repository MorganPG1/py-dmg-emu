'''
DMG Gameboy Emulator Project - MorganPG

debug/symbols.py

RGBDS debug symbols (.sym) parser
'''
import bisect
from os.path import exists
#Format seems to be:
#; = comment
#BANK:ADDR LABEL
# OR CONSTANT LABEL (we will ignore constants)
class SymbolParser():
    def __init__(self, path:str) -> None:
        self.labels:dict[str, str] = {} #Key = BANK:ADDR, Value = Label
        self.bank_symbols:dict[int,list[tuple[int,str]]] = {}
        self.bank_addrs:dict[int,list[int]] = {}
        if exists(path):
            with open(path) as f:
                lines = f.readlines()

                for line1 in lines:
                    if line1.startswith(";"):
                        continue

                    if ":" not in line1:
                        continue

                    key = line1[:7]
                    bank = int(key[:2], 16)
                    addr = int(key[3:], 16)

                    val = line1[8:len(line1)-1]
                    self.labels[key] = val

                    if bank not in self.bank_symbols:
                        self.bank_symbols[bank] = []
                        self.bank_addrs[bank] = []
                    self.bank_symbols[bank].append((addr, val))
                    self.bank_addrs[bank].append(addr)
    def get_symbol(self, bank:int, addr:int) -> str:
        if bank not in self.bank_symbols:
            return ""

        symbols = self.bank_symbols[bank]
        addrs = [s[0] for s in symbols]

        i = bisect.bisect_right(addrs, addr) - 1

        if i < 0:
            return ""

        base, label = symbols[i]
        offset = addr - base

        if offset == 0:
            return label
        return f"{label}+{offset}"
    def is_same_symbol(self, bank:int, addr1:int, addr2:int) -> bool:
        if bank not in self.bank_addrs:
            return False

        addrs = self.bank_addrs[bank]

        idx1 = bisect.bisect_right(addrs, addr1) - 1
        idx2 = bisect.bisect_right(addrs, addr2) - 1

        return idx1 >= 0 and idx1 == idx2