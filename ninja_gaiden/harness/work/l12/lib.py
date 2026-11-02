"""1-2 lock round helpers: Mesen pool at the locked 1-2 control (frame 2474, NesHawk pads), candidate eval."""
import sys, os
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F
HIST = C.rows_of('logs/l11_rep_r1_poweron.inputs.txt')
MST = 'states/mesen/l12_ctl.mst'

def make_mst():
    if os.path.exists(MST): return
    fc = FS.boot(HIST, 'logs/l12_base.trace.csv')
    fc.save('s'); fc.save_file('s', MST, frame=len(HIST)); fc.close()

def pool(n=2):
    make_mst()
    P = F.FastPool(n, boot_rows=None, ticks=True)
    P.put_all('s', open(MST, 'rb').read())
    for wk in P.workers: wk.load('s')
    return P

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def legalize(want, hist=HIST):
    en = L.Enforcer(list(hist)[-1900:])
    return tuple(tuple(sorted(en.emit(w))) for w in want)

def run(P, cands, chunk=48):
    stops = [(0x66, '==', 0)]
    return FS.run_chunked(P, 's', cands, chunk=chunk, record='all', stops=stops, log=lambda s: None)

def kill(r):
    """offset (1-based row index) where boss hp hits 0, plus hp/ninpo there."""
    if r is None: return None
    for i, s in enumerate(r.states):
        if s['bosshp'] == 0:
            return i + 1, s['hp'], s['ninpo']
    return None
