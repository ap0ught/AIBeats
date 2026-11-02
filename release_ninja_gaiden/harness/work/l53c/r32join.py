"""room 32: entry grid row spec + landing L, then the legal TAS tail (ltas_28714_28843, frames 28715..) shifted; room-change frame.
python work/l53c/r32join.py cyc n m r"""
import sys
sys.path.insert(0, 'work/l53p')
from lib import *
U, L_, R, AL, AR = ('Up',), ('Left',), ('Right',), ('A', 'Left'), ('A', 'Right')
CYC = {'c2': [AL, AL, R, R, R, R, R, R], 'c2u': [AL, AL, R, R, R, R, R, R, U, U], 'c7': [AL, AL, R, R, R, R, R], 'up': [U]}
cn, n, m, r = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
hist = [row(l.strip()) for l in open('work/l53c/hist_tas28652.txt') if l.strip()]
ent = (CYC[cn] * 60)[:n] + [AL, AL] + [L_] * m + [R] * r + [AR, AR] + [R] * 60
tail = [row(l.strip()) for l in open('work/l53c/ltas_28714_28843.txt') if l.strip() and not l.startswith('#')]
fc = core('states/mesen/l53c_tas28652.mst'); fc.save('b'); fc._ka_slot = 'b'
st = fc.run_batch('b', [ent], record='all')[0].states
land = next(i for i, s in enumerate(st) if RXY(s)[1] == 160 and RXY(s)[0] >= 112 and s['coll'] & 0x30)
print('landing frame', 28653 + land, RXY(st[land]), 'xsub', st[land]['xsub'], 'TAS 28714', tas_xy(28714), TM(28714)[0x85] if False else '')
cands = []
for dl in range(-2, 4):          # extra Right rows before the tail (shift)
    rows = ent[:land + 1] + [R] * max(dl, 0) + tail[1 + max(-dl, 0):] + [()] * 30
    lg = legal_ok(rows, hist)
    cands.append((dl, rows, lg))
rr = fc.run_batch('b', [c[1] for c in cands], record='all')
for (dl, rows, lg), r_ in zip(cands, rr):
    ch = next((28653 + i for i, s in enumerate(r_.states) if s['room6e'] == 33), None)
    hp = min(s['hp65'] for s in r_.states)
    print('dl', dl, 'legal', lg or 'ok', 'room 33 at', ch, 'hpmin', hp, 'np end', r_.states[-1]['np64'])
    if ch and not lg:
        open(f'work/l53c/r32_{cn}_{n}_{m}_{r}_d{dl}.txt', 'w').write(f'# room 32 rows from 28653 (TAS axis), room 33 at {ch}\n' + '\n'.join(P(x) for x in rows[:ch - 28653 + 1]) + '\n')
fc.close()
