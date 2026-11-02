"""NesHawk transitions 6-3 -> 6-4a -> 6-4b -> 6-5 -> END on the TAS path (agent l63p).
From a ref4751 state, TAS rows to row K (inclusive), optional pokes, then for each Start row S: blank rows (Start on S, S+1),
direction D held from row L (default: load + 1). Reports: load ($6D change), control (first row after the load on which x moves),
END: P (first frame $63 == 0 in stage 21 after $66 == 0), E (first frame > P with $3E == 1), seen = E + 1.
python work/l63p/nh_trans63.py <state> K --start S1,S2|none [--dir Right] [--tasrows-to M] [--poke a=v,...] [--n N]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
a = sys.argv[1:]
def opt(name, d=None):
    if name in a:
        i = a.index(name); v = a[i + 1]; del a[i:i + 2]; return v
    return d
SS = opt('--start', 'none'); SS = [None if x == 'none' else int(x) for x in SS.split(',')]
D = opt('--dir', 'Right'); D = None if D == 'none' else D; TT = opt('--tasrows-to'); N = int(opt('--n', '900')); PK = opt('--poke')
RF = opt('--rows'); RS = int(opt('--rows-start', '0')); PP = opt('--prepoke'); stn, K = a[0], int(a[1])
TR = A.tas_rows()
def trow(f): return tuple(TR[f - 1]) if f - 1 < len(TR) else ()
e = C.open_emu('l63p_nhtrans63.log')
try:
    e.tick(TICKS)
    st = e.load(stn); f0 = st['frame']
    if RF:
        rr_ = [() if l.strip() in ('', '-') else tuple(sorted(l.strip().split('+'))) for l in open(RF) if not l.startswith('#')]
        e.run_ram([trow(f) for f in range(f0 + 1, RS)])
        for kv in (PP.split(',') if PP else []):
            ad, v = kv.split('='); e.poke(int(ad, 0), int(v, 0))
        e.run_ram(rr_[:K - RS + 1])
    else:
        e.run_ram([trow(f) for f in range(f0 + 1, K + 1)])
    if PK:
        for kv in PK.split(','):
            ad, v = kv.split('='); e.poke(int(ad, 0), int(v, 0))
    base = e.msave()
    for S in SS:
        e.mload(base)
        w = []
        for f in range(K + 1, K + 1 + N):
            r = set(trow(f)) if (TT and f <= int(TT)) else set()
            if S and f in (S, S + 1): r.add('Start')
            w.append(tuple(sorted(r)))
        _, rams = e.run_ram(w)
        st0 = rams[0][0x6D]; load = ctl = P = E = None; t_kill = None
        for i, r in enumerate(rams):
            f = K + 1 + i
            if load is None and r[0x6D] != st0: load = f
        if load and D:
            # replay with D held from load+1 to find control
            e.mload(base)
            w2 = [tuple(sorted(set(w[i]) | ({D} if K + 1 + i > load else set()))) for i in range(len(w))]
            _, rams2 = e.run_ram(w2)
            prev = None
            for i, r in enumerate(rams2):
                f = K + 1 + i
                if f > load + 50:
                    x = (r[0x51], r[0x52], r[0x86])
                    if prev is not None and x != prev and ctl is None: ctl = f
                    prev = x
        for i, r in enumerate(rams):
            f = K + 1 + i
            if r[0x6D] == 21 and r[0x66] == 0 and r[0x63] == 0 and P is None: P = f
            if P is not None and f > P and r[0x3E] == 1 and E is None: E = f
        m = rams[0]
        print(f'K {K} Start {S}: load {load} (K+{load - K if load else None}) control {ctl} (load+{ctl - load if ctl and load else None})'
              f' | at K+1: T {m[0x63]} t62 {m[0x62]} np {m[0x64]} 3E {m[0x3E]} BF {m[0xBF]} boss {m[0x66]} st {m[0x6D]}'
              + (f' | P {P} (K+{P - K}) E {E} seen {E + 1 if E else None}' if P else ''), flush=True)
finally:
    e.close()
