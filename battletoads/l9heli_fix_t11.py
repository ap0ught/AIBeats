"""Can the floor mine be destroyed or shoved aside?  From the b1 path at frame 150: Left until the mine is D px away, then attack patterns.
Report mine hp / presence / x and the toad's progress."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t11.log"); e.load(g["root"])
for b in g["inputs"][:150]: e.step(bt(b), 1)
root0 = e.msave()
def mine(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x72: return (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x51A + q], m[0x565 + q])
    return None
def seqs():
    yield "punch once, Left", ["Left+B"] + ["Left"] * 79
    yield "punch x2 (gap 12), Left", ["Left+B"] + ["Left"] * 12 + ["Left+B"] + ["Left"] * 66
    yield "Left+B every 8", (["Left+B"] + ["Left"] * 7) * 10
    yield "Left+B every 4", (["Left+B"] + ["Left"] * 3) * 20
    yield "Left+B every 2", (["Left+B", "Left"]) * 40
    yield "B hold", ["Left+B"] * 80
    yield "jump, B at 6", ["Left+A"] * 4 + ["Left"] * 2 + ["Left+B"] + ["Left"] * 73
    yield "jump, B at 12", ["Left+A"] * 4 + ["Left"] * 8 + ["Left+B"] + ["Left"] * 67
    yield "jump, B at 20", ["Left+A"] * 4 + ["Left"] * 16 + ["Left+B"] + ["Left"] * 59
    yield "Down+B", ["Down+B"] + ["Left"] * 79
for D in (50, 40, 32, 26):
    for name, seq in seqs():
        e.mload(root0); n = 0; hurt = None; tr = []
        while True:
            m = e.ram(0, 0x800); s = toad(m); mi = mine(m)
            if mi is None or s["x"] - mi[0] <= D or n > 80: break
            e.step(("Left",), 1); n += 1
        for i, b in enumerate(seq):
            e.step(bt(b), 1); m = e.ram(0, 0x800); s = toad(m)
            if i % 8 == 7: tr.append((s["x"], mine(m), s["an"]))
            if s["hp"] < 47: hurt = (i + 1, s["x"], mine(m)); break
        print(f"D {D} n {n} {name:24s} hurt {hurt} track {tr}", flush=True)
e.close()
