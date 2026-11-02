"""NesHawk: 5-4 kill -> act-end cutscene -> Start -> 6-1 load -> 6-1 control, from ref4751/15_5-4_control (TAS path).
Variants: d blank rows inserted before the TAS's 5-4 rows (delays the fight), a 2-f Start at frame S (power-on axis),
Left held from frame L (default: from the load). Reports kill (boss HP 0), timer at kill+1, load ($6D 15->16),
control (first row on which Left moves Ryu), $BF / $62 on the control row.
    python work/l61p/nh_trans61.py <d1,d2,..> <S1,S2,..|k:a:b (S = kill + k for k in a..b)> [--left L] [--pokes 0xBF=v]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
a = sys.argv[1:]
pk = {}
if '--pokes' in a:
    i = a.index('--pokes'); pk = {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in a[i + 1].split(','))}; del a[i:i + 2]
LF = None
if '--left' in a:
    i = a.index('--left'); LF = int(a[i + 1]); del a[i:i + 2]
DS = [int(x) for x in a[0].split(',')]
spec = a[1]
TR = A.tas_rows()
e = C.open_emu('l61p_nhtrans.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/15_5-4_control'); f0 = st['frame']
    for k, v in pk.items(): e.poke(k, v)
    base = e.msave()
    END = 30160
    for d in DS:
        # first find the kill with no Start
        e.mload(base)
        w = [()] * d + [tuple(TR[f - 1]) for f in range(f0 + 1, 29330)]
        _, rams = e.run_ram(w)
        kill = None
        for i, r in enumerate(rams):
            if r[0x66] == 0 and r[0x6D] == 15: kill = f0 + 1 + i; tk = rams[i + 1][0x63] if i + 1 < len(rams) else None; break
        if spec.startswith('k:'):
            _, ka, kb = spec.split(':'); SS = [kill + k for k in range(int(ka), int(kb) + 1)]
        else: SS = [int(x) for x in spec.split(',')]
        for S in SS:
            e.mload(base)
            N = END - f0
            ww = (list(w) + [()] * N)[:N]
            for f in range(29330 + d, END): ww[f - f0 - 1] = ()
            for f in (S, S + 1): ww[f - f0 - 1] = ('Start',)
            _, rams = e.run_ram(ww[:S + 400 - f0])
            load = None
            for i, r in enumerate(rams):
                f = f0 + 1 + i
                if load is None and r[0x6D] == 16: load = f; break
            ctl = None
            if load:
                e.mload(base)
                _, r0 = e.run_ram(ww[:load + 200 - f0])
                e.mload(base)
                L0 = LF if LF else load
                wl = list(ww)
                for f in range(L0, END): wl[f - f0 - 1] = tuple(sorted(set(wl[f - f0 - 1]) | {'Left'}))
                _, rams = e.run_ram(wl[:load + 200 - f0])
                for i in range(load - f0 - 1, len(rams)):
                    if rams[i][0x86] != r0[i][0x86]: ctl = f0 + 1 + i; r = rams[i]; break
            print(f'd {d} kill {kill} timer {tk} Start {S} (kill+{S - kill}) load {load} (S+{load - S if load else None}) control {ctl}'
                  + (f' (load+{ctl - load}, kill+{ctl - kill}) BF {r[0xBF]} 62 {r[0x62]} x {r[0x86]} hp {r[0x65]} np {r[0x64]} it {r[0xC9]}' if ctl else ''), flush=True)
finally:
    e.close()
