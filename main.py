from board.board import Motherboard

mb = Motherboard("./rom.gb")
running = True

while running:
    mb.mainloop()

    