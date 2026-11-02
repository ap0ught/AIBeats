"""print the bird (slot j) state per frame on a row file from a state: python work/l51c/bst.py mst F0 f1 f2 step j [rows] [lagbase]"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
mst, F0, f1, f2, st, j = sys.argv[1], *map(int, sys.argv[2:7])
rows = [tuple(sorted(r)) for r in C.rows_of(sys.argv[7])] if len(sys.argv) > 7 and sys.argv[7] != '-' else c1rows()
lag = int(sys.argv[8]) if len(sys.argv) > 8 else 530
fld = dict(FLD); fld['vf'] = 0x448 + j; fld['vs'] = 0x450 + j
fc = F.FastCore(boot_rows=None, ticks=True, fields=fld); fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
r = fc.run_batch('s', [rows[F0:f2]], record='all')[0]
for i, s in enumerate(r.states):
    f = F0 + 1 + i
    if f < f1 or (f - f1) % st: continue
    X, y = RXY(s); hi = s['scr_hi']; hi = hi - 256 if hi >= 128 else hi
    v = s['vs']*256 + s['vf']; v = v - 65536 if v >= 32768 else v
    print(f, 'TASeq', f - 504 - lag, 'Ryu', X, y, '| t', s[f't{j}'], 'u', hi*256 + s['scr_lo'] + s[f'ex{j}'] - X, 'dy', s[f'ey{j}'] - y, 'v', v/256, P(rows[f-1]))
fc.close()
