"""Ryu + enemies, ours vs the TAS, row by row (row i = frame F0+i+1 ours, TAS 9828+i+1).
python work/l31t/cmpen.py <our stage rows file | tas> <i0> <i1> [every]
'tas' = legalized TAS rows from TAS 9828 (lag 165)."""
import sys
sys.path.insert(0, 'work/l31t'); sys.path.insert(0, '.')
from lib import *
from ng.solve import hitbox as H
src = sys.argv[1]; i0, i1 = int(sys.argv[2]), int(sys.argv[3]); ev = int(sys.argv[4]) if len(sys.argv) > 4 else 1
TROWS = TR[9828:9828 + i1 + 1]
ours = legal_after([], TROWS) if src == 'tas' else C.rows_of(src)[:i1 + 1]
def run(mst, rows):
    fc = F.FastCore(boot_rows=None); fc.put('s', open(mst, 'rb').read()); fc.load('s')
    out = []
    for i, r in enumerate(rows):
        fc.step([r], record='last'); m = fc.ram()
        if i0 <= i <= i1:
            s52 = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]; sc = s52 * 256 + m[0x51]
            out.append((i, '+'.join(r) or '-', sc + m[0x86], m[0x8A], m[0x65], m[0x64], m[0xC9],
                        [(e['slot'], e['type'], sc + e['x'], e['y']) for e in H.enemies(m)]))
    fc.close()
    return out
A_ = run(MST, ours); B_ = run('states/mesen/l31t_tas9828.mst', TROWS)
for a_, b_ in zip(A_, B_):
    if a_[0] % ev and a_[2:6] == b_[2:6]: continue
    print(f"{a_[0]} f{F0+a_[0]+1} {a_[1]:>10} X {a_[2]} y {a_[3]} hp {a_[4]} np {a_[5]} it {a_[6]} en {a_[7]}")
    print(f"{'':>6} TAS {b_[1]:>10} X {b_[2]} y {b_[3]} hp {b_[4]} np {b_[5]} it {b_[6]} en {b_[7]}")
