"""l53c: 5-4 fight + tally + cutscene on our line. From our state after row 29105 (room-33 Right from 28867, trigger 29099,
Start 29104-05), blank to 29258, then Left (29259 = control) + b13's rows (TAS 29261.. shifted by -1) without b13's Starts,
then ONE Start (2 f) at row s. Report boss-0 frame, timer at kill, tally end, 6-1 load ($6D 16), for each s and for $62 pokes."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
L, R, S = ('Left',), ('Right',), ('Start',)
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
base = [()] * 23 + [R] * (29099 - 28867 + 1) + [()] * 4 + [S, S]
fc.step(base, record='last'); fc.save('r'); fc._ka_slot = 'r'
r = fc.ram(); print('after 29105: t62', r[0x62], 't63', r[0x63], 'BF', r[0xBF], 'np', r[0x64], 'it', r[0xC9])
b13 = [row(l.strip()) for l in open('logs/a56_5-4_b13.inputs.txt') if not l.startswith('#')]
b13 = [tuple(sorted(x for x in rr if x != 'Start')) for rr in b13]
fight = [()] * (29258 - 29105) + [L] + b13[:600]            # rows 29106 .. ; b13[0] = TAS 29261 -> ours 29260
def run(slot, srow, extra=0):
    rows = fight[:]
    n = srow - 29106
    rows = (rows + [()] * (n + 200 - len(rows)))[:n + 200]
    rows[n] = S; rows[n + 1] = S
    st = fc.run_batch(slot, [rows], record='all')[0].states
    kill = tl = ld = None
    for i, s in enumerate(st):
        f = 29106 + i
        m = s
        if kill is None and s['room6e'] == 34 and f > 29270 and fc_boss(s) == 0: kill = (f, s['t63'], s['t62'])
        if ld is None and s['st6d'] == 16: ld = f
    return kill, ld
def fc_boss(s): return s['bh']
fc.close()
FLD['bh'] = 0x66
fc = core_at(28843); fc.save('b')
fc.step(base, record='last'); fc.save('r'); fc._ka_slot = 'r'
for srow in range(29895, 29915):
    print('Start at', srow, '->', run('r', srow), flush=True)
for v in (0, 5, 10, 15, 19, 20, 21, 25, 30, 35, 40, 45, 50, 55, 59, 60, 61):
    fc.load('r'); fc.poke(0x62, v); fc.save(f'p{v}')
    print('poke $62 =', v, '->', [run(f'p{v}', s) for s in (29908, 29911)], flush=True)
fc.close()
