"""Mesen trace of rows file from row lo to hi: frame row input X y anim hp enemies. python work/l32a/tr.py rows lo hi [--mst m --hist h]"""
import sys
sys.path.insert(0, 'work/l32a')
from lib import *
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return v
    return d
mst = opt('--mst', MST); hf = opt('--hist', '')
hist = C.rows_of(hf) if hf else HIST
rows = [tuple(r) for r in C.rows_of(a[0])]; lo, hi = int(a[1]), int(a[2])
fc = core(mst)
fc.step(rows[:lo - 1], record='last')
for i in range(lo - 1, min(hi, len(rows))):
    fc.step([rows[i]], record='last'); m = fc.ram()
    print(len(hist) + i + 1, i + 1, '+'.join(rows[i]) or '-', 'X', X(m), 'y', m[0x8A], 'an', m[0x80], 'hp', m[0x65], 'bf', m[0xBF], [(e[1], e[2], e[3]) for e in enemies(m)])
fc.close()
