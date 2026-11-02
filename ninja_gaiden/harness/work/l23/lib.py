"""2-3 agent helpers (Mesen). Base = 2-2 candidate l22_art_t12 (2-3 control 9172)."""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); from ng.solve import common as C, legality as L
from ng import fastcore as F
import importlib.util as _iu
_sp = _iu.spec_from_file_location('l22flib', 'work/l22f/lib.py'); L22 = _iu.module_from_spec(_sp); _sp.loader.exec_module(L22)  # 2-2 control Mesen state

POW = os.environ.get('L23_POW', 'logs/l22_art_t12_poweron.inputs.txt')
TAG = os.environ.get('L23_TAG', 't12')
HIST = C.rows_of(POW)
CTL = len(HIST)                      # 9172
MST_C = f'states/mesen/l23_{TAG}_ctl.mst'     # at control (after all HIST rows)
MST_P = f'states/mesen/l23_{TAG}_pre.mst'     # one row before control (HIST[:-1])

def make():
    if os.path.exists(MST_C) and os.path.exists(MST_P): return
    fc = L22.core()
    stage = HIST[L22.F0:]
    fc.step(stage[:-1], record='last'); fc.save('p'); fc.save_file('p', MST_P, frame=CTL - 1)
    fc.step(stage[-1:], record='last'); fc.save('c'); fc.save_file('c', MST_C, frame=CTL)
    r = fc.ram(); fc.close()
    print('control', CTL, 'X', r[0x86], 'y', r[0x8A], 'BF', r[0xBF], 'hp', r[0x65], 'np', r[0x64], 'item', r[0xC9], 'stage', r[0x6D])

def core(which='c'):
    make()
    fc = F.FastCore(boot_rows=None, ticks=True)
    fc.put('s', open(MST_C if which == 'c' else MST_P, 'rb').read()); fc.load('s')
    return fc

def row(s): return () if s in ('-', '') else tuple(sorted(s.split('+')))

def legal_after(prefix, want, hist=None):
    h = list(HIST if hist is None else hist)
    en = L.Enforcer((h + list(prefix))[-1900:])
    return [tuple(sorted(en.emit(w))) for w in want]

def trace(fc, rows, slot=7):
    """step rows one by one, return per-row tuples (Ryu x/y, boss x/hp, BF, ninpo, $66)."""
    out = []
    for r in rows:
        fc.step([r]); m = fc.ram()
        out.append(dict(x=m[0x86] + 256 * m[0x85], y=m[0x8A], hp=m[0x65], np=m[0x64], item=m[0xC9],
                        bhp=m[0x66], bx=m[0x460 + slot], by=m[0x480 + slot], bf=m[0xBF], st=m[0x6D],
                        btype=m[0x400 + slot] if True else 0))
    return out
