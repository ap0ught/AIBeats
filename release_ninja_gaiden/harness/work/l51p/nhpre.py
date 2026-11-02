"""NesHawk check of 5-1 stage rows (row 1 = the 5-1 control row 22,125) on the TAS path with $BF after the control row = c:
ref4751/11_4-4_control + TAS rows to 22,124, poke $BF = c-1, then the rows. Prints hits, X/y every 20 rows, and the
first frame at X >= 600.   python work/l51p/nhpre.py <rows file> c1,c2,..."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'ng/stages'); sys.path.insert(0, 'work/l51p')
from ng.solve import common as C
from ng.mode import TICKS
import a56_common as A
rows = [tuple(sorted(r)) for r in C.rows_of(sys.argv[1])]
cs = [int(x) for x in sys.argv[2].split(',')]
TR = A.tas_rows()
e = C.open_emu('l51p_nhpre.log')
try:
    e.tick(TICKS)
    st = e.load('ref4751/11_4-4_control'); f00 = st['frame']
    e.run_ram([tuple(TR[f - 1]) for f in range(f00 + 1, 22125)])
    m = e.ram_all(); print('state after 22124: x', m[0x86], 'BF', m[0xBF], 'st', m[0x6D], 'hp', m[0x65], flush=True)
    base = e.msave()
    for c in cs:
        e.mload(base); e.poke(0xBF, (c - 1) % 256)
        _, rams = e.run_ram(rows)
        hp = 16; out = []; g = None
        for i, r in enumerate(rams):
            f = 22125 + i
            hi = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]; X = hi * 256 + r[0x51] + r[0x86]; y = r[0x8A]
            if r[0x65] != hp: out.append(f'hit {f} X {X} y {y} {hp}->{r[0x65]}'); hp = r[0x65]
            if g is None and X >= 600: g = f
        r = rams[-1]; hi = r[0x52] - 256 if r[0x52] >= 128 else r[0x52]
        print(f'c {c}: X600 at {g}; end frame {22124 + len(rams)} X {hi*256 + r[0x51] + r[0x86]} y {r[0x8A]} hp {r[0x65]} np {r[0x64]} item {r[0xC9]} | {out}', flush=True)
finally:
    e.close()
