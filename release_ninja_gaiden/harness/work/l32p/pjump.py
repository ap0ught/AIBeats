"""pillar -> branch jump test from the TAS state 12030 (BF poked so tosser-1 spawn BF = b).
python work/l32p/pjump.py b"""
import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
b = int(sys.argv[1])
fc = core('states/mesen/l32p_tas12030.mst'); fc.poke(0xBF, (b - 25) & 255); fc.save('p')
H = list(TR[:12030])
cands = []
for j in range(12036, 12070):
    want = list(TR[12030:j]) + [('A', 'Right')] * 2 + [('Right',)] * 80
    cands.append((j, legal_after([], want, H)))
rs = fc.run_batch('p', [c for _, c in cands], record='all')
for (j, rows), r in zip(cands, rs):
    path = [(12031 + i, ax(s), s['y'], s['hp']) for i, s in enumerate(r.states)]
    land = next(((f, x, y) for f, x, y, h in path if f > j + 5 and y == 128), None)
    print('jump at', j, 'X at jump', path[j - 12031][1], 'land', land, 'end', path[-1])
fc.close()
