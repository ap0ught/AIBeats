"""Chain prefix: control row 19,299 Left, 19,300 A+Left (as e1) + r4q rows (logs/a34/r4_43q_x1, from the TAS state 18,960)
shifted by 340; compare with the r4q dump frame by frame; report the first divergence; save rows/state."""
import sys; sys.path.insert(0, 'work/l43p')
from lib import *
H = hist_chain()
rr = [tuple(sorted(r)) for r in C.rows_of('logs/a34/r4_43q_x1.inputs.txt')]
d = open('work/l43p/r4q_ram.bin', 'rb').read()[4:]
def RM(f): i = f - 18961; return d[i*2048:(i+1)*2048]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
head = [('Left',), ('A', 'Left')]
rr = list(rr); rr[0] = ('A', 'Left')
rows = head + rr[:N]
print('legal on the chain:', legal_ok(rows, H) or 'PASS', '| r4q rows 1-3', [P(r) for r in rr[:3]])
fc = core(CHAIN_MST)
_, recs, _ = fc.step(rows, record='all')
first = None
for i, r in enumerate(recs):
    tf = 18959 + i; f = tf + LAG
    if tf < 18961: continue
    m = RM(tf); a = XY(r) + (r['hp65'], r['room6e']); b = XY(m) + (m[0x65], m[0x6E])
    if a[:2] != b[:2] or a[3] != b[3]:
        if first is None: first = tf; print('first divergence TAS-axis', tf, 'chain', f, 'ours', a, 'r4q', b)
    if tf % 25 == 0 or (first and tf < first + 5): print('  ', tf, f, P(rows[i]), 'ours', a, 'r4q', b)
fc.save('z'); fc.save_file('z', f'states/mesen/l43p_pre1_{19298 + len(rows)}.mst', frame=19298 + len(rows))
open(f'work/l43p/pre1_{19298 + len(rows)}.txt', 'w').write(chr(10).join('+'.join(r) for r in rows) + chr(10))
print('end chain frame', 19298 + len(rows), XY(recs[-1]), 'hp', recs[-1]['hp65'], 'np', recs[-1]['np64'], 'rm', recs[-1]['room6e'])
fc.close()
