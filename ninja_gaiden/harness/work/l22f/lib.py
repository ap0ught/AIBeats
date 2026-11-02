"""2-2 follow agent helpers (Mesen at the locked 2-2 control, frame 6130, NesHawk pads)."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F
import a56_common as A
HIST = C.rows_of('logs/l21f_fol_v4_poweron.inputs.txt')
F0 = len(HIST)  # 6130
MST = 'states/mesen/l22f_ctl.mst'
T = A.tas_trace(); TR = A.tas_rows()
TAS_CTL = 6104

def make_mst():
    if os.path.exists(MST): return
    fc = FS.boot(HIST, 'logs/l22f_base.trace.csv')
    fc.save('s'); fc.save_file('s', MST, frame=F0); fc.close()

def core():
    make_mst()
    fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open(MST, 'rb').read()); fc.load('s')
    return fc

def pool(n=2, mst=None):
    make_mst()
    P = F.FastPool(n, boot_rows=None, ticks=True)
    P.put_all('s', open(mst or MST, 'rb').read())
    for wk in P.workers: wk.load('s')
    return P

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def enf(prefix=()):
    en = L.Enforcer(list(HIST)[-1900:])
    for r in prefix: en.emit(r)
    return en

def legal_after(prefix, want):
    """legalize want after HIST+prefix (prefix assumed legal)."""
    en = L.Enforcer((list(HIST) + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]

def play(rows, stops=None, record='all'):
    fc = core()
    r = fc.run_batch('s', [list(rows)], record=record, stops=stops or [(0x6D, 'changed', 0)])
    fc.close()
    return r[0]

def ax(s): return C.abs_x(s)
