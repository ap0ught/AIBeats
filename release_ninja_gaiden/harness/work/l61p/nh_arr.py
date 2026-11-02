"""NesHawk: does the 6-1 arrival state depend on the 5-4 history? TAS 5-4 rows delayed by d (blank rows first), Start on kill+595,
RAM on the 6-1 control row - 1 compared with d = 0 (all bytes except the stack page)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l61p_nharr.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/15_5-4_control'); f0 = st['frame']
    base = e.msave(); out = {}
    for d in (0, 2, 5, 11):
        e.mload(base)
        w = [()] * d + [tuple(TR[f - 1]) for f in range(f0 + 1, 29330)]
        _, rams = e.run_ram(w)
        kill = next(f0 + 1 + i for i, r in enumerate(rams) if r[0x66] == 0 and r[0x6D] == 15)
        e.mload(base)
        S = kill + 595; ctl = kill + 750
        ww = (w + [()] * 2000)[:ctl - 1 - f0]
        for f in range(29330 + d, ctl): ww[f - f0 - 1] = ()
        for f in (S, S + 1): ww[f - f0 - 1] = ('Start',)
        _, rams = e.run_ram(ww)
        out[d] = (kill, rams[-1])
        print('d', d, 'kill', kill, 'state row', ctl - 1, 'BF', rams[-1][0xBF], 'x', rams[-1][0x86], 'st', rams[-1][0x6D], flush=True)
    r0 = out[0][1]
    for d, (k, r) in out.items():
        diff = [hex(a) for a in range(0x800) if r[a] != r0[a] and not 0x100 <= a < 0x300]; ens = [hex(a) for a in range(0x400, 0x500) if r[a] != r0[a]]
        print('d', d, 'diffs vs d0 (no 0x100-0x2FF)', len(diff), diff[:40], 'enemy-slot diffs', ens, flush=True)
finally:
    e.close()
