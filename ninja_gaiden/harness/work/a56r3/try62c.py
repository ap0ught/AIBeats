import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C
from ng.inputs import read_inputs
N0 = int(sys.argv[1]); seqs = sys.argv[2:]
rows0 = list(read_inputs(P / "states/tmp/a56r3_62_r3c_best.inputs.txt"))
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1700:] + [()] * 150
e = C.open_emu("a56r3_try62.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    e.load("tmp/a56_6-1_c8_next")
    en0 = C.Enforcer(hist)
    e.run([en0.emit(r, retry=0) for r in rows0[:N0]])
    sid = e.msave()
    for sq in seqs:   # e.g. "Left+A*2,Left*6,Right*80"
        des = []
        for part in sq.split(","):
            b, n = part.split("*")
            des += [tuple(x for x in b.split("+") if x and x != "-")] * int(n)
        e.mload(sid); en = en0.copy()
        tr = C.play_trace(e, [en.emit(r, retry=0) for r in des])
        print(sq); print([(i, C.abs_x(t), t["x"], t["y"], t["anim"], t["scroll_flags"]) for i, t in enumerate(tr) if i % 4 == 0])
finally:
    e.close()
