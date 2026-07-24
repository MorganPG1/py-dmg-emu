class MemoryRegion():
    '''
    Base class for a region in memory space
    '''
    def __init__(self) -> None:
        pass

    def read(self, count:int) -> bytearray:
        '''
        Reads data from the MemoryRegion

        :param self: The MemoryRegion object
        :param count: The number of bytes to read
        :type count: int
        :return: The data read from the MemoryRegion
        :rtype: bytearray
        '''
        pass

    def write(self, buffer:bytearray) -> None:
        '''
        Writes data to the MemoryRegion

        :param self: The MemoryRegion object
        :param buffer: The data to write
        :type buffer: bytearray
        '''
        pass


