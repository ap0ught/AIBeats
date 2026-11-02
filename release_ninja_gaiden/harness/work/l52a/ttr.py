"""TAS trace: python work/l52a/ttr.py f1 f2  (X y act pose touch flags pad vy hp np item room)"""
import sys; sys.path.insert(0, 'work/l52p')
from lib0 import *
for f in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
    m = TM(f); X, y = XY(m)
    print(f, 'X', X, 'xs', m[0x85], 'y', y, 'act', hex(m[0x80]), 'pose', m[0x83], 'tch', hex(m[0x8C]), 'fl', hex(m[0x84]),
          'pad', hex(m[0x28]), hex(m[0x2A]), 'vy', m[0x89], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'rm', m[0x6E], 'kb', hex(m[0x93]))
