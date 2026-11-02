"""NesHawk: 5-1 -> 5-2 transition on the TAS path (ref4751/12_5-1_control + TAS rows to 24,140): trigger ($5C 2->0), load
($6D 12->13), Ryu x per frame around the 5-2 control row, Left early / Start variants."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
TR = A.tas_rows()
e = C.open_emu('l51p_nhtrans.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/12_5-1_control'); f00 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f00 + 1, 24141)]); base = e.msave()
    def run(name, lf, start=None):
        e.mload(base)
        rows = [tuple(TR[f - 1]) for f in range(24141, 24148)]
        for f in range(24148, 24436):
            r = ('Left',) if f >= lf else ()
            if start and f in (start, start + 1): r = ('Start',)
            rows.append(r)
        _, rams = e.run_ram(rows)
        trig = next(24141 + i for i, m in enumerate(rams) if m[0x5C] == 0)
        load = next(24141 + i for i, m in enumerate(rams) if m[0x6D] == 13)
        xs = {24141 + i: m[0x86] for i, m in enumerate(rams) if 24424 <= 24141 + i <= 24432}
        print(f'{name:28s} trigger {trig} load {load} x {xs} BF@24435 {rams[-1][0xBF]}', flush=True)
    run('Left from 24427 (TAS)', 24427)
    run('Left from 24426', 24426)
    run('Left from 24300', 24300)
    run('Left from 24428', 24428)
    run('Start 24150 + Left 24427', 24427, 24150)
    run('Start 24280 + Left 24427', 24427, 24280)
finally:
    e.close()
