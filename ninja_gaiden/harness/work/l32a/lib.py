"""3-2 first-half helpers (Mesen at the locked 3-2 control 11,595, from l31_alt_b2r)."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
from ng.solve import common as C, legality as L, hitbox as H
from ng import fastcore as F
import a56_common as A
POW = 'logs/l31_alt_b2r_poweron.inputs.txt'
HIST = C.rows_of(POW)
MST = 'states/mesen/lock_32_ctl.mst'
F0 = len(HIST)            # 11595
TAS_CTL = 11434
LAG0 = 160                # our frame f ~ TAS frame f-160 (x 35 moving after both 11595 / 11435)
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['thrown'] = 0xC8; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51
TR = A.tas_rows(); TT = A.tas_trace()

def core(mst=MST):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD); fc.put('s', open(mst, 'rb').read()); fc.load('s')
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def legal_after(prefix, want, hist=None):
    en = L.Enforcer((list(HIST if hist is None else hist) + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]

def enemies(m):
    s52 = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]; sc = s52 * 256 + m[0x51]
    return [(e['slot'], e['type'], sc + e['x'], e['y']) for e in H.enemies(m)]

def X(m):
    s52 = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]
    return s52 * 256 + m[0x51] + m[0x86]
