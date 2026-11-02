"""NesHawk: 5-1 wall (X 1,504 face, top y 96) after the legal bird boost (Left x2 at 22,793 variant; hit 23,084).
TAS path state 22,389 + legalized TAS rows (left2) to K, then climb candidates; score = first frame with y <= 96 and X >= 1,505
(on top), else best y.  python work/l51p/nhwall.py K [trace]"""
import sys, itertools
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l51p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
from lib0 import *
TR = A.tas_rows()
def T(f): return set(TR[f - 1])
S = 22389; K = int(sys.argv[1]); TRACE = len(sys.argv) > 2
want = []
for f in range(S + 1, K + 1):
    w = T(f)
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    if f in (22793, 22794): w = {'Left'}
    want.append(tuple(sorted(w)))
hist = [tuple(sorted(T(f) - ({'Left'} if {'Left', 'Right'} <= T(f) else set()))) for f in range(S - 120, S + 1)]
en = A.Enforcer(hist); pre = [tuple(sorted(en.emit(w))) for w in want]
e = C.open_emu('l51p_nhwall.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/12_5-1_control')
    e.run_ram([tuple(TR[f - 1]) for f in range(st['frame'] + 1, S + 1)])
    _, rams = e.run_ram(pre); base = e.msave()
    m = rams[-1]; print('state', K, 'X,y', XY(m), 'hp', m[0x65], 'inv', m[0x95], 'rf', hex(m[0x84]), flush=True)
    if TRACE:
        _, rr = e.run_ram([('Right',)] * 40)
        for i, m in enumerate(rr): print(K + 1 + i, XY(m), 'rf', hex(m[0x84]), 'anim', m[0x8C] if False else '')
        sys.exit()
    # candidate climbs: macro cycles after an initial wait of w frames of Right
    cyc = {}
    AR, AL_, R_, L_ = ('A', 'Right'), ('A', 'Left'), ('Right',), ('Left',)
    for a_ in range(2, 9):
        for b_ in range(2, 9):
            cyc[f'ch{a_}{b_}'] = [AR] * 2 + [R_] * a_ + [AL_] * 2 + [L_] * b_
    for n in range(4, 10):
        cyc[f'pil{n}'] = [AR] * 2 + [L_] * n
        cyc[f'wal{n}'] = [AL_] * 2 + [R_] * n
    res = []
    for name, cy in cyc.items():
        if not name.startswith('pil'): continue
        for ph in range(8, 49):
            for RW in (0, 2, 4):
                rows = (cy * 12)[:ph] + [('Right',)] * RW + [('A', 'Right')] * 2 + [('Right',)] * 60
                L = __import__('a34_core').Legal(list(hist) + list(pre))
                ok = True
                for r in rows:
                    if L.why(tuple(sorted(r))): ok = False; break
                    L.push(tuple(sorted(r)))
                if not ok: continue
                e.mload(base); _, rr = e.run_ram(rows)
                top = None; by = 999
                for i, m in enumerate(rr):
                    X, y = XY(m)
                    if m[0x65] == 0 or y > 240: break
                    by = min(by, y)
                    if y <= 100 and X >= 1530 and top is None: top = K + 1 + i
                res.append((top or 99999, by, name, ph, RW))
    res.sort()
    for r in res[:12]: print(r, flush=True)
    print('TAS at X>=1530 y<=100:', next(f for f in range(23081, 23300) if XY(TM(f))[1] <= 100 and XY(TM(f))[0] >= 1530))
finally:
    e.close()
