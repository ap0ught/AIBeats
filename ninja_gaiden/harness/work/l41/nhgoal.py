"""NesHawk: from a state, play each rows file N frames; first frame where <expr> holds (vars X,y,hp,np,room,item,stage).
python work/l41/nhgoal.py <state> <N> "<expr>" <rows...>"""
import sys
sys.path.insert(0, 'work/l41')
from lib import *
from ng.mode import TICKS
stn, N, ex = sys.argv[1], int(sys.argv[2]), sys.argv[3]
e = C.open_emu('l41_nhg.log')
try:
    e.tick(TICKS)
    for fn in sys.argv[4:]:
        rows = C.rows_of(fn); st = e.load(stn); f0 = st['frame']
        _, rams = e.run_ram(rows[f0 - F0:f0 - F0 + N])
        hit = None
        for j, m in enumerate(rams):
            if eval(ex, {}, dict(X=X(m), y=m[0x8A], hp=m[0x65], np=m[0x64], room=m[0x6E], item=m[0xC9], stage=m[0x6D])):
                hit = (f0 + j + 1, X(m), m[0x8A], m[0x65], m[0x64]); break
        r15 = next((f0 + j + 1 for j, m in enumerate(rams) if m[0x6E] == 15), None)
        print(fn, 'room15', r15, 'goal', hit, 'last', X(rams[-1]), rams[-1][0x8A], rams[-1][0x65], flush=True)
finally:
    e.close()
