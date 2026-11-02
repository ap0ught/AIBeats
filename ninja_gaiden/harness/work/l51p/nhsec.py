"""NesHawk: legalized TAS rows on a 5-1 section from the TAS path (ref4751/12_5-1_control + TAS rows to S), variants
'name:f=ROW,f1-f2=ROW;name2:...'; compares Ryu X/y/hp with the TAS per frame (first difference, hits, end).
python work/l51p/nhsec.py S E "<variants>" [--bf c]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l51p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
from lib0 import *
a = sys.argv[1:]
BF = None
if '--bf' in a: i = a.index('--bf'); BF = int(a[i+1]); del a[i:i+2]
S, E = int(a[0]), int(a[1]); VS = a[2].split(';')
TR = A.tas_rows()
def T(f): return set(TR[f - 1])
def build(ovs):
    ov = {}
    for it in ovs.split(',') if ovs else []:
        k, v = it.split('='); k1, k2 = (k.split('-') + [k])[:2]
        for f in range(int(k1), int(k2) + 1): ov[f] = set(x for x in v.split('+') if x and x != '-')
    want = []
    for f in range(S + 1, E + 1):
        w = T(f)
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
        if f in ov: w = ov[f]
        want.append(tuple(sorted(w)))
    hist = []
    for f in range(S - 120, S + 1):
        w = T(f)
        if 'Left' in w and 'Right' in w: w -= {'Left'}
        hist.append(tuple(sorted(w)))
    en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(w))) for w in want]
    ch = [(S + 1 + i, '+'.join(want[i]) or '-', '+'.join(rows[i]) or '-') for i in range(len(rows)) if want[i] != rows[i]]
    return rows, ch
e = C.open_emu('l51p_nhsec.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/12_5-1_control'); f00 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f00 + 1, S + 1)])
    if BF is not None: e.poke(0xBF, (BF + S - 22125) % 256)
    base = e.msave()
    for v in VS:
        name, ovs = (v.split(':', 1) + [''])[:2]
        rows, ch = build(ovs)
        e.mload(base); _, rams = e.run_ram(rows)
        first = None; hits = []; hp = TM(S)[0x65]
        for i, m in enumerate(rams):
            f = S + 1 + i; X, y = XY(m); t = TM(f); TX, TY = XY(t)
            if m[0x65] != hp: hits.append(f'{f}:{X},{y},{hp}->{m[0x65]}'); hp = m[0x65]
            if first is None and (X, y, m[0x65]) != (TX, TY, t[0x65]): first = (f, (X, y, m[0x65]), (TX, TY, t[0x65]))
        X, y = XY(rams[-1]); TX, TY = XY(TM(E))
        # lag at the end: TAS frame with the same X
        lagf = next((g for g in range(E - 60, E + 200) if XY(TM(g))[0] >= X), None)
        print(f'{name:14s} enforcer {ch[:6]} | first diff {first} | end X {X} y {y} hp {rams[-1][0x65]} (TAS {TX},{TY}; TAS reaches X {X} at {lagf} -> lag {E - lagf if lagf else None}) | hits {hits}', flush=True)
finally:
    e.close()
