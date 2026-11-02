"""Graft the 4-4 kill onto a 4-3 candidate (Mesen; confirm with nhgraft.py on NesHawk).
    python work/l44p/graft.py <4-3 power-on rows> <Mesen state> <state frame> <out tag>
The state must be on the candidate's own path (after row <state frame>), anywhere before its trigger. The tool plays the
candidate's rows to the trigger (first $5C 2 -> 0), keeps them up to the trigger row, adds blank rows to the pre-control
row (trigger + 278), reads v = $62, picks the jump delay d (v 24 -> 1, v 25 -> 2, else 0: the kill then lands on the timer
tick), appends the 4-4 rows (control row Left, A+Left x2, -, B+Right x2, blanks, 2-f Start at kill + 147 + 3 x timer, blanks) up to
the row before the 5-1 control, checks kill / load / 5-1 control with run_batch, and writes
logs/l44p_<tag>.inputs.txt (4-4 stage rows) + logs/l44p_<tag>_poweron.inputs.txt.
Test mode (no candidate): python work/l44p/graft.py --test <v>  (TAS pre-control state with $62 poked to v)."""
import sys, subprocess
sys.path.insert(0, 'work/l44p')
from lib import *

def stage_rows(d, start_row, n):
    w = [('Left',)] + [()] * d + [('A', 'Left'), ('A', 'Left'), (), ('B', 'Right'), ('B', 'Right')]
    w += [()] * (n - len(w))
    w[start_row - 1] = ('Start',); w[start_row] = ('Start',)
    return w

def pick_d(v): return v - 23 if v in (24, 25) else 0

def check(fc, slot, d):
    """returns (kill row, timer at kill, 5-1 control row) with the Start at kill + 594 (NesHawk-equal in run_batch)."""
    w = stage_rows(d, 700, 800)
    res = fc.run_batch(slot, [w[:60]], record='all')[0].states
    k = next(i + 1 for i, r in enumerate(res) if r['bhp'] == 0 and r['st6d'] == 11)
    tk = res[k + 1]['t63']            # the timer the tally sees (it can still tick on the row after the kill)
    w = stage_rows(d, k + 147 + 3 * tk, 800)
    res = fc.run_batch(slot, [w], record='all')[0].states
    load = next(i + 1 for i, r in enumerate(res) if r['st6d'] == 12)
    ctl = next(i + 1 for i, r in enumerate(res) if i + 1 > load and r['t62'] != res[load - 1]['t62'])
    return k, tk, load, ctl, w

if sys.argv[1] == '--test':
    fc = core(PRE)
    for v in [int(x) for x in sys.argv[2].split(',')]:
        fc.load('s'); fc.poke(0x62, v); fc.save('v')
        out = []
        for d in range(4):
            k, tk, load, ctl, _ = check(fc, 'v', d)
            out.append(f'd{d}: kill {k} t {tk} 5-1ctl row {ctl}')
        print('v', v, 'pick d', pick_d(v), ' | '.join(out), flush=True)
    fc.close(); sys.exit()

pf, mst, sf, tag = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
P = [tuple(sorted(r)) for r in C.rows_of(pf)]
fc = core(mst)
f = sf; trig = None; prev5c = fc.ram()[0x5C]
while f < len(P):
    f += 1
    fc.step([P[f - 1]]); m = fc.ram()
    if prev5c == 2 and m[0x5C] == 0 and m[0x6D] == 10:
        trig = f; break
    prev5c = m[0x5C]
assert trig, 'no trigger in the candidate rows'
CT = trig + 279
fc.step([()] * (CT - 1 - trig)); m = fc.ram()
v = m[0x62]
print(f'trigger {trig} -> 4-4 control row {CT}; pre-control: x {m[0x86]} hp {m[0x65]} np {m[0x64]} item {m[0xC9]} BF {m[0xBF]} $62 v {v} st {m[0x6D]}', flush=True)
fc.save('c')
d = pick_d(v)
k, tk, load, ctl, w = check(fc, 'c', d)
print(f'd {d}: kill stage row {k} (frame {CT + k - 1}) timer {tk}; 5-1 control row {ctl} (frame {CT + ctl - 1}); 4-4 = {ctl - 1} f', flush=True)
fc.close()
stage = w[:ctl - 1]
hist = P[:trig] + [()] * (CT - 1 - trig)
C.write_inputs(f'logs/l44p_{tag}.inputs.txt', stage, f'4-4 stage rows from control row {CT} (row 1 = Left); kill row {k}, 5-1 control {CT + ctl - 1}; v {v} d {d}')
C.write_inputs(f'logs/l44p_{tag}_poweron.inputs.txt', hist + stage, f'{pf} rows 1-{trig} + blanks + 4-4 rows; 5-1 control row {CT + ctl - 1} (Right)')
print(subprocess.run([sys.executable, 'check_inputs.py', f'logs/l44p_{tag}_poweron.inputs.txt', '--period', '5', '--hold', '2', '--release', '2',
                      '--windows', '600:109,1800:246'], capture_output=True, text=True).stdout[-400:])
