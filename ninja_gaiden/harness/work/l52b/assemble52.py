"""Assemble the 5-2 power-on candidate on d3 (agent l52b).
python work/l52b/assemble52.py <out name> <room-26 rows file(s) from 26,529 ...> [--r25 file] [--extra N]
= rows 1-25,495 of logs/l52a_d3_poweron.inputs.txt + blank rows to 25,517 + room 24/25 rows (work/l52b/ch_d3_to26528.txt or a
rebuilt chain) + the room-26 files, then (Mesen) finds the trigger ($5C 2->0 in room 26) and pads blank rows to trigger + 278 and
Left on trigger + 279 (= 5-3 control row). Writes logs/<out name>.inputs.txt (utf-8, temp + rename, .backup) and prints the frames."""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
if os.environ.get('MINGB'):
    import fcka as _fk; d = list(_fk._init.__defaults__); d[-1] = float(os.environ['MINGB']); _fk._init.__defaults__ = tuple(d)
from ng.inputs import read_inputs, write_inputs
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
R2425 = opt('--r2425', 'work/l52b/ch_d3_to26528.txt')
name = a[0]; r26files = a[1:]
def load_rows(p):
    out = []
    for l in open(p):
        l = l.strip()
        if l.startswith('#'): continue
        out.append(() if l in ('', '-') else tuple(x for x in l.split('+') if x))
    return out
base = read_inputs('logs/l52a_d3_poweron.inputs.txt')
assert len(base) == 25495
rows = [tuple(r) for r in base] + [()] * (25517 - 25495) + load_rows(R2425)
n2425 = len(rows); print('rooms 24-25 rows end at', n2425)
for p in r26files: rows += load_rows(p)
# find the trigger in Mesen from the d3 state 25,517
fc = core('states/mesen/l52a_d3_25517.mst')
_, st, _ = fc.step(rows[25517:], record='all')
trig = None
for i, s in enumerate(st):
    f = 25518 + i
    if s['room6e'] == 26 and s['e5c'] == 0 and f > n2425: trig = f; break
if trig is None:
    s = st[-1]; print('NO TRIGGER; end', 25517 + len(st), RXY(s), 'hp', s['hp65'], 'np', s['np64']); fc.close(); sys.exit(1)
rows = rows[:trig]
ctl = trig + 279
rows += [()] * (ctl - 1 - trig) + [('Left',)]
fc.load('s') if False else None
fc.close()
fc = core('states/mesen/l52a_d3_25517.mst')
_, st, _ = fc.step(rows[25517:], record='all'); m = fc.ram(); fc.close()
X, y = XY(m)
print(f'trigger {trig}  5-3 control row {ctl}  rows {len(rows)}  end X {X} y {y} hp {m[0x65]} np {m[0x64]} item {m[0xC9]} room {m[0x6E]} BF {m[0xBF]}')
s_prev = None
for i, s in enumerate(st):
    if s_prev and (s['hp65'] != s_prev['hp65'] or s['np64'] != s_prev['np64'] or s['room6e'] != s_prev['room6e'] or s['item'] != s_prev['item']):
        print('  ', 25518 + i, 'X,y', RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'rm', s['room6e'])
    s_prev = s
write_inputs(f'logs/{name}.inputs.txt', rows, f'power-on: l52a d3 rows 1-25,495 (locked 1-24,997) + l52b rooms 24-26; trigger {trig}, 5-3 control {ctl} (Left)')
print('wrote', f'logs/{name}.inputs.txt')
