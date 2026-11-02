"""4-1 lock round helpers (Mesen). Our 4-1 control = 14,848 (q4, LOCKED 3-3); the control row = Right (stage row 0).
Stage rows file (for verify finish from NesHawk lock_41_pre, history work/l41/h14865.inputs.txt) = [Right] + rows."""
import sys, os, time
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
from ng.solve import common as C, legality as L, hitbox as H
from ng import fastcore as F
HISTF = 'work/l41/hq14847.inputs.txt'   # q4 (3-3 LOCKED); p4t: work/l41/h14865.inputs.txt
HIST = C.rows_of(HISTF)          # 14,847 rows
F0 = 14848                       # 4-1 control frame on q4 (p4t: 14,866)
TASOFF = F0 - 14569                     # our frame = TAS frame + 297 when in sync with the TAS/r2c axis
MST = 'states/mesen/l41q_ctl.mst'   # p4t: states/mesen/l41_ctl.mst
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['thrown'] = 0xC8; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51
FLD['pad2a'] = 0x2A

def core(mst=MST, fields=FLD):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=fields); fc.put('s', open(mst, 'rb').read()); fc.load('s')
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def hist_ctl(): return list(HIST) + [('Right',)]

def legal_after(prefix, want):
    en = L.Enforcer((hist_ctl() + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]

def X(m):
    return m[0x52] * 256 + m[0x51] + m[0x86]

def enemies(m):
    sc = m[0x52] * 256 + m[0x51]
    return [(e['slot'], e['type'], sc + e['x'], e['y']) for e in H.enemies(m)]
