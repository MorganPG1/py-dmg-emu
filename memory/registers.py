'''
DMG Gameboy Emulator Project - MorganPG

memory/registers.py

Classes for 8 and 16 bit registers
'''
from memory.memory import MemoryController
class Register():
    '''
    Base class for all registers
    '''
    def __init__(self) -> None:
        self.val:int
        '''The value stored in the register'''
        
        pass

    def get(self) -> int:
        '''
        Returns the value currently stored in the register

        :param self: The Register object
        :return: The value stored in the register
        :rtype: int
        '''
        pass

    def set(self, value:int):
        '''
        Changes the value stored in the register

        :param self: The Register object
        :param value: The value to store in the register
        :type value: int
        '''
        pass

    def inc(self) -> bool:
        '''
        Increments the value stored in the register

        :param self: The Register object
        :return: True if an overflow happened, False otherwise
        :rtype: bool
        '''
        pass

    def dec(self) -> bool:
        '''
        Decrements the value stored in the register

        :param self: The Register object
        :return: True if an underflow happened, False otherwise
        :rtype: bool
        '''
        pass

    def geti(self) -> int:
        '''
        Returns the value stored in the register, then increments it

        :param self: The Register object
        :return: The value stored in the register
        :rtype: int
        '''
        val = self.get()
        self.inc()
        return val
    
    def getd(self) -> int:
        '''
        Returns the value stored in the register, then decrements it

        :param self: The Register object
        :return: The value stored in the register
        :rtype: int
        '''
        val = self.get()
        self.dec()
        return val
    
class Register8b(Register):
    '''
    An 8 bit register
    '''
    def __init__(self, initial_val:int=0x00) -> None:
        '''
        An 8 bit register

        :param self: The Register8b object
        :param initial_val: The value to initialise the register to
        :type initial_val: int
        '''
        self.val:int = initial_val & 0xFF

    def get(self) -> int:
        return self.val

    def set(self, value:int):
        self.val = value & 0xFF

    def inc(self) -> bool:
        inc = (self.val + 1)

        self.val = inc & 0xFF

        return inc > 255

    def dec(self) -> bool:
        dec = (self.val - 1)
        
        self.val = dec & 0xFF

        return dec < 0

    def geti(self) -> int:
        val = self.val

        self.val = (val + 1) & 0xFF
        return val

    def getd(self) -> int:
        val = self.val

        self.val = (val - 1) & 0xFF
        return val

class FlagRegister(Register8b):
    def set(self, value: int):
        super().set(value)
        self.val &= 0xF0
    def inc(self) -> bool:
        raise NotImplementedError("INC/DEC/GETI/GETD not implemented for the flag register.")
    def dec(self) -> bool:
        raise NotImplementedError("INC/DEC/GETI/GETD not implemented for the flag register.")
    def getd(self) -> int:
        raise NotImplementedError("INC/DEC/GETI/GETD not implemented for the flag register.")
    def geti(self) -> int:
        raise NotImplementedError("INC/DEC/GETI/GETD not implemented for the flag register.")
    def get_z(self) -> bool:
        return bool(self.val & 0x80)
    def get_n(self) -> bool:
        return bool(self.val & 0x40)
    def get_h(self) -> bool:
        return bool(self.val & 0x20)
    def get_c(self) -> bool:
        return bool(self.val & 0x10)
    def set_z(self, state:int):
        if state:
            self.val |= (1 << 7)
        else:
            self.val &= ~(1 << 7)
    def set_n(self, state:int):
        if state:
            self.val |= (1 << 6)
        else:
            self.val &= ~(1 << 6)
    def set_h(self, state:int):
        if state:
            self.val |= (1 << 5)
        else:
            self.val &= ~(1 << 5)
    def set_c(self, state:int):
        if state:
            self.val |= (1 << 4)
        else:
            self.val &= ~(1 << 4)
    def set_znhc(self, z:int, n:int, h:int, c:int):
        self.val = (z << 7) | (n << 6) | (h << 5) | (c << 4)
