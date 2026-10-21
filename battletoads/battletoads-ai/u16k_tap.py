"""Track K: does a DOUBLE TAP of Right on the snake give sprint speed (spd 192)?  The record's toad crosses the head at ~3 px/f
(read frame by frame from his video: logs/fix/u16k_wr_z1.jpg, _z2.jpg).  From the vault2 line (jump-grab + hold-A climb) cut at
several frames, apply tap patterns and print x / spd / height relative to the head for 40 frames.
    python u16k_tap.py  -> logs/fix/u16k_tap.txt"""
import itertools, json
from u16k_lib import *

pre_all = json.load(open(LOGS_DIR / "fix" / "early_l6vault2_best.keep.json"))["inputs"]
e, lines = open_room("u16k_tap.log")
room = e.msave()
PAT = {
    "RA,-,RA": [("Right", "A"), (), ("Right", "A")],
    "RA,A,RA": [("Right", "A"), ("A",), ("Right", "A")],
    "R,-,RA": [("Right",), (), ("Right", "A")],
    "R,A,RA": [("Right",), ("A",), ("Right", "A")],
    "R,-,R": [("Right",), (), ("Right",)],
    "RA,-,R": [("Right", "A"), (), ("Right",)],
    "RA,A,R": [("Right", "A"), ("A",), ("Right",)],
    "RA,-,-,RA": [("Right", "A"), (), (), ("Right", "A")],
    "RA,A,A,RA": [("Right", "A"), ("A",), ("A",), ("Right", "A")],
    "RA,RA,-,RA": [("Right", "A"), ("Right", "A"), (), ("Right", "A")],
    "RA,RA,A,RA": [("Right", "A"), ("Right", "A"), ("A",), ("Right", "A")],
    "RA hold": [("Right", "A")],
}
out, hits = [], []
for cut in range(120, 190, 2):
    e.mload(room)
    for b in pre_all[:cut]:
        e.step(bt(b), 1)
    t0 = rd(e)
    base = e.msave()
    for name, pat in PAT.items():
        e.mload(base)
        seq = list(pat) + [pat[-1]] * 40
        tr, mx = [], 0
        for j, b in enumerate(seq[:40]):
            e.step(b, 1)
            t = rd(e)
            if t["hp"] < 47 or not t["head"]:
                tr.append("HURT" if t["hp"] < 47 else "nohead")
                break
            mx = max(mx, t["spd"])
            tr.append(f"{t['x']}/{t['spd']}/{t['H'] - t['head'][1]}/{t['an']}")
        line = f"cut {cut} (x {t0['x']} rel {t0['H'] - t0['head'][1]}) {name:11s} maxspd {mx}: " + " ".join(tr[:26])
        out.append(line)
        if mx >= 150:
            hits.append(line)
            print("SPRINT", line[:260], flush=True)
    e.mfree(base)
    open(LOGS_DIR / "fix" / "u16k_tap.txt", "w").write("\n".join(out) + "\n")
print(len(out), "trials;", len(hits), "with spd >= 150")
e.close()
