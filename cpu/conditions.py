from memory.registers import FlagRegister

class Conditional():
    '''
    Base class for all conditionals
    '''
    def __init__(self, flags:FlagRegister) -> None:
        '''
        A condition to be evaluated 

        :param self: The Conditional object
        :param flags: The flag register
        :type flags: FlagRegister
        '''
        self.flags = flags
        ...

    def evaluate(self) -> bool:
        '''
        Evaluates a condition

        :param self: The Conditional object
        :return: The state of the condition
        :rtype: bool
        '''
        ...

class NZ(Conditional):
    '''
    A conditional which is true when the zero flag is not set
    '''
    def evaluate(self) -> bool:
        return not self.flags.get_z()


class Z(Conditional):
    '''
    A conditional which is true when the zero flag is set
    '''
    def evaluate(self) -> bool:
        return self.flags.get_z()


class NC(Conditional):
    '''
    A conditional which is true when the carry flag is not set
    '''
    def evaluate(self) -> bool:
        return not self.flags.get_c()


class C(Conditional):
    '''
    A conditional which is true when the carry flag is set
    '''
    def evaluate(self) -> bool:
        return self.flags.get_c()

