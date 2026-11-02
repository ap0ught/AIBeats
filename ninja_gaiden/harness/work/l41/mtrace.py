"""Mesen trace of stage rows: python work/l41/mtrace.py <rows> <from> <to> [step]"""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
rows = C.rows_of(sys.argv[1]); a, b = int(sys.argv[2]), int(sys.argv[3]); st = int(sys.argv[4]) if len(sys.argv) > 4 else 1
fc = core(); fc.step(rows[:a - 1 - F0], record='last')
for f in range(a, b + 1):
    fc.step([rows[f - F0 - 1]], record='last'); m = fc.ram()
    if (f - a) % st: continue
    en = ' '.join(f"{e[0]}:t{e[1]}@{e[2]},{e[3]}" for e in enemies(m))
    print(f, '+'.join(rows[f - F0 - 1]) or '-', 'X', X(m), 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'an', m[0x80], en)
fc.close()
