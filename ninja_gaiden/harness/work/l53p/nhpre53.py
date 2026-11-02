"""NesHawk check of the 5-3 head start: ref4751/14_5-3_control (after row 26609) + pre53 rows from 26610; compare Ryu X,y/hp/np
with the TAS dump on every frame."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l53p')
from ng.solve import common as C
from ng.mode import TICKS
from lib0 import *
rows = [l.strip() for l in open('work/l53p/pre53_26704.txt') if l.strip() and not l.startswith('#')]
rows = [() if r == '-' else tuple(r.split('+')) for r in rows]
e = C.open_emu('l53p_nhpre.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/14_5-3_control'); f0 = st['frame']; print('state frame', f0, flush=True)
    sub = rows[f0 - 26608 + 1:]
    _, rams = e.run_ram(sub)
    bad = 0
    for i, m in enumerate(rams):
        f = f0 + 1 + i; t = TM(f)
        if XY(m) != XY(t) or m[0x65] != t[0x65] or m[0x64] != t[0x64]:
            bad += 1
            if bad < 5: print('diff', f, XY(m), XY(t))
    print('frames', len(rams), 'diffs', bad, 'end', f0 + len(rams), XY(rams[-1]), 'hp', rams[-1][0x65], 'np', rams[-1][0x64], flush=True)
finally:
    e.close()
