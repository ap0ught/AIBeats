"""6-3/6-4 prep helpers (agent l63p). Frame = power-on row number (NesHawk frame k = after row k), TAS axis.
TAS: 6-3 control row 34,561; rooms 42 34,990 / 43 35,145 / 44 36,437; stage end 37,118, Start 37,124, 6-4a load 37,126,
control 37,278; kill 37,339; Start 37,933, 6-4b load 37,935, control 38,087; kill 38,188; Start 38,779, 6-5 load 38,781,
control 38,933; kill 39,084; P 39,525; END seen 39,530. Mesen TAS states: states/mesen/l63p_tas<f>.mst (mkst.py)."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l31t'); sys.path.insert(0, 'work/l63p')
import lib0  # l63p's (falls back to l61p's dumps)
sys.modules['lib0'] = lib0
sys.path.insert(1, 'work/l61p')
import importlib.util
_s = importlib.util.spec_from_file_location('l61lib', 'work/l61p/lib.py'); L61 = importlib.util.module_from_spec(_s); _s.loader.exec_module(L61)
from lib0 import TM, XY, TF0, NF
core = L61.core; legal_ok = L61.legal_ok; legalize_tas = L61.legalize_tas; P = L61.P; row = L61.row; T = L61.T; RXY = L61.RXY
FLD = L61.FLD; A = L61.A; K = L61.K; C = L61.C; F = L61.F
def pad(f): return TM(f)[0x2A]
def tas_mst(f): return f'states/mesen/l63p_tas{f}.mst'
import os, glob
def core_at(f):
    if os.path.exists(tas_mst(f)): return core(tas_mst(f))
    have = sorted(int(p.split('tas')[-1].split('.')[0]) for p in glob.glob('states/mesen/l63p_tas*.mst'))
    g = max(h for h in have if h <= f)
    fc = core(tas_mst(g))
    fc.step([pad(k) for k in range(g + 1, f + 1)], record='last'); fc.save('s'); fc._ka_slot = 's'
    return fc
def tas_xy(f): return XY(TM(f))
