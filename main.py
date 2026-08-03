from board.board import Motherboard

mb = Motherboard("./cpu_instrs.gb")
#mb = Motherboard("./b.gb")

running = True

while running:
    try:
        mb.mainloop(False)
    except Exception as e:
        '''
        print("EXECUTION STOPPED")
        for name, reg in mb.cpu.registers.items():
            print(f"{name}: {hex(reg.get())}")
        running = False
        '''
        pass