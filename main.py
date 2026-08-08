'''
DMG Gameboy Emulator Project - MorganPG

main.py:

The main script, this is what you execute to run the code.
'''
from board.board import Motherboard
from sys import argv

SYMBOLS = ""
if len(argv) == 1:
    print("Usage: main.py <gameboy rom> <optional debug symbols file>")
    exit()
elif len(argv) > 2:
    SYMBOLS = argv[2]

CART = argv[1]

mb = Motherboard(CART, SYMBOLS)

running = True

while running:
    mb.mainloop()