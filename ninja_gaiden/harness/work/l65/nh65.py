"""l65 NesHawk check of 6-5 lines: ref state room47_6-5 + TAS rows to 38,932 (6-5 control - 1), poke $BF = v, play the line
(row 1 = control row) + 40 blank rows. Prints kill row (control row = 1), hp, T at the kill, pad-read conflicts ($2A != row).
python work/l65/nh65.py <line.txt> <bf list a,b,c or a-b> [--pre addr=v,..]
Multiple lines: line1.txt:bfs line2.txt:bfs ...  (each arg 'file:bfs')"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
PRE = opt('--pre', '')
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
def rows_of(p): return [row(l.strip()) for l in open(p).read().splitlines() if not l.startswith('#')]
def vals(s):
    out = []
    for p in s.split(','):
        if '-' in p: x, y = map(int, p.split('-')); out += list(range(x, y + 1))
        elif p: out.append(int(p))
    return out
jobs = []
if ':' in a[0]:
    for x in a:
        f, v = x.rsplit(':', 1); jobs.append((f, vals(v)))
else:
    jobs.append((a[0], vals(a[1])))
BIT = {'A': 0x80, 'B': 0x40, 'Select': 0x20, 'Start': 0x10, 'Up': 0x08, 'Down': 0x04, 'Left': 0x02, 'Right': 0x01}
TR = A.tas_rows()
e = C.open_emu('l65_nh65.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/room47_6-5'); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, 38932 + 1)])
    for kv in [p for p in PRE.split(',') if p]:
        k_, v_ = kv.split('='); e.poke(int(k_, 0), int(v_, 0))
    base = e.msave()
    for fn, vs in jobs:
        rows = rows_of(fn) + [()] * 40
        for v in vs:
            e.mload(base); e.poke(0xBF, v)
            _, rams = e.run_ram(rows)
            kill = None
            for i, m in enumerate(rams):
                if m[0x66] == 0 and m[0x6D] == 21 and m[0x65] > 0:
                    kill = (i + 1, m[0x65], m[0x63]); break
            conf = [i + 1 for i, m in enumerate(rams[:kill[0] if kill else len(rams)]) if m[0x2A] != sum(BIT[b] for b in rows[i])]
            m = rams[-1]
            print(fn, 'bf', v, 'kill', kill, 'end hp', m[0x65], 'stage', m[0x6D], 'conflicts', conf[:12], flush=True)
finally:
    e.close()
