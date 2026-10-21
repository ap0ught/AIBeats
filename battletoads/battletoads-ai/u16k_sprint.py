"""Track K: SPRINT jump at the snake (the record's toad flies at the snake at ~3 px/f from the spawn spot, read frame by frame
from his video).  From the room root: idle to r=rj, Right, -, Right x k (double tap = run), Right+A x a, then hold Right+A.
Print x / spd / rel / anim per frame, to see whether the run speed (192) survives the grab and the climb.
    python u16k_sprint.py  -> logs/fix/u16k_sprint.txt"""
import itertools, json
from u16k_lib import *

e, lines = open_room("u16k_sprint.log")
room = e.msave()
out = []
for rj, k, a in itertools.product((96, 100, 104, 108, 112, 116), (0, 1, 2, 3, 5), (6, 12, 20)):
    e.mload(room)
    seq = [()] * rj + [("Right",), ()] + [("Right",)] * k + [("Right", "A")] * a + [("Right", "A")] * 120
    tr, grab, over, mx_after = [], None, None, 0
    for r, b in enumerate(seq[:230]):
        e.step(b, 1)
        t = rd(e)
        if t["hp"] < 47:
            tr.append("HURT")
            break
        rel = (t["H"] - t["head"][1]) if t["head"] else None
        if r >= rj:
            tr.append(f"{r + 1}:{t['x']}/{t['spd']}/{rel}/{t['an']}/z{t['z']}")
        if grab is None and t["an"] in (88, 89):
            grab = (r + 1, t["x"], t["H"], rel, t["spd"])
        if grab:
            mx_after = max(mx_after, t["spd"])
        if over is None and grab and t["x"] >= 126 and t["head"] and t["head"][1] < 7758:
            over = (r + 1, t["x"], t["H"], rel, t["spd"], t["an"])
    line = f"rj {rj} k {k} a {a}: grab {grab} over {over} maxspd after grab {mx_after} | " + " ".join(tr[:150])
    out.append(line)
    print(line[:330], flush=True)
    open(LOGS_DIR / "fix" / "u16k_sprint.txt", "w").write("\n".join(out) + "\n")
e.close()
