"""c3a rows to 24,270 + stage-A throws (a,b,c) to 24,400 + stage-B (p,w,d) [+ knockback rows], until Ryu stands on
pillar B at X >= 2,694 (frame T), then c2's rows from 24,503 (c2's jump off the pillar). Run to the trigger.
python work/l51c/pgraft.py "a,b,c" "p,w,d" [kb] [out_poweron]   kb: rows during the knockback: R (Right) or N (blank)"""
import sys; sys.path.insert(0, 'work/l51c')
from lc import *
a, b, c = [None if x == 'None' else int(x) for x in sys.argv[1].split(',')]
p, w, d = map(int, sys.argv[2].split(','))
kb = sys.argv[3] if len(sys.argv) > 3 else 'R'
out = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
F0 = 24270; MST = 'states/mesen/l51c_c3a_24270.mst'
rows = [tuple(sorted(r)) for r in C.rows_of('logs/l51_c3a_poweron.inputs.txt')]; hist = rows[:F0]
c2 = [tuple(sorted(r)) for r in C.rows_of('logs/l51_a_c2_poweron.inputs.txt')]
END = 24400
want = [{'Right'} for _ in range(END - F0)]
for f in (a, a + 1): want[f - F0 - 1] = {'A', 'Right'}
for t in (b, c):
    if t:
        for f in (t, t + 1):
            s = want[f - F0 - 1]; s.discard('Right'); s |= {'B', 'Up'}
want += [{'Right'}] * (p - END) + [set()] * w + [{'Right'}] * d + [{'A', 'Right'}] * 2
fc = core(MST)
# find the knockback start and the frame on top at X >= 2694 by stepping
tail = []
for extra in range(0, 120):
    rr = enforce(want + tail, hist)
    r = fc.run_batch('s', [rr], record='last')[0]; s = r.states[-1]; X, y = RXY(s)
    if y == 128 and X >= 2694 and not s['rf84'] & 4: break
    inkb = s['inv95'] > 40 and s['rf84'] & 4
    tail.append(set() if (kb == 'N' and inkb) else {'Right'})
T = F0 + len(want) + len(tail)
print('on top at X>=2694:', T, X, y, 'hp', s['hp65'], '(c3a: 24,490)')
import os
if os.environ.get('SAVE'):
    tag = os.environ['SAVE']; rr = enforce(want + tail, hist)
    r = fc.run_batch('s', [rr], record='last', keep=True, prefix='o')[0]; fc.save_file('o1', f'states/mesen/l51c_{tag}_{T}.mst', T)
    with open(f'work/l51c/h_{tag}_{T}.inputs.txt', 'w', encoding='utf-8') as fo:
        fo.write(f'# frames={T} l51c {tag}' + chr(10))
        for x in rows[:F0] + rr: fo.write(('+'.join(x) if x else '') + chr(10))
    print('saved', tag, T)
endm = sys.argv[5] if len(sys.argv) > 5 else 'c2'
endrows = [set(x) for x in c2[24502:24760]] if endm == 'c2' else tasleg(int(endm), int(endm) + 260)
full = enforce(want + tail + endrows, hist)
r = fc.run_batch('s', [full], record='all')[0]
hp = 9; trig = None
for i, s in enumerate(r.states):
    f = F0 + 1 + i
    if s['hp65'] != hp: print('hp', hp, '->', s['hp65'], 'at', f, RXY(s)); hp = s['hp65']
    if s['e5c'] == 0: trig = f; print('TRIGGER', line(f, s)); break
    if f % 10 == 0 and f > T: print(line(f, s), '|', P(full[i]))
print('5-2 control', trig + 280 if trig else None, 'legal', legal_ok(full, hist) or 'ok')
fc.close()
if out and trig:
    pw = rows[:F0] + full[:trig - F0]
    with open(out, 'w', encoding='utf-8') as fo:
        fo.write(f'# frames={trig + 280} l51c: c3a to {F0}, throws {sys.argv[1]}, pillar-B bird {sys.argv[2]} kb {kb}, c2 end from 24,503\n')
        for x in pw + [()] * 280: fo.write(('+'.join(x) if x else '') + '\n')
    print('wrote', out)
