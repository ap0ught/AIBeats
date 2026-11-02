"""$BF arrival scan on the TAS line: TAS Mesen state 18,960 with $BF poked (= our chain's value at the same stage-relative
frame), TAS effective pads to the end trigger. For each value: first frame Ryu (X, y, hp) leaves the TAS, first frame the
enemy slots differ (type / x / y), which slot/type. python work/l43p/bfscan.py v1 v2 ... | all | near"""
import sys; sys.path.insert(0, 'work/l43p')
from lib import *
for j in range(8): FLD[f'ex{j}'] = 0x460 + j; FLD[f'ey{j}'] = 0x480 + j
a = sys.argv[1:]
TBF = 251   # TAS $BF after row 18,960
if a == ['all']: vals = list(range(256))
elif a == ['near']: vals = [(TBF + 84 + d) % 256 for d in range(-30, 6)]
else: vals = [int(v) for v in a]
END = 21074
pads = [TPAD[f] for f in range(18961, END + 1)]
fc = core(tas_mst(18960)); fc.save('b')
def en(m):
    return tuple((m[0x400+j] if m[0x73] >> j & 1 else 0, m[0x460+j], m[0x480+j]) for j in range(8))
def en_r(r):
    return tuple((r[f't{j}'] if r['eact'] >> j & 1 else 0, r[f'ex{j}'], r[f'ey{j}']) for j in range(8))
TEN = {f: en(TM(f)) for f in range(18961, END + 1)}
TXY = {f: tas_xy(f) + (TM(f)[0x65],) for f in range(18961, END + 1)}
for v in vals:
    fc.load('b'); fc.poke(0xBF, v)
    _, recs, _ = fc.step(pads, record='all')
    fr = fe = None; info = ''
    for i, r in enumerate(recs):
        f = 18961 + i
        if fe is None and en_r(r) != TEN[f]:
            fe = f; e1 = en_r(r); e0 = TEN[f]
            k = next(j for j in range(8) if e1[j] != e0[j]); info = f'slot {k} TAS {e0[k]} ours {e1[k]}'
        if fr is None and XY(r) + (r['hp65'],) != TXY[f]:
            fr = f; rinfo = f'Ryu {XY(r)} hp {r["hp65"]} vs TAS {TXY[f]}'
            break
    last = recs[-1]
    print(f'BF@18960 {v:3d} (d {(v - TBF) % 256:3d}) enemy-diverge {fe} {info} | Ryu-diverge {fr} {rinfo if fr else ""} | end rm {last["room6e"]} st {last["st6d"]} 5C {last["e5c"]}', flush=True)
fc.close()
