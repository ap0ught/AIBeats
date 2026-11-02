"""NesHawk: from states/<state> (frame f0 = 11,595 + k0 rows of <rows>), add a B row (2 frames) at each row in [lo, hi]
of <rows>, play to row n; print first ninpo change and X/y at the end.
python work/l32a/nhscan.py <rows> <state> k0 lo hi n [--spec B+Right]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l32a')
from ng.solve import common as C, legality as L
from ng.mode import TICKS
a = sys.argv[1:]
def opt(nm, d):
    if nm in a:
        i = a.index(nm); v = a[i + 1]; del a[i:i + 2]; return type(d)(v)
    return d
spec = opt('--spec', ''); hold = opt('--hold', 2)
rows = [tuple(r) for r in C.rows_of(a[0])]; stn = a[1]; k0, lo, hi, n = map(int, a[2:6])
HIST = C.rows_of('logs/l31_alt_b2r_poweron.inputs.txt')
def X(m): return (m[0x52] - 256 if m[0x52] >= 128 else m[0x52]) * 256 + m[0x51] + m[0x86]
e = C.open_emu('l32a_nhscan.log')
try:
    e.tick(TICKS); st = e.load(stn); print('loaded', stn, st['frame'])
    sid = e.msave()
    for j in [None] + list(range(lo, hi + 1)):
        want = list(rows[:n])
        if j is not None:
            for d in range(hold):
                w = tuple(sorted(set(want[j - 1 + d]) | {'B'})) if not spec else tuple(sorted(spec.split('+')))
                want[j - 1 + d] = w
        en = L.Enforcer((list(HIST) + want[:k0])[-1900:])
        lg = [tuple(sorted(en.emit(w))) for w in want[k0:]]
        e.mload(sid); sts, rams = e.run_ram(lg)
        np0 = rams[0][0x64]; ch = None; hit = None
        for i, m in enumerate(rams):
            if ch is None and m[0x64] != np0: ch = (k0 + i + 1, X(m), m[0x8A], m[0x64])
            if hit is None and m[0x65] < 15: hit = k0 + i + 1
        m = rams[-1]
        print('B at', j, 'np change', ch, 'hit', hit, 'end X', X(m), 'y', m[0x8A], 'np', m[0x64], 'it', m[0xC9], 'hp', m[0x65], flush=True)
finally:
    e.close()
