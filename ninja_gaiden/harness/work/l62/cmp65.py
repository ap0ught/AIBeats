import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
def rows_of(p): return [() if l.strip() in ('','-') else tuple(sorted(l.strip().split('+'))) for l in open(p).read().splitlines() if not l.startswith('#')]
TR = A.tas_rows()
e = C.open_emu('l62_cmp65.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/room46_6-4b'); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, 38086 + 1)])
    e.run_ram(rows_of('work/l63p/jq_r4k2_kill.txt'))
    d = 11; S = 38921 + d
    _, rams = e.run_ram([()] * (S - 38340 - 1) + [('Start',), ('Start',)] + [()] * 400)
    load = next(38340 + 1 + i for i, m in enumerate(rams) if m[0x6D] == 21); ctl = load + 152
    ref = rams[ctl - 1 - 38341]
    st = e.load('l63v1_39880'); f0 = st['frame']
    d = 6; S3 = 40462 + d; C3 = 40617 + d
    _, rams = e.run_ram([()] * (S3 - f0 - 1) + [('Start',), ('Start',)] + [()] * 400)
    ld = next(f0 + 1 + i for i, m in enumerate(rams) if m[0x6D] == 21); C3 = ld + 152
    ours = rams[C3 - 1 - f0 - 1]
    print('ref bf', ref[0xBF], 'ours bf', ours[0xBF])
    print([(hex(x), ours[x], ref[x]) for x in range(0x800) if ours[x] != ref[x] and not 0x100 <= x < 0x300])
finally:
    e.close()
