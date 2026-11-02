"""3-2 prep helpers (Mesen). Start = c1b 3-2 control (frame 11604)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
from ng.solve import common as C, legality as L
from ng import fastcore as F
import a56_common as A
HIST = C.rows_of('logs/l31_tas_c1b_poweron.inputs.txt')
F0 = len(HIST)  # 11604
MST = 'states/mesen/l32p_ctl.mst'
T = A.tas_trace(); TR = A.tas_rows()
TAS_CTL = 11434
def core(mst=None):
    fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open(mst or MST, 'rb').read()); fc.load('s')
    return fc
def legal_after(prefix, want, hist=None):
    en = L.Enforcer((list(hist or HIST) + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]
def ax(s): return C.abs_x(s)
