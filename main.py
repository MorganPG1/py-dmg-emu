from board.board import Motherboard
from sys import argv

SYMBOLS = ""
if len(argv) > 2:
    SYMBOLS = argv[2]

CART = argv[1]

mb = Motherboard(CART, SYMBOLS)

running = True

while running:
    mb.mainloop()