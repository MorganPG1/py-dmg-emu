from board.board import Motherboard

DEBUG = True
#CART = "./cpu_instrs.gb"
CART = "./b.gb"

mb = Motherboard(CART, DEBUG)

running = True

while running:
    try:
        mb.mainloop()
    except Exception as e:
        '''
        print("EXECUTION STOPPED")
        for name, reg in mb.cpu.registers.items():
            print(f"{name}: {hex(reg.get())}")
        running = False
        '''
        pass