"""No-boost fallback at tosser 1 (Mesen): pre51 rows to 22,340, then Right, A+Right x2 at j (jump at the pillar's left face X 416),
k cycles [A+Left x2, Right x n] (single-wall climb), Right x r, A+Right x2, Right -> first frame X >= 500 and y <= 128.
python work/l51p/climb1.py c [c ...]"""
import sys
sys.path.insert(0, 'work/l51p')
from lib import *
pre = [tuple(sorted(r)) for r in C.rows_of('work/l51p/pre51_22490.txt')][:22340 - 22124]
fc = core(tas_mst(22124)); fc._ka_slot = 's'
for c in [int(v) for v in sys.argv[1:]]:
    fc.load('s'); fc.poke(0xBF, (c - 1) % 256); fc.step(pre); fc.save('b'); fc._ka_slot = 'b'
    names, cands = [], []
    for j in range(22341, 22366, 2):
        for n in (6, 7, 8, 9):
            for k in (1, 2, 3, 4):
                for r in (0, 2, 5):
                    cy = [('A', 'Left')] * 2 + [('Right',)] * n
                    rows = [('Right',)] * (j - 22341) + [('A', 'Right')] * 2 + [('Right',)] * 14 + cy * k + [('Right',)] * r + [('A', 'Right')] * 2 + [('Right',)] * 70
                    if legal_ok(rows, pre): continue
                    names.append((j, n, k, r)); cands.append(rows)
    res = fc.run_batch('b', cands, record='all')
    out = []
    for nm, rr in zip(names, res):
        g = None; hp = 16
        for i, s in enumerate(rr.states):
            X, y = RXY(s)
            if s['hp65'] == 0 or y > 232: break
            if X >= 500 and y <= 128: g = 22341 + i; hp = s['hp65']; break
        if g: out.append((g, -hp, nm))
    out.sort()
    print(f'c {c}: {len(cands)} cands; best X>=500 y<=128:', out[:5], '(TAS 22,403; head start 22,402)', flush=True)
fc.close()
