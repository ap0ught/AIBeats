"""NesHawk: real 6-1 arrivals from a delayed 5-4 (d blank rows before the TAS's 5-4 rows, Start on kill+595) + the head start
pre61_32595 from the control row; (a) as is (its own c), (b) with $BF poked so that c = 84. Reports hits / rooms / end."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l61p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
HS = [l.strip() for l in open('work/l61p/pre61_32595.txt') if l.strip() and not l.startswith('#')]
HS = [() if r == '-' else tuple(r.split('+')) for r in HS]
DS = [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else [2, 5, 11]
e = C.open_emu('l61p_nharr2.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/15_5-4_control'); f0 = st['frame']
    base = e.msave()
    for d in DS:
        e.mload(base)
        w = [()] * d + [tuple(TR[f - 1]) for f in range(f0 + 1, 29330)]
        _, rams = e.run_ram(w)
        kill = next(f0 + 1 + i for i, r in enumerate(rams) if r[0x66] == 0 and r[0x6D] == 15)
        e.mload(base)
        S = kill + 595
        ww = (w + [()] * 2000)[:kill + 640 - f0]
        for f in range(29330 + d, kill + 641): ww[f - f0 - 1] = ()
        for f in (S, S + 1): ww[f - f0 - 1] = ('Start',)
        _, rams = e.run_ram(ww)
        load = next(f0 + 1 + i for i, r in enumerate(rams) if r[0x6D] == 16); ctl = load + 152
        e.run_ram([()] * (ctl - 1 - (kill + 640)))
        arr = e.msave()
        open(f'work/l61p/arr_d{d}.bin', 'wb').write(bytes(e.ram_all()))
        GR = sys.argv[sys.argv.index('--groups') + 1].split(',') if '--groups' in sys.argv else []
        MODES = ((() if '--noown' in sys.argv else ('own', 'c84')) + (('tasram', 'tasram_oam') if '--tasram' in sys.argv else ()) + tuple('g:' + g for g in GR)) if '--run' in sys.argv else ()
        for mode in MODES:
            e.mload(arr)
            m0 = e.ram_all()
            if mode == 'c84': e.poke(0xBF, 83)
            if mode.startswith('g:'):
                from lib0 import TM as _TM
                _t = _TM(30062); e.poke(0xBF, 83)
                for part in mode[2:].split('+'):
                    lo, hi = (int(x, 16) for x in part.split('-'))
                    for _a in range(lo, hi + 1):
                        if 0x100 <= _a < 0x200: continue
                        e.poke(_a, _t[_a])
            if mode.startswith('tasram'):
                from lib0 import TM as _TM
                _t = _TM(30062)
                for _a in range(0x800):
                    if 0x100 <= _a < 0x200: continue
                    if 0x200 <= _a < 0x300 and mode == 'tasram': continue
                    e.poke(_a, _t[_a])
            _, rams = e.run_ram(HS)
            hits = [ctl + i for i in range(1, len(rams)) if rams[i][0x65] < rams[i-1][0x65]]
            rooms = [ctl + i for i in range(1, len(rams)) if rams[i][0x6E] != rams[i-1][0x6E]]
            c = rams[0][0xBF]; r = rams[-1]
            from lib0 import XY as _XY
            with open(f'work/l61p/nh_arr_d{d}_{mode}.txt', 'w') as fo:
                for i, m in enumerate(rams): fo.write(f'{i + 1} {_XY(m)[0]} {_XY(m)[1]} {m[0x65]} {m[0x64]} {m[0xC9]} {m[0x6E]} {m[0xBF]} {m[0x2A]}' + chr(10))
            print(f'd {d} kill {kill} control {ctl} c {c} {mode}: hits(rel) {[h - ctl for h in hits[:4]]} rooms(rel) {[x - ctl for x in rooms]} end x {r[0x86]} y {r[0x8A]} hp {r[0x65]} np {r[0x64]} it {r[0xC9]} rm {r[0x6E]}', flush=True)
finally:
    e.close()
