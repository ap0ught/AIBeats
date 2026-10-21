"""Track K: the portal's pull-in.  K6 (rj 93) touches the portal at x 416 and the warp animation takes 161 frames from $E50D
to the level-byte change; the rj 94 line touches at x 419 and takes 156 (L6c: x 418, 156).  Scan: release Right (or both)
for ONE frame somewhere on the ledge (Right, -, Right is a double tap, the run resumes) to shift the touch x.
Reports touch frame/x, $E50D frame and the frame the level byte leaves 8 (no presses after the touch).
    python u16k_ledge.py -> logs/fix/u16k_ledge.txt"""
import json
from u16k_lib import *

e, lines = open_room("u16k_ledge.log")
room = e.msave()
out, rows = [], []
for rj in (93, 94, 95):
    base_ins = [""] * rj + ["Right", ""] + ["Right+A"] * 400
    e.mload(room)
    for b in base_ins[:238]:
        e.step(bt(b), 1)
    base = e.msave()
    cases = [(None, None, None)] + [(f, rel, None) for f in range(244, 266) for rel in ("A", "", "Right")] \
        + [(f, "A", f2) for f in range(246, 258, 2) for f2 in range(f + 2, 262, 2)]
    for f, rel, f2 in cases:
        e.mload(base)
        touch, e50d, lvl, land = None, None, None, None
        for r in range(238, 470):
            b = "Right+A"
            if f is not None and (r == f or r == f2):
                b = rel
            if touch:
                b = ""
            e.step(bt(b), 1)
            t = rd(e)
            m = t["m"]
            if t["hp"] < 47:
                break
            if land is None and t["z"] == 0:
                land = (r + 1, t["x"])
            if touch is None and land and t["spd"] == 0 and t["x"] >= 408 and t["z"] == 0:
                touch = (r + 1, t["x"])
            if e50d is None and t["rtn"] == 0xE50D:
                e50d = r + 1
            if m[0x10] != 8:
                lvl = r + 1
                break
        line = f"rj {rj} release {rel!r}@{f}{'+' + str(f2) if f2 else ''}: land {land} touch {touch} E50D {e50d} level byte leaves 8 at r+{lvl}"
        out.append(line)
        rows.append((lvl or 9999, line))
        if f is None:
            print(line, flush=True)
    e.mfree(base)
rows.sort()
print("\n".join(l for _, l in rows[:25]))
open(LOGS_DIR / "fix" / "u16k_ledge.txt", "w").write("\n".join(out) + "\n")
e.close()
