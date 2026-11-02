"""l62 chain (Mesen, from our real room-37 arrival states/mesen/l62_33589.mst; rows from 33,590):
room 37 rows file -> room 38 cycle -> room 39 rows (from change+23) -> room 40 rows (from change+off40) -> tail.
python work/l62/ch62.py r37rows r39rows [r40rows] [--off40 24] [--out file] [--tail Right] [--n 300]"""
import sys
sys.path.insert(0, 'work/l62')
from lib62 import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
OFF40 = opt('--off40', 24); OUT = opt('--out', ''); TAIL = row(opt('--tail', 'Right')); NT = opt('--n', 300); OFF39 = opt('--off39', 23)
F0 = 33589
fc = base(mst='states/mesen/l62_33589.mst')
def play(rows): return run(fc, rows)
def change(st, rm):
    return next((F0 + 1 + i for i, s in enumerate(st) if s['room6e'] == rm), None)
r37 = rows_file(a[0])
st = play(r37 + [()] * 40); c38 = change(st, 38); print('room 38 change', c38, flush=True)
rows = r37[:c38 - F0]; rows += [rows[-1], rows[-1]] + [()] * 21
cyc = [row(x) for x in 'Left A+Left A A+Right A+Right Right'.split()]
st = play(rows + cyc * 16 + [row('Left')] * 40); c39 = change(st, 39); print('room 39 change', c39, '(room 38', c39 - c38, 'f; TAS 98)', flush=True)
rows = rows + (cyc * 16 + [row('Left')] * 40)[:c39 - F0 - len(rows)]; rows += [rows[-1], rows[-1]]
rows += [()] * (c39 + OFF39 - 1 - F0 - len(rows))
r39 = rows_file(a[1])
st = play(rows + r39 + [()] * 40); c40 = change(st, 40); print('room 40 change', c40, '(room 39', c40 - c39 if c40 else None, 'f; TAS 444)', flush=True)
if c40:
    rows = (rows + r39)[:c40 - F0]; rows += [rows[-1], rows[-1]]
    rows += [()] * (c40 + OFF40 - 1 - F0 - len(rows))
    if len(a) > 2: rows += rows_file(a[2])
rows += [TAIL] * NT
st = play(rows)
ev = events(st, F0 + 1)
for e_ in ev:
    if 'spawn' not in e_ and 'gone' not in e_: print(e_)
s = st[-1]; print('end', F0 + len(st), RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'rm', s['room6e'], 'legal', legal_ok(rows) or 'ok')
if OUT: wrows(OUT, rows, f'l62 chain rows from 33590 (room 38 {c38}, 39 {c39}, 40 {c40})')
fc.close()
