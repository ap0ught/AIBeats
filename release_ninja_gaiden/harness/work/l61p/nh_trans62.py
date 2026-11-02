"""NesHawk: plain stage changes 6-1 -> 6-2 and 6-2 -> 6-3 on the TAS path. From a ref4751 state, TAS rows to the trigger T,
then blank rows with a direction D held from row L (variants) and/or a 2-f Start at S; reports the first row on which Ryu's x moves
(= control row) and $BF / $62 there.
python work/l61p/nh_trans62.py <state> T D <L1,L2,..> [--start S1,S2]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
a = sys.argv[1:]
SS = []
if '--start' in a:
    i = a.index('--start'); SS = [int(x) for x in a[i + 1].split(',')]; del a[i:i + 2]
stn, T, D, LS = a[0], int(a[1]), a[2], [int(x) for x in a[3].split(',')]
TR = A.tas_rows()
e = C.open_emu('l61p_nhtrans62.log')
try:
    e.tick(TICKS)
    st = e.load(stn); f0 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f0 + 1, T + 1)])
    base = e.msave()
    END = T + 330
    for L in LS:
        for S in (SS or [None]):
            e.mload(base)
            w = [((D,) if f >= L else ()) for f in range(T + 1, END)]
            if S:
                for f in (S, S + 1): w[f - T - 1] = tuple(sorted(set(w[f - T - 1]) | {'Start'}))
            _, rams = e.run_ram(w)
            x0 = rams[0][0x86]; ctl = None; prev = x0
            for i, r in enumerate(rams):
                if i > 200 and r[0x86] != prev and ctl is None: ctl = T + 1 + i; rr = r
                prev = r[0x86]
            print(f'T {T} {D} from {L} Start {S}: control {ctl} (T+{ctl - T if ctl else None}) BF {rr[0xBF] if ctl else None} 62 {rr[0x62] if ctl else None}', flush=True)
finally:
    e.close()
