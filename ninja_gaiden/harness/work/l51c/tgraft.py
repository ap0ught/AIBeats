"""c3a rows to 24,270 + throw variant (a,b,c) rows to 24,391, then c2's end rows from 24,405 (X-2,596 arrival).
python work/l51c/tgraft.py "a,b,c" [out_poweron]"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
a, b, c = [None if x == 'None' else int(x) for x in sys.argv[1].split(',')]
out = sys.argv[2] if len(sys.argv) > 2 else None
F0 = 24270; MST = 'states/mesen/l51c_c3a_24270.mst'
rows = [tuple(sorted(r)) for r in C.rows_of('logs/l51_c3a_poweron.inputs.txt')]; hist = rows[:F0]
c2 = [tuple(sorted(r)) for r in C.rows_of('logs/l51_a_c2_poweron.inputs.txt')]
want = [{'Right'} for _ in range(24391 - F0)]
for f in (a, a + 1): want[f - F0 - 1] = {'A', 'Right'}
for t in (b, c):
    if t:
        for f in (t, t + 1):
            s = want[f - F0 - 1]; s.discard('Right'); s |= {'B', 'Up'}
full = enforce(want + [set(x) for x in c2[24404:24760]], hist)
fc = core(MST)
r = fc.run_batch('s', [full], record='all')[0]
hp = 9; trig = None
for i, s in enumerate(r.states):
    f = F0 + 1 + i
    if s['hp65'] != hp: print('hp', hp, '->', s['hp65'], 'at', f, RXY(s)); hp = s['hp65']
    if f == 24391: print('arrival', line(f, s))
    if s['e5c'] == 0: trig = f; print('TRIGGER', line(f, s)); break
print('5-2 control', trig + 280 if trig else None, 'legal', legal_ok(full, hist) or 'ok')
fc.close()
if out and trig:
    pw = rows[:F0] + full[:trig - F0]
    with open(out, 'w', encoding='utf-8') as fo:
        fo.write(f'# frames={trig + 280} l51c: c3a to {F0}, throw variant {sys.argv[1]}, c2 end from 24,405\n')
        for x in pw + [()] * 280: fo.write(('+'.join(x) if x else '') + '\n')
    print('wrote', out)
