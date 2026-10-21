"""Track K: the warp mash behind the new portal contact.  K6's contact is at input 2286 (L6c 2378); A,B alternating reaches
the Level 8 placement 220 frames later (L6c's own mash 217, early_mash's A,B on up14 215).  Which presses matter?
Root = K6[:2286] replayed from L4c5_end0.  Family: idle to contact+s0, then alternate starting with `first`, one idle
frame inserted at contact+j (flips the parity after j).  Logs the level-byte timeline of each.
    python u16k_mash.py -> logs/fix/u16k_mash.txt, best tail logs/fix/u16k_mash_best.json"""
import json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
seg = json.load(open(LOGS_DIR / "pbeam_K6.json"))["inputs"]
CONTACT = 2286
e = BizHawk(log_name="u16k_mash.log")
e.load("L4c5_end0")
for b in seg[:CONTACT]:
    e.step(bt(b), 1)
root = e.msave()
out, best = [], None


def play(tail_fn, label, limit=260):
    global best
    e.mload(root)
    stage, ev, tail, prev_lv = 0, [], [], 8
    for j in range(limit):
        b = tail_fn(j)
        e.step(bt(b), 1)
        tail.append(b)
        m = e.ram(0, 0x800)
        lv, hp, x = m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8
        if lv != prev_lv:
            ev.append(f"{prev_lv}->{lv}@{j + 1}")
            prev_lv = lv
        if stage == 0 and lv == 7:
            stage = 1
        if stage == 1 and hp == 0 and x == 0:
            stage = 2
            ev.append(f"blank@{j + 1}")
        if stage == 2 and hp > 0 and x > 0:
            ev.append(f"placed@{j + 1}")
            line = f"{label}: placed contact+{j + 1} | {' '.join(ev)}"
            out.append(line)
            if best is None or j + 1 < best[0]:
                best = (j + 1, label, list(tail))
                print(line, flush=True)
            return j + 1
    out.append(f"{label}: no placement | {' '.join(ev)}")
    return None


def alt(s0, first, skip=None, skip2=None):
    other = "B" if first == "A" else "A"

    def fn(j):
        if j < s0 or j == skip or j == skip2:
            return ""
        k = j - s0 - (1 if skip is not None and j > skip else 0) - (1 if skip2 is not None and j > skip2 else 0)
        return first if k % 2 == 0 else other
    return fn


for first in ("A", "B"):
    play(alt(0, first), f"alt from 0 first {first}")
    for j in range(1, 226):
        play(alt(0, first, j), f"alt first {first} idle@{j}")
open(LOGS_DIR / "fix" / "u16k_mash.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:2])
json.dump({"contact": CONTACT, "placed_after": best[0], "label": best[1], "tail": best[2]}, open(LOGS_DIR / "fix" / "u16k_mash_best.json", "w"))
e.close()
