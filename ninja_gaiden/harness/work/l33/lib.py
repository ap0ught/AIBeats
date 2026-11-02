"""3-3 Basaquer lock round helpers (Mesen). Candidates = 3-2 lock candidates (power-on to 3-3 control).
Re-apply on a new 3-2 candidate: add it to CANDS (power-on file + 3-2 stage rows), run mk.py <tag>."""
import sys, os, time
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C, legality as L, hitbox as H
from ng import fastcore as F
L32_MST = 'states/mesen/lock_32_ctl.mst'   # 3-2 control 11,595 (Mesen)
L32_F0 = 11595
CANDS = {
    'cB': dict(pow='logs/l32_a_cB_poweron.inputs.txt', stage='logs/l32_a_cB.inputs.txt', nh='l32_a_cB_end'),
    'cC': dict(pow='logs/l32_a_cC_poweron.inputs.txt', stage='logs/l32_a_cC.inputs.txt', nh='l32_a_cC_end'),
}
FLD = dict(F._fields()); FLD['eact'] = 0x73; FLD['thrown'] = 0xC8; FLD['bf'] = 0xBF
for i in range(8):
    FLD[f't{i}'] = 0x400 + i
FLD['bx'] = 0x467; FLD['by'] = 0x487

def mst(tag): return f'states/mesen/l33_{tag}_ctl.mst'
def hist(tag): return C.rows_of(CANDS[tag]['pow'])

def core(tag, fields=FLD):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=fields); fc.put('s', open(mst(tag), 'rb').read()); fc.load('s')
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def legal_after(prefix, want, h):
    en = L.Enforcer((list(h) + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]
