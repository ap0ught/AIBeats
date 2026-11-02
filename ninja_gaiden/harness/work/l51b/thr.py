"""Windmill throw variants from TAS 23,700 (c = 78 + lag): python work/l51b/thr.py lag"""
import sys
sys.path.insert(0, 'work/l51b')
from lb import *
L = int(sys.argv[1]); c = 78 + L
S = 23700
hist = enforce(tasleg(S - 300, S), [()] * 30)
def run(mods, n=23830, show=False):
    rows = enforce(tasleg(S + 1, n, mods), hist)
    lg = legal_ok(rows, hist)
    fc.load('b'); _, recs, _ = fc.step(rows, record='all')
    h = trackhits(recs, S + 1)
    r = recs[-1]; X, y = RXY(r)
    # first frame at y 208 after 23790 ... report X at 23800 and 23830
    r8 = recs[23800 - S - 1]
    return lg, h, RXY(r8), (X, y), r['hp65'], r['np64']
fc = core(tas_mst(S)); fc.poke(0xBF, (c + S - 22125) % 256); fc.save('b'); fc._ka_slot = 'b'
print('TAS', tas_xy(23800), tas_xy(23830))
V = {
 'tas1f(illegal)': {},
 'BU2 rel2': {23743: {'B', 'Up'}, 23744: {'B', 'Up'}, 23778: {'B', 'Up'}, 23779: {'B', 'Up'}},
 'BUR2': {23743: {'B', 'Up', 'Right'}, 23744: {'B', 'Up', 'Right'}, 23778: {'B', 'Up', 'Right'}, 23779: {'B', 'Up', 'Right'}},
}
for d1 in (-2, -1, 0, 1, 2):
    for d2 in (-2, -1, 0, 1, 2):
        m = {}
        for t in (23743 + d1, 23744 + d1, 23778 + d2, 23779 + d2): m[t] = {'B', 'Up', 'Right'}
        V[f'BUR d{d1},{d2}'] = m
for k, m in V.items():
    print(k, run(m))
fc.close()
