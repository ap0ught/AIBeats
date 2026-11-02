import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
def rows_of(p): return [() if l.strip() in ('','-') else tuple(sorted(l.strip().split('+'))) for l in open(p).read().splitlines() if not l.startswith('#')]
TR = A.tas_rows()
LINE = 'work/l63p/dm_r2d5_kill.txt'
e = C.open_emu('l62_grp65.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/room46_6-4b'); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, 38086 + 1)])
    e.run_ram(rows_of('work/l63p/jq_r4k2_kill.txt'))
    S = 38921 + 11
    _, rams = e.run_ram([()] * (S - 38340 - 1) + [('Start',), ('Start',)] + [()] * 400)
    ld = next(38341 + i for i, m in enumerate(rams) if m[0x6D] == 21); ctl = ld + 152
    st = e.load('ref4751/room46_6-4b')
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, 38086 + 1)]); e.run_ram(rows_of('work/l63p/jq_r4k2_kill.txt'))
    e.run_ram([()] * (S - 38340 - 1) + [('Start',), ('Start',)] + [()] * (ctl - 1 - S - 1))
    ref = e.ram_all(); print('ref bf', ref[0xBF], flush=True)
    st = e.load('l63v1_39880'); f0 = st['frame']; S3 = 40468
    _, rams = e.run_ram([()] * (S3 - f0 - 1) + [('Start',), ('Start',)] + [()] * 300)
    ld = next(f0 + 1 + i for i, m in enumerate(rams) if m[0x6D] == 21); C3 = ld + 152
    e.load('l63v1_39880'); e.run_ram([()] * (S3 - f0 - 1) + [('Start',), ('Start',)] + [()] * (C3 - 1 - S3 - 1))
    ours = e.ram_all(); print('ours bf', ours[0xBF], 'ctl', C3, flush=True)
    base = e.msave()
    G = {'slots': range(0x400, 0x500), 'c3ce': range(0xC3, 0xCF), 'x38x': [0x381, 0x382, 0x394], 'x6xx': [0x644, 0x664, 0x665, 0x666, 0x681],
         '8d': [0x8D], 'timer': [0x3E, 0x62, 0x60]}
    line = rows_of(LINE) + [()] * 30
    for name in ['none', 'all'] + list(G):
        e.mload(base)
        addrs = [x for g in G.values() for x in g] if name == 'all' else ([] if name == 'none' else list(G[name]))
        for x in addrs:
            if ours[x] != ref[x]: e.poke(x, ref[x])
        _, rr = e.run_ram(line)
        kill = next((i + 1 for i, m in enumerate(rr) if m[0x66] == 0 and m[0x6D] == 21 and m[0x65] > 0), None)
        dead = next((i + 1 for i, m in enumerate(rr) if m[0x6E] == 35 or m[0x65] == 0), None)
        print(name, 'kill row', kill, 'death row', dead, 'min hp', min(m[0x65] for m in rr), flush=True)
finally:
    e.close()
