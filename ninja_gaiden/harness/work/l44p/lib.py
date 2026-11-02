"""4-4 prep helpers (agent l44p). Frame = power-on row number (NesHawk frame k after row k).
TAS 4-4: control row 21,353 (Left moves x 32 -> 31), kill (boss HP 0) after row 21,376, Start 21,971, 5-1 load 21,973,
5-1 control 22,124.  Mesen states: states/mesen/l44p_tas21352.mst (pre-control), l44p_tas21353.mst (after the Left row)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
import a56_common as A
TR0 = A.tas_rows()
def T(f): return tuple(sorted(TR0[f - 1]))
FLD = dict(F._fields()); FLD['bf'] = 0xBF; FLD['hp65'] = 0x65; FLD['np64'] = 0x64; FLD['item'] = 0xC9
FLD['st6d'] = 0x6D; FLD['x86'] = 0x86; FLD['y8a'] = 0x8A; FLD['bhp'] = 0x66; FLD['t63'] = 0x63; FLD['t62'] = 0x62
FLD['eact'] = 0x73
for _j in range(8):
    FLD[f't{_j}'] = 0x400 + _j
PRE = 'states/mesen/l44p_tas21352.mst'
CTL = 'states/mesen/l44p_tas21353.mst'

def core(mst=PRE):
    fc = F.FastCore(boot_rows=None, ticks=True, fields=FLD)
    fc.put('s', open(mst, 'rb').read()); fc.load('s'); fc._ka_slot = 's'
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))
def P(r): return '+'.join(sorted(r)) if r else '-'
