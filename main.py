from board.board import Motherboard

mb = Motherboard("./tetris.gb")
running = True

while running:
    try:
        mb.mainloop(True)
    except KeyboardInterrupt as e:
        print("EXECUTION STOPPED")
        for name, reg in mb.cpu.registers.items():
            print(f"{name}: {hex(reg.get())}")
        running = False