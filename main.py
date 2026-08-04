from board.board import Motherboard
from sys import argv

DEBUG = True
CART = argv[1]

mb = Motherboard(CART, DEBUG)

running = True

while running:
    mb.mainloop()