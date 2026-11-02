"""4-2 helpers (agent l42a). Mesen at the locked 4-2 pre-control 16,997 (r15_c); stage row 1 = frame 16,998 (control row).
TAS lag 316: our frame f ~ TAS frame f-316 (Right on 16,998 = TAS 16,682 state except $BF 81 vs 21, $62, score)."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
import fcka
from ng.solve import common as C, legality as L, hitbox as H
from ng import fastcore as F
import a56_common as A
POW = 'logs/l41_r15_c_poweron.inputs.txt'
HIST = C.rows_of('work/l42a/h16997.inputs.txt')
MST = 'states/mesen/lock_42_pre.mst'
F0 = len(HIST)            # 16997
TAS_CTL = 16682
LAG0 = 316
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['thrown'] = 0xC8; FLD['bf'] = 0xBF; FLD['scr_hi'] = 0x52; FLD['scr_lo'] = 0x51
for _j in range(8): FLD[f't{_j}'] = 0x400 + _j
TR = A.tas_rows(); TT = A.tas_trace()

def core(mst=MST):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD); fc.put('s', open(mst, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def unud(w):
    w = set(w)
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return tuple(sorted(w))

def legal_after(prefix, want, hist=None):
    en = L.Enforcer((list(HIST if hist is None else hist) + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]

def enemies(m):
    s52 = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]; sc = s52 * 256 + m[0x51]
    return [(e['slot'], e['type'], sc + e['x'], e['y']) for e in H.enemies(m)]

def X(m):
    s52 = m[0x52] - 256 if m[0x52] >= 128 else m[0x52]
    return s52 * 256 + m[0x51] + m[0x86]
