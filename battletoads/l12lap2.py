"""After the early landing on the small platform (knowledge/l12_lap_launch.json from L12_lap): wait, then jump into
face 4's wind so it carries the toad to the pole at x 288 (the old hang state at frame 9136: (288, 4944, hanging)).
    python l12lap2.py -> knowledge/l12_lap_pole.json (inputs from L12_lap to the hang), prints the hang state"""
import itertools, json
from toads.emulator import BizHawk
from shortcut import k5, col
launch = json.load(open("knowledge/l12_lap_launch.json"))
e = BizHawk(log_name="l12lap2.log"); e.load("L12_lap")
for b in launch: e.step(tuple(v for v in b.split("+") if v), 1)
base = e.msave()
def rd():
    m = e.ram(0, 0x800); return k5(m), m[0x51A], m[0x11], m
best = None
for w, d, k, after in itertools.product(range(30, 130, 2), ("Right", ""), (4, 8, 12, 16, 22, 30, 40), ("Right", "", "Left", "Right+A")):
    if best and w > best[0]: break
    e.mload(base); seq = [""] * w + [(d + "+A").lstrip("+")] * k + [after] * 150
    prev = None; static = 0
    for i, b in enumerate(seq):
        e.step(tuple(v for v in b.split("+") if v), 1); key, hp, lives, m = rd()
        if hp < 40 or lives < 6: break
        static = static + 1 if (key[2] == 8 and prev == key[:2]) else 0
        prev = key[:2]
        if static >= 4 and abs(key[0] - 288) <= 6:
            tot = i + 1
            if best is None or tot < best[0]:
                best = (tot, launch + seq[:tot], (w, d, k, after), key, m[0x3B5])
                print("POLE", best[2], "at", len(launch) + tot, "state", key, "anim", m[0x3B5], flush=True)
                json.dump(best[1], open("knowledge/l12_lap_pole.json", "w"))
            break
print("best", (len(launch) + best[0]) if best else None, "(old: 9136 - 8616 = 520)")
e.close()