class Register16b(Register):
    '''
    A 16 bit register
    '''
    def __init__(self, regA:Register8b, regB:Register8b) -> None:
        '''
        A 16 bit register

        :param self: The Register16b object
        :param regA: The register that stores the upper 8 bits
        :type regA: Register8b
        :param regB: The register that stores the lower 8 bits
        :type regB: Register8b
        '''
        self.regA = regA
        self.regB = regB
        

    def get(self) -> int:
        return (self.regA.val << 8) | self.regB.val

    def set(self, value: int):
        self.regA.val = (value >> 8) & 0xFF
        self.regB.val = value & 0xFF

    def inc(self) -> bool:
        vali = ((self.regA.val << 8) | self.regB.val) + 1

        self.regA.val = (vali >> 8) & 0xFF
        self.regB.val = vali & 0xFF

        return vali > 0xFFFF

    def dec(self) -> bool:
        vald = ((self.regA.val << 8) | self.regB.val) - 1
        
        self.regA.val = (vald >> 8) & 0xFF
        self.regB.val = vald & 0xFF

        return vald < 0

    def geti(self) -> int:
        val = ((self.regA.val << 8) | self.regB.val)
        vali = val + 1
        
        self.regA.val = (vali >> 8) & 0xFF
        self.regB.val = vali & 0xFF

        return val

    def getd(self) -> int:
        val = ((self.regA.val << 8) | self.regB.val)
        vald = val - 1
        
        self.regA.val = (vald >> 8) & 0xFF
        self.regB.val = vald & 0xFF

        return val

class Register16b_uncombined(Register):
    '''
    A 16 bit register that is not made up of 2 smaller registers (unlike Register16b)
    '''
    def __init__(self, initial_val:int=0x00) -> None:
        '''
        A 16 bit register 

        :param self: The Register16b_uncombined object
        :param initial_val: The value to initialise the register to
        :type initial_val: int
        '''
        self.val = initial_val
    def get(self) -> int:
        return self.val & 0xFFFF
    def set(self, value: int):
        self.val = value & 0xFFFF
    def inc(self) -> bool:
        inc = self.val + 1
        self.val = inc & 0xFFFF
        return inc > 0xFFFF
    def dec(self) -> bool:
        dec = self.val - 1
        self.val = dec & 0xFFFF
        return dec < 0
    def geti(self) -> int:
        val = self.val
        self.val = (val + 1) & 0xFFFF
        return val
    def getd(self) -> int:
        val = self.val
        self.val = (val - 1) & 0xFFFF
        return val

class Register16b_mem(Register8b):
    '''
    i have no clue how to describe this for now so uh future me update this
    pretty much [HL], [BC], [DE], you get the idea
    '''

    def __init__(self, register:Register16b, mem:MemoryController, mode:int) -> None:
        self.reg = register
        self.mem = mem
        self.mode = mode
    def get(self) -> int:
        match self.mode:
            case 1:
                addr = self.reg.geti()
            case 2:
                addr = self.reg.getd()
            case _:
                addr = self.reg.get()

        return self.mem.read(addr, 1)[0]
    def set(self, value: int):
        match self.mode:
            case 1:
                addr = self.reg.geti()
            case 2:
                addr = self.reg.getd()
            case _:
                addr = self.reg.get()

        data = bytearray([value])
        self.mem.write(addr, data)
    def inc(self) -> bool:
        match self.mode:
            case 1:
                addr = self.reg.geti()
            case 2:
                addr = self.reg.getd()
            case _:
                addr = self.reg.get()

        val = self.mem.read(addr, 1)[0] + 1
        self.mem.write(addr, bytearray([val & 0xFF]))

        return val > 0xFF
    def dec(self) -> bool:
        match self.mode:
            case 1:
                addr = self.reg.geti()
            case 2:
                addr = self.reg.getd()
            case _:
                addr = self.reg.get()

        val = self.mem.read(addr, 1)[0] - 1
        self.mem.write(addr, bytearray([val & 0xFF]))

        return val < 0x0
    