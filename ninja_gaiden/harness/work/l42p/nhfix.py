"""NesHawk misread fixer for a 4-2 rows file (rows[0] = control row 16,682 on the TAS axis), $BF poked at control.
python work/l42p/nhfix.py <rows> <c> <goal frame> <out>
Loop: find the first frame where NesHawk's $2A != the row (an eaten edge); try moving that edge 1 f earlier / later
(and 2 f); keep the variant whose first misread is latest with the best (hp, X at the goal); stop when clean."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import to_mask
rows = [tuple(r) for r in C.rows_of(sys.argv[1])]; c = int(sys.argv[2]); G = int(sys.argv[3]); out = sys.argv[4]
e = C.open_emu('l42p_nhfix.log')
def run(rw):
    e.load('ref4751/09_4-2_control'); e.poke(0xBF, c)
    _, rams = e.run_ram(rw[1:G - 16682 + 1])
    mis = None; hp = 16; hits = []
    for i, m in enumerate(rams):
        f = 16683 + i
        if mis is None and m[0x2A] != to_mask(rw[i + 1]): mis = f
        if m[0x65] < hp: hits.append(f)
        hp = m[0x65]
    m = rams[-1]; X = m[0x52]*256 + m[0x51] + m[0x86]
    return mis, m[0x65], X, hits
def legal(rw):
    from ng.solve.legality import check
    r = check(list(rw), [()] * 300)
    return r.get('pass', False)
try:
    e.tick(TICKS)
    cur = list(rows)
    res = run(cur); print('start', res, flush=True)
    for it in range(40):
        mis = res[0]
        if mis is None: break
        i = mis - 16682
        best = None
        for sh in (-1, 1, -2, 2, -3, 3):
            v = list(cur)
            if sh < 0:
                for k in range(i + sh, i): v[k] = cur[i]
            else:
                for k in range(i, i + sh): v[k] = cur[i - 1]
            if not legal(v): continue
            r = run(v)
            sc = (r[0] or 99999, r[1], r[2])
            print('  edge', mis, 'shift', sh, '->', r, flush=True)
            if r[0] is not None and r[0] <= mis: continue
            if best is None or (r[1], r[2], r[0] or 99999) > (best[1][1], best[1][2], best[1][0] or 99999): best = (v, r)
        if best is None: print('no fix at', mis); break
        cur, res = best; print('fixed', mis, '->', res, flush=True)
    C.write_inputs(out, cur, f'nhfix of {sys.argv[1]} c {c}')
    print('final', res)
finally:
    e.close()
