"""Track K: when does the warp-room head pause (frames where its H does not advance by 2)?  For several input scripts.
    python u16k_pause.py "<spec>" ...   -> prints grab frame and the pause frames (r) up to r+226"""
import sys
from u16k_lib import *

e, lines = open_room("u16k_pause.log")
room = e.msave()
for spec in sys.argv[1:]:
    ins = []
    for part in spec.split(";"):
        n, b = part.split(":")
        ins += [b] * int(n)
    e.mload(room)
    prev, pauses, grab, over = None, [], None, None
    for r, b in enumerate(ins[:226]):
        e.step(bt(b), 1)
        t = rd(e)
        if t["hp"] < 47:
            break
        if grab is None and t["an"] in (88, 89):
            grab = r + 1
        if over is None and grab and t["x"] >= 126:
            over = (r + 1, t["x"], t["H"])
        if t["head"]:
            if prev is not None and t["head"][1] - prev != 2 and r + 1 > 73:
                pauses.append((r + 1, t["head"][1]))
            prev = t["head"][1]
    print(f"{spec[:60]:60s} grab {grab} over {over} head pauses (r, H): {pauses[:8]}", flush=True)
e.close()
