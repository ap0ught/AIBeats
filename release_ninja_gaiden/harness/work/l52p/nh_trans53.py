"""NesHawk: 5-2 -> 5-3 transition on the TAS path (ref4751/13_5-2_control + TAS rows to 26,320): trigger ($5C 2->0), load
($6D 13->14), Ryu x per frame around the 5-3 control row, Left early / Start variants, Right / A on the control row."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l52p_nhtrans.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/13_5-2_control'); f00 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f00 + 1, 26321)]); base = e.msave()
    def run(name, lf, start=None, ctl=None, d='Left'):
        e.mload(base)
        rows = [tuple(TR[f - 1]) for f in range(26321, 26329)]
        for f in range(26329, 26640):
            r = (d,) if f >= lf else ()
            if start and f in (start, start + 1): r = ('Start',)
            if ctl and f == ctl[0]: r = ctl[1]
            rows.append(r)
        _, rams = e.run_ram(rows)
        trig = next(26321 + i for i, m in enumerate(rams) if m[0x5C] == 0)
        load = next(26321 + i for i, m in enumerate(rams) if m[0x6D] == 14)
        xs = [(26321 + i, m[0x86]) for i, m in enumerate(rams) if 26604 <= 26321 + i <= 26614]
        mv = next((26321 + i for i, m in enumerate(rams) if m[0x6D] == 14 and i and m[0x86] != rams[i-1][0x86]), None)
        print(f'{name:32s} trigger {trig} load {load} first x move {mv} x {xs} BF@26608 {rams[26608-26321][0xBF]} hp {rams[-1][0x65]} np {rams[-1][0x64]} it {rams[-1][0xC9]}', flush=True)
    run('Left from 26608 (TAS)', 26608)
    run('Left from 26607', 26607)
    run('Left from 26609', 26609)
    run('Left from 26400', 26400)
    run('Left from 26330', 26330)
    run('Right from 26608', 26608, d='Right')
    run('Start 26330 + Left 26608', 26608, 26330)
    run('Start 26460 + Left 26608', 26608, 26460)
    run('Start 26600 + Left 26608', 26608, 26600)
finally:
    e.close()
