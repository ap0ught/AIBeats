"""3-1 alt agent helpers (Mesen at the locked 3-1 control 9,993)."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C, legality as L, hitbox as H
from ng import fastcore as F
import a56_common as A
POW = 'logs/l22_art_w10_to31_poweron.inputs.txt'
HIST = C.rows_of(POW)
MST = 'states/mesen/lock_31_ctl.mst'
if os.environ.get('L31_PRE'):          # start one row earlier (row 9,993 = 3-1 control frame, free to set to Right)
    HIST = HIST[:-1]; MST = 'states/mesen/l31alt_pre.mst'
F0 = len(HIST)            # 9993 (9992 with L31_PRE)
TAS_CTL = 9829            # TAS 3-1 control frame
LAG0 = F0 - TAS_CTL       # 164
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['thrown'] = 0xC8; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51

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
