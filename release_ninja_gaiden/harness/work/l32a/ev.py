"""Mesen: play 3-2 stage rows (rows after 3-2 control, legalized after the history) and print events
(ninpo/item/hp/thrown changes), first frame at X >= --x (default 1252), and the stage change.
    python work/l32a/ev.py <rows file> [N rows] [--x 1252] [--quiet] [--tail 600] [--mst m --hist h]"""
import sys
sys.path.insert(0, 'work/l32a')
from lib import *
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
GX = opt('--x', 1252); TAIL = opt('--tail', 0); mst = opt('--mst', MST); hf = opt('--hist', '')
quiet = '--quiet' in a; a = [q for q in a if q != '--quiet']
hist = C.rows_of(hf) if hf else HIST
rows = [tuple(r) for r in C.rows_of(a[0])]
if len(a) > 1: rows = rows[:int(a[1])]
lg = legal_after([], rows, hist)
if lg != rows: print('NOTE: legalization changed', sum(1 for p, q in zip(lg, rows) if p != q), 'rows')
fc = core(mst); prev = None; f = len(hist); got = False
for i in range(len(lg) + TAIL):
    r = lg[i] if i < len(lg) else ()
    fc.step([r], record='last'); m = fc.ram(); f += 1
    k = (m[0x64], m[0xC9], m[0x65], m[0xC8])
    if not quiet and prev is not None and k != prev:
        print(f, 'row', i + 1, 'X', X(m), 'y', m[0x8A], 'in', '+'.join(r) or '-', 'np', m[0x64], 'it', m[0xC9], 'hp', m[0x65], 'thrown', m[0xC8], 'en', enemies(m))
    prev = k
    if not got and X(m) >= GX and m[0x6D] == 6:
        got = True; print('X>=%d at frame %d row %d (TAS-frame lag %d) X %d y %d hp %d np %d it %d bf %d' % (GX, f, i + 1, 0, X(m), m[0x8A], m[0x65], m[0x64], m[0xC9], m[0xBF]))
    if m[0x6D] != 6:
        print('STAGE CHANGE at frame', f, 'row', i + 1, 'hp', m[0x65], 'np', m[0x64], 'item', m[0xC9], '$62', m[0x62]); break
s = m
print('END frame', f, 'X', X(m), 'y', m[0x8A], 'hp', m[0x65], 'np', m[0x64], 'it', m[0xC9], 'anim', m[0x80], 'en', enemies(m))
fc.close()
