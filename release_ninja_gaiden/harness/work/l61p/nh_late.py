"""NesHawk k-scan of the 5-4 Start delay (THE judge for the 6-1 arrival): Start (2 f) on kill + 595 + k, 6-1 control = load + 152,
then the head start (default pre61_32595.txt) from the control row; per k: c, $3E, $62, RAM diffs vs the first k, hits / room changes
(row numbers from the control row; TAS-equivalent = hits [2498] rooms [1425, 2511]).
python work/l61p/nh_late.py <k list> [--state NAME --kill K] [--rows file]
  default: ref4751/15_5-4_control + the TAS's 5-4 rows (kill 29,314). --state: a NesHawk state (states/NAME.State) saved on or after
  the 5-4 kill row K and before kill + 594 (blank rows are played from it)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l61p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
HS = [l.strip() for l in open('work/l61p/pre61_32595.txt') if l.strip() and not l.startswith('#')]
HS = [() if r == '-' else tuple(r.split('+')) for r in HS]
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
STN = opt('--state', ''); KILL = opt('--kill', 29314); RF = opt('--rows', 'work/l61p/pre61_32595.txt')
HS = [l.strip() for l in open(RF) if l.strip() and not l.startswith('#')]
HS = [() if r == '-' else tuple(r.split('+')) for r in HS]
KS = [int(x) for x in a[0].split(',')]
e = C.open_emu('l61p_nhlate.log')
try:
    e.tick(TICKS)
    st = e.load(STN or 'ref4751/15_5-4_control'); f0 = st['frame']
    base = e.msave(); ref = None
    for k in KS:
        e.mload(base)
        S = KILL + 595 + k
        if STN: w = [()] * (S + 200 - f0)
        else: w = [tuple(TR[f - 1]) for f in range(f0 + 1, 29330)] + [()] * (S + 200 - 29330)
        for f in (S, S + 1): w[f - f0 - 1] = ('Start',)
        _, rams = e.run_ram(w)
        load = next(f0 + 1 + i for i, r in enumerate(rams) if r[0x6D] == 16); ctl = load + 152
        e.mload(base)
        e.run_ram(w[:ctl - 1 - f0])
        m = e.ram_all()
        if ref is None: ref = m
        diff = [hex(a) for a in range(0x800) if m[a] != ref[a] and not 0x100 <= a < 0x300]
        _, rr = e.run_ram(HS)
        hits = [i + 1 for i in range(1, len(rr)) if rr[i][0x65] < rr[i-1][0x65]]
        rooms = [i + 1 for i in range(1, len(rr)) if rr[i][0x6E] != rr[i-1][0x6E]]
        print(f'k {k}: Start {S} load {load} control {ctl} c {rr[0][0xBF]} 3E {m[0x3E]} 62 {m[0x62]} RAM diffs vs k0 {diff[:12]} | head start hits(rel) {hits[:3]} rooms(rel) {rooms}', flush=True)
finally:
    e.close()
