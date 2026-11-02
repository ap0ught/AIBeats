"""prefix = base rows with waits up to `cut` (new axis), then c1 rows cut+shift .. 24,404 (the X-2,596 arrival), then the
rows of an end file from 24,405 on. Reports the trigger and the 5-2 control (= trigger + 279; see LOCKED_CHAIN).
python work/l51c/graft.py "s:w,..." cut shift endfile [out_poweron]"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
F0 = 23663; MST = 'states/mesen/l51c_c1_23663.mst'
spec = [tuple(map(int, x.split(':'))) for x in sys.argv[1].split(',') if x]
cut, shift, endf = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
out = sys.argv[5] if len(sys.argv) > 5 else None
rows = c1rows(); hist = rows[:F0]
endr = [tuple(sorted(r)) for r in C.rows_of(endf)]
base = [set(r) for r in rows[F0:24200]] + tasleg(23671, 24150)
want = list(base)
for s, w in sorted(spec, reverse=True):
    k = s - F0 - 1; want = want[:k] + [set()] * w + want[k:]
want = want[:cut - F0] + [set(r) for r in rows[cut + shift:24404]]
arr = F0 + len(want)
want += [set(r) for r in endr[24404:]]
cand = enforce(want, hist)
lg = legal_ok(cand, hist)
print('arrival frame', arr, 'legal:', lg or 'ok', 'enforce changed rows:', sum(1 for a, b in zip(cand, want) if set(a) != b))
fc = core(MST)
r = fc.run_batch('s', [cand], record='all')[0]
hp = 12; trig = None
for i, s in enumerate(r.states):
    f = F0 + 1 + i; X, y = RXY(s)
    if s['hp65'] != hp: print('hp', hp, '->', s['hp65'], 'at', f, X, y); hp = s['hp65']
    if f == arr: print('arrival', line(f, s))
    if s['e5c'] == 0 and trig is None: trig = f; print('TRIGGER', f, line(f, s)); break
print('5-2 control (file length = trigger + 280, as c1/c2)', trig + 280 if trig else None)
fc.close()
if out and trig:
    pw = rows[:F0] + cand[:trig - F0]
    with open(out, 'w', encoding='utf-8') as fo:
        fo.write(f'# frames={trig + 280} l51c: c1 rows to {F0}, bird-phase waits {sys.argv[1]}, end {endf}\n')
        for x in pw + [()] * 280: fo.write(('+'.join(x) if x else '') + '\n')
    print('wrote', out)
