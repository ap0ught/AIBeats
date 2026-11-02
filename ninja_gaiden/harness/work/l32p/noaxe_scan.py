"""replay the no-axe line (TAS rows 12030-12053, then rows file from 12054) for every tosser-1 spawn BF b; report top frame.
python work/l32p/noaxe_scan.py <rows from 12054>"""
import sys
sys.path.insert(0, 'work/l32p'); sys.path.insert(0, '.')
from lib import *
rows = list(TR[12030:12054]) + C.rows_of(sys.argv[1])
fc = core('states/mesen/l32p_tas12030.mst'); fc.save('base')
for b in range(256):
    fc.load('base'); fc.poke(0xBF, (b - 25) & 255); fc.save('p')
    r = fc.run_batch('p', [rows], record='all')[0]
    top = None; hit = None
    for i, s in enumerate(r.states):
        f = 12031 + i
        if top is None and ax(s) >= 1100 and s['y'] <= 96: top = f
        if hit is None and s['hp'] < 16: hit = f
    print(b, 'top', top, 'hit', hit, 'end', ax(r.states[-1]), r.states[-1]['y'], r.states[-1]['hp'], flush=True)
fc.close()
