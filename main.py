from board.board import Motherboard

mb = Motherboard("./rom.gb")
running = True

for name, reg in mb.cpu.registers.items():
    print(f"{name}: {hex(reg.get())}")
    
while running:
    mb.mainloop()

    