"""Track K: can the toad STAND on the rising head in the warp room (z 0, carried), so that a standstill dash jump (tap Right,
let go, Right+A: jump speed 4.7 px/f and run speed 3 px/f) can start from its top?  From the walk-mode line
(early_l6vault2_best.keep.json: hold-A climb, Right+A walks over the head top in contact) cut at several frames, release
to one of several pad states for 30 frames and watch z / anim / position relative to the head.
    python u16k_stand.py -> logs/fix/u16k_stand.txt"""
import json
from u16k_lib import *

pre_all = json.load(open(LOGS_DIR / "fix" / "early_l6vault2_best.keep.json"))["inputs"]
e, lines = open_room("u16k_stand.log")
room = e.msave()
out, stands = [], []
for cut in range(178, 201):
    e.mload(room)
    for b in pre_all[:cut]:
        e.step(bt(b), 1)
    t0 = rd(e)
    base = e.msave()
    for name, pad in (("-", ()), ("R", ("Right",)), ("L", ("Left",)), ("D", ("Down",)), ("U", ("Up",))):
        e.mload(base)
        tr, stood = [], 0
        for j in range(30):
            e.step(pad, 1)
            t = rd(e)
            if t["hp"] < 47 or not t["head"]:
                tr.append("X")
                break
            rel = t["H"] - t["head"][1]
            tr.append(f"{t['x']}/{rel}/z{t['z']}/a{t['an']}")
            if t["z"] == 0:
                stood += 1
        line = f"cut {cut} (x {t0['x']} rel {t0['H'] - t0['head'][1]} an {t0['an']}) pad {name}: stood {stood} | " + " ".join(tr[:30])
        out.append(line)
        if stood:
            stands.append(line)
            print(line[:300], flush=True)
    e.mfree(base)
open(LOGS_DIR / "fix" / "u16k_stand.txt", "w").write("\n".join(out) + "\n")
print(len(out), "runs;", len(stands), "with z == 0 at some frame")
e.close()
