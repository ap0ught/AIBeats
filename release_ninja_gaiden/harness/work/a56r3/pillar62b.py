"""Round 3: 6-2 room 37, leave the tall pillar's top to the LEFT like the record (jump off the left edge).
Replays round-1 rows to row N (N in 1205..1249), then Left x a, Left+A x h, Left x 90 (and variants with none
held in the air); reports room / min abs x / scroll / y per variant.  python work/a56r3/pillar62b.py"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages")); sys.path.insert(0, str(P))
import a56_common as C  # noqa
from ng.inputs import read_inputs  # noqa

rows0 = list(read_inputs(P / "states/tmp/a56_best_6-2_snap.inputs.txt"))
hist = list(read_inputs(P / "logs/a56_6-1_c8.inputs.txt"))[-1700:] + [()] * 150
e = C.open_emu("a56r3_pillarb.log")
try:
    from ng.mode import TICKS
    e.tick(TICKS)
    e.load("tmp/a56_6-1_c8_next")
    en0 = C.Enforcer(hist)
    pre = [en0.emit(r, retry=0) for r in rows0[:1205]]
    e.run(pre)
    res = []
    for N in range(1205, 1250, 4):
        if N > 1205:
            e.mload(sid)
            pre2 = [en0.emit(r, retry=0) for r in rows0[N - 4:N]]
            e.run(pre2)
        sid = e.msave()
        enN = en0.copy()
        for a in (0, 2, 4, 6, 8, 10, 12):
            for h in (2, 6, 12):
                for air in ("Left", None):
                    des = [("Left",)] * a + [("Left", "A")] * h + [(air,) if air else ()] * 20 + [("Left",)] * 70
                    e.mload(sid)
                    en = enN.copy()
                    rr = [en.emit(r, retry=0) for r in des]
                    tr = C.play_trace(e, rr)
                    in37 = [t for t in tr if t["room"] == 37]
                    minx = min(C.abs_x(t) for t in in37) if in37 else 0
                    rc = next((i for i, t in enumerate(tr) if t["room"] != 37), None)
                    res.append((minx, N, a, h, air, rc, min(t["y"] for t in tr), tr[-1]["y"], tr[-1]["hp"],
                                tr[-1]["scroll"], tr[-1]["scroll_scr"]))
        e.mload(sid)
        s = e.state()
        print("N", N, "ax", C.abs_x(s), "y", s["y"], "anim", s["anim"], "scroll", s["scroll"], s["scroll_scr"], flush=True)
    res.sort(key=lambda r: (r[0], r[1]))
    for r in res[:30]:
        print("RES", r)
    print("worst", res[-3:])
finally:
    e.close()
