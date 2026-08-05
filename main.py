from board.board import Motherboard
from sys import argv

if len(argv) > 2:
    DEBUG = True
else:
    DEBUG = False
CART = argv[1]

mb = Motherboard(CART, DEBUG)

running = True

while running:
    mb.mainloop()