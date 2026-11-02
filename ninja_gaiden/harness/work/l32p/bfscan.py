"""For each BF value b at the tosser-1 spawn (TAS frame 12055), poke $BF at the TAS state 12030 and replay TAS rows
(optionally with w blank rows inserted at TAS row k). Report the frame Ryu reaches the wall top (X>=1098, y<=96) and
X >= 1161. python work/l32p/bfscan.py [w] [k]"""
import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
w = int(sys.argv[1]) if len(sys.argv) > 1 else 0
k = int(sys.argv[2]) if len(sys.argv) > 2 else 12040
rows = list(TR[12030:k]) + [()] * w + list(TR[k:12260])
fc = core('states/mesen/l32p_tas12030.mst')
fc.save('base')
res = []
for b in range(256):
    fc.load('base'); fc.poke(0xBF, (b - 25) & 255); fc.save('p')
    r = fc.run_batch('p', [rows], record='all', stops=[(0x6D, 'changed', 0)])[0]
    top = x1161 = None; hit = None; hp = None
    for i, s in enumerate(r.states):
        f = 12031 + i
        if top is None and ax(s) >= 1098 and s['y'] <= 96: top = f
        if x1161 is None and ax(s) >= 1161 and s['y'] <= 96: x1161 = f
        if hit is None and s['hp'] < 16: hit = f
    hp = r.states[-1]['hp']
    print(b, 'top', top, 'X1161', x1161, 'hit', hit, 'hp_end', hp, 'endX', ax(r.states[-1]), 'y', r.states[-1]['y'], flush=True)
fc.close()
