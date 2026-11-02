"""l65 NesHawk check on REAL 6-5 arrivals (no pokes): ref room46_6-4b + TAS rows to 38,086, a56 r4k2 (6-4b kill row 254,
T 145), Start (2 f) on the earliest Start 38,921 + d, then blank to the 6-5 control - 1; read bf / $62 / $3E there and play the
line that pick.py chooses for that bf (or a given line). Prints arrival bytes, kill row, hp, END seen offset (pick rule) and the
pad-read conflicts.
python work/l65/nhreal.py <d list e.g. 0,7,30> [--line file]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l65')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
import pick
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return v
    return d
LINE = opt('--line', '')
def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
def rows_of(p): return [row(l.strip()) for l in open(p).read().splitlines() if not l.startswith('#')]
ds = []
for p in a[0].split(','):
    if '-' in p: x, y = map(int, p.split('-')); ds += list(range(x, y + 1))
    else: ds.append(int(p))
BIT = {'A': 0x80, 'B': 0x40, 'Select': 0x20, 'Start': 0x10, 'Up': 0x08, 'Down': 0x04, 'Left': 0x02, 'Right': 0x01}
TR = A.tas_rows()
r4 = rows_of('work/l63p/jq_r4k2_kill.txt')
tab = pick.load()
e = C.open_emu('l65_nhreal.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/room46_6-4b'); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, 38086 + 1)])
    _, rams = e.run_ram(r4)
    print('6-4b kill check: $66 after row 254 =', rams[253][0x66], 'T', rams[253][0x63], flush=True)
    base = e.msave()
    for d in ds:
        e.mload(base)
        S = 38921 + d
        pre = [()] * (S - 38340 - 1) + [('Start',), ('Start',)]
        _, rams = e.run_ram(pre + [()] * 200)
        load = next(38340 + 1 + i for i, m in enumerate(rams) if m[0x6D] == 21)
        ctl = load + 152
        e.mload(base)
        _, rams = e.run_ram((pre + [()] * 400)[:ctl - 1 - 38340])
        m = rams[-1]
        bf, t62, e3e = m[0xBF], m[0x62], m[0x3E]
        if LINE:
            line = LINE
        else:
            c = pick.best(bf, t62, e3e, tab)
            if not c:
                print('d', d, 'ctl', ctl, 'bf', bf, 't62', t62, 'e3e', e3e, 'NO LINE', flush=True); continue
            line = c[0][3]
        rows = rows_of(line) + [()] * 30
        _, rams = e.run_ram(rows)
        kill = next(((i + 1, mm[0x65], mm[0x63]) for i, mm in enumerate(rams) if mm[0x66] == 0 and mm[0x6D] == 21 and mm[0x65] > 0), None)
        conf = [i + 1 for i, mm in enumerate(rams[:kill[0] if kill else len(rams)]) if mm[0x2A] != sum(BIT[b] for b in rows[i])]
        endo = pick.end_offset(kill[0], t62, e3e)[0] if kill else None
        print('d', d, 'Start', S, 'ctl', ctl, 'bf', bf, 't62', t62, 'e3e', e3e, line, 'kill', kill, 'END seen', endo,
              'conflicts', conf[:10], flush=True)
finally:
    e.close()
