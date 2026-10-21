"""EARLY track (2026-10-09): Karnath warp room, part 4 - how EARLY can the toad be over the snake's head?

early_l6vault2.py: jump-grab at r+98 from x 84, then the beam mostly held A; 18 px above the head's coordinate at r+186;
Right+A there walks over the head to x 128 by r+200.  The head starts rising at r+71, so an earlier jump could grab
right under (or at) the head.  Scan: walk to x0, at r = rj press Right+A for a frames, then one of three climbs
(hold A / hold Right+A / Left+A x4, Right+A x4) until the toad is `top` px above the head's coordinate, then hold
Right+A; report the first frame the toad is right of the head (x >= 126) while the head still rises (r < 223).

    python early_l6vault4.py   -> logs/fix/early_l6vault4.txt, best prefix logs/fix/early_l6vault4_best.json
"""
import itertools
import json

from early_l6vault2 import rd, bt, ROOT, LOGS_DIR, BizHawk

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="early_l6vault4.log")
e.load("cap14_f11000")
for i in range(11000, ROOT):
    e.step(bt(lines[i]), 1)
room = e.msave()
res, best = [], None
for x0, rj, a, climb, top in itertools.product((64, 72, 80, 84, 88, 92, 96, 100), range(72, 112, 2), (2, 6, 10, 16, 22), ("A", "RA", "alt"), (10, 14, 18, 22)):
    e.mload(room)
    ins, over, grab, phase = [], None, None, 0
    for r in range(222):
        t = rd(e)
        if t["hp"] < 47 or not (t["head"] or r < 20):
            break
        rel = (t["H"] - t["head"][1]) if t["head"] else -999
        if grab is None and t["an"] in (88, 89):
            grab = (r, t["H"], rel)
        if r < rj:
            inp = ("Right",) if t["x"] < x0 - 1 and t["z"] == 0 else (("Left",) if t["x"] > x0 + 1 and t["z"] == 0 else ())
        elif r < rj + a:
            inp = ("Right", "A")
        elif phase == 0 and rel >= top and grab:
            phase, inp = 1, ("Right", "A")
        elif phase == 1:
            inp = ("Right", "A")
        elif climb == "A":
            inp = ("A",)
        elif climb == "RA":
            inp = ("Right", "A")
        else:
            inp = ("Left", "A") if ((r - rj - a) // 4) % 2 == 0 else ("Right", "A")
        e.step(inp, 1)
        ins.append("+".join(inp))
        t2 = rd(e)
        if t2["hp"] < 47:
            break
        if t2["x"] >= 126 and t2["head"] and t2["head"][1] < 7758 and t2["H"] - t2["head"][1] >= -8:
            over = (r + 1, t2["x"], t2["H"], t2["H"] - t2["head"][1])
            break
    res.append((x0, rj, a, climb, top, grab, over))
    if over and (best is None or over[0] < best[0][0]):
        best = (over, (x0, rj, a, climb, top), list(ins))
        json.dump({"from_frame": ROOT, "inputs": best[2], "over": over, "params": best[1]}, open(LOGS_DIR / "fix" / "early_l6vault4_best.json", "w"))
        print(f"over the head at r+{over[0]} (x {over[1]}, H {over[2]}, rel {over[3]}) with x0 {x0} jump r+{rj} A{a} climb {climb} top {top}; grabbed {grab}", flush=True)
out = [f"{len(res)} trials; {sum(1 for r in res if r[6])} get right of the rising head; {sum(1 for r in res if r[5])} grab the snake",
       f"best: {best[0] if best else None} {best[1] if best else None}"]
ok = sorted([r for r in res if r[6]], key=lambda r: r[6][0])[:25]
out += [str(r) for r in ok]
print("\n".join(out[:8]))
open(LOGS_DIR / "fix" / "early_l6vault4.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
e.close()
