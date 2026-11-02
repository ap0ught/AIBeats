"""l53c chain: rooms 31-33 + transition + 5-4 + 6-1 load from a state just before the room-31 control row.
python work/l53c/c53.py <F0|path.mst F0> [--poke '64=20,65=3'] [--out rows.txt] [--r31 file] [--r32 file] [--start54 k] [--nh]
F0 = frame after which the state is, = room-31 change + 23 (TAS 28,417). Rows built (our axis):
  room 31 rows (file, first row on F0+1, last row = room-32 change) -> blanks to room-32 control - 1 (= change + 23)
  -> room-32 rows (file rows from TAS 28,653) -> blanks to room-33 control - 1 (change + 22) -> Right to the trigger
  -> blanks, Start x2 on trigger + 5 -> blanks to 5-4 control - 1 (trigger + 159) -> Left + b13 (no Starts)
  -> Start x2 on kill + 594 -> blanks to 6-1 load + 3.
Prints events; writes the rows (from F0+1) to --out."""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
FLD['bh'] = 0x66
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
POKE = opt('--poke', ''); OUT = opt('--out', ''); R31 = opt('--r31', 'work/l53c/b_r31d.txt'); R32 = opt('--r32', 'work/l53c/r32_c2_16_13_1_d0.txt')
if a[0].endswith('.mst'):
    fc = core(a[0]); F0 = int(a[1])
else:
    F0 = int(a[0]); fc = core_at(F0)
for p in [p for p in POKE.split(',') if p]:
    k, v = p.split('='); fc.poke(int(k, 16), int(v))
fc.save('b'); fc._ka_slot = 'b'
def rd(fn): return [row(l.strip()) for l in open(fn) if l.strip() and not l.startswith('#')]
L, R, S = ('Left',), ('Right',), ('Start',)
r31, r32 = rd(R31), rd(R32)
b13 = [tuple(sorted(x for x in rr if x != 'Start')) for rr in rd('logs/a56_5-4_b13.inputs.txt')]
ev = []
def pad(rows, n):
    # blanks after a segment; a press held only 1 f on the last row is held 1 more (hold rule)
    out = [()] * n
    if n and rows and rows[-1] and (len(rows) < 2 or not set(rows[-1]) <= set(rows[-2])): out[0] = rows[-1]
    return out
def play(rows):
    st = fc.run_batch('b', [rows], record='all')[0].states
    return st
rows = list(r31)
st = play(rows + [()] * 40)
ch32 = next(F0 + 1 + i for i, s in enumerate(st) if s['room6e'] == 32)
ev.append(('room 32 change', ch32))
rows = rows[:ch32 - F0]; rows = rows + pad(rows, 23) + r32
st = play(rows + [()] * 40)
ch33 = next(F0 + 1 + i for i, s in enumerate(st) if s['room6e'] == 33)
ev.append(('room 33 change', ch33))
rows = rows[:ch33 - F0]; rows = rows + pad(rows, 22) + [R] * 300
st = play(rows)
trig = next(F0 + 1 + i for i, s in enumerate(st) if s['e5c'] == 4 and s['room6e'] == 33)
s_t = st[trig - F0 - 1]
ev.append(('5-3 trigger', trig, 'X', RXY(s_t), '$62', s_t['t62'], 'hp', s_t['hp65'], 'np', s_t['np64'], 'item', s_t['item']))
rows = rows[:trig - F0] + [()] * 4 + [S, S] + [()] * (159 - 6) + [L] + b13[:120]
st = play(rows + [()] * 700)
ctl = trig + 160
s_c = st[ctl - F0 - 2]
ev.append(('5-4 control row (trigger+160)', ctl, 'room', s_c['room6e'], 'X before/after', RXY(st[ctl - F0 - 2]), RXY(st[ctl - F0 - 1]),
           'hp', s_c['hp65'], 'np', s_c['np64'], 'item', s_c['item']))
kill = next(F0 + 1 + i for i, s in enumerate(st) if s['room6e'] == 34 and s['bh'] == 0 and F0 + 1 + i > ctl + 5)
s_k = st[kill - F0 - 1]
ev.append(('boss 0 (kill)', kill, 'ctl+', kill - ctl, 'timer', s_k['t63'], 'np', s_k['np64']))
rows = rows + [()] * (kill + 594 - F0 - 1 - len(rows)) + [S, S] + [()] * 10
st = play(rows)
ld = next((F0 + 1 + i for i, s in enumerate(st) if s['st6d'] == 16), None)
ev.append(('6-1 load ($6D 16)', ld, 'kill+', ld - kill if ld else None))
if ld is None:
    for k in range(595, 600):
        rr = rows[:kill + 594 - F0 - 1] + [()] * (k - 594) + [S, S] + [()] * 10
        st = play(rr); ld = next((F0 + 1 + i for i, s in enumerate(st) if s['st6d'] == 16), None)
        if ld: rows = rr; ev.append(('6-1 load with Start kill+', k, ld)); break
for e in ev: print(*e)
print('legal:', legal_ok(rows) or 'ok (no history)')
if OUT:
    open(OUT, 'w').write(f'# l53c rows from frame {F0 + 1}: rooms 31-33, 5-4, to the 6-1 load {ld}\n' + '\n'.join(P(x) for x in rows[:ld - F0 + 2]) + '\n')
fc.close()
