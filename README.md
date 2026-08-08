# py-dmg-emu
A gameboy emulator written in python. As expected, very slow, but nowhere near as slow as I was expecting. This (like my previous PC emulator) is not meant to be accurate, nor a product you should use. It is currently unfinished, will it ever be finished? Probably not, but in it's current state you can play tetris and get to the overworld in pokemon red so i consider that a success.

## What needs working on
 - PPU emulation, currently works kinda but a lot of features are incomplete or not implemented
 - Optimisations, particularly in PPU because that is the slowest aspect.
 - Code cleanup, the code is very messy because a lot of this code was written while i was half asleep at like 3 AM

## What is not currently implemented
 - APU, no audio support at all, i'm not sure if i will ever implement this because it seems like it will slow down an already very slow codebase
 - LCD STAT interrupt
## How do i use this
If you want to test out this emulator the only dependencies are pygame and numpy, install them and you should be good to go.
The arguments are:

```
python3 main.py <path to .gb file> <path to .sym file (optional, for debugging purposes)>
```

I'd recommend using PyPy (you'll have to use pygame-ce though) for the best performance. I do keep getting a double-linked list corrupted malloc error sometimes when i use PyPy which i cannot figure out how i debug because that is a C exception in PyPy (i think it might be something up with the PPU implementation) but that could just be my system so it needs further testing.