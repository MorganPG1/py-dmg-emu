from board.board import Motherboard

DEBUG = False
CART = "./cpu_instrs.gb"
#CART = "./b.gb"

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
        print(f"An exception was caught during CPU excecution: {e}")
        print("For testing purposes, this exception will be ignored, expect errors.")
        