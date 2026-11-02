"""NesHawk: 4-4 kill + act-end Start + 5-1 control from ref4751/11_4-4_control (TAS path).
Variants: stage rows file (from the control row 21,353; row 1 = Left) + blank tail with a 2-f Start at frame S
(+ optional Right held from frame R). Reports frame numbers on the power-on axis (NesHawk frame k after row k):
kill (boss HP 0), timer at kill, load ($6D 11->12), first $62 change after load, first x change after load.
    python work/l44p/nh44.py <rows> <S1,S2,..> [--pokes 0xBF=v] [--right R]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
a = sys.argv[1:]
pk = {}
if '--pokes' in a:
    i = a.index('--pokes'); pk = {int(k, 0): int(v, 0) for k, v in (x.split('=') for x in a[i + 1].split(','))}; del a[i:i + 2]
RF = None
if '--right' in a:
    i = a.index('--right'); RF = int(a[i + 1]); del a[i:i + 2]
rows = [tuple(sorted(r)) for r in C.rows_of(a[0])]
SS = [int(x) for x in a[1].split(',')]
e = C.open_emu('l44p_nh44.log')
try:
    e.tick(TICKS)
    import a56_common as A
    TR = A.tas_rows()
    st = e.load('ref4751/10_4-3_control'); f00 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f00 + 1, 21353)]); f0 = 21352
    m = e.ram_all(); print('state frame', f0, 'x', m[0x86], 'BF', m[0xBF], '62', m[0x62], 'st', m[0x6D], 'hp', m[0x65], 'np', m[0x64], flush=True)
    # the state is AFTER row f0; our row 1 = TAS row 21,353
    skip = 0
    for k, v in pk.items(): e.poke(k, v)
    base = e.msave()
    for S in SS:
        e.mload(base)
        N = 22140 - f0
        w = list(rows[skip:]) + [()] * N
        w = w[:N]
        for f in (S, S + 1):
            w[f - f0 - 1] = ('Start',)
        if RF:
            for f in range(RF, 22140):
                w[f - f0 - 1] = tuple(sorted(set(w[f - f0 - 1]) | {'Right'}))
        _, rams = e.run_ram(w)
        kill = tk = load = c62 = cx = None
        for i, r in enumerate(rams):
            f = f0 + 1 + i
            if kill is None and r[0x66] == 0 and r[0x6D] == 11: kill = f; tk = r[0x63]
            if load is None and r[0x6D] == 12: load = f; t = r[0x62]; x0 = r[0x86]; xl = x0
            elif load:
                if c62 is None and r[0x62] != t: c62 = f
                if cx is None and r[0x86] != xl and f > load + 30: cx = (f, xl, r[0x86])
                xl = r[0x86]
        print(f'Start {S}: kill {kill} timer {tk} load {load} 62-change {c62} x-change {cx} BF@c62 {rams[c62 - f0 - 1][0xBF] if c62 else None}', flush=True)
finally:
    e.close()
