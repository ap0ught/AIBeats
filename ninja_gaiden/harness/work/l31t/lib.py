"""3-1 tas5 agent helpers (Mesen at the locked 3-1 control, frame 9993, NesHawk pads)."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F
import a56_common as A
HIST = C.rows_of('logs/l22_art_w10_to31_poweron.inputs.txt')
F0 = len(HIST)  # 9993
MST = 'states/mesen/l31_ctl.mst'
T = A.tas_trace(); TR = A.tas_rows()
TAS_CTL = 9829
LAG = F0 - TAS_CTL  # 164

def core(mst=None):
    fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open(mst or MST, 'rb').read()); fc.load('s')
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def legal_after(prefix, want):
    en = L.Enforcer((list(HIST) + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]

def play(rows, stops=None, record='all', fields=None):
    fld = dict(F._fields()); fld.update(fields or {})
    fc = F.FastCore(boot_rows=None, ticks=True, fields=fld); fc.put('s', open(MST, 'rb').read()); fc.load('s')
    r = fc.run_batch('s', [list(rows)], record=record, stops=stops or [(0x6D, 'changed', 0)])
    fc.close()
    return r[0]

def ax(s): return C.abs_x(s)
