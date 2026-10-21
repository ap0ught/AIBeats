"""Can the toad pass the floor mine (0x72) on the ground?  From the b1 path at frame 150 (landed at 832, running left): Left until the mine
is D px away, then a pattern for 60 frames.  Report hp loss, x progress, crouch anim."""
import json
from l9heli_fix_lib import *
g = json.load(open(LOGS_DIR / "fix" / "heli_beam_b1.json"))[0]
e = BizHawk(log_name="l9heli_fix_t10.log"); e.load(g["root"])
for b in g["inputs"][:150]: e.step(bt(b), 1)
root0 = e.msave()
def mine(m):
    for q in range(2, 15):
        if m[0x3C1 + q] == 0x72: return m[0x3FD + q] | m[0x3EE + q] << 8
pats = {"Left": ["Left"], "Down+Left": ["Down+Left"], "Down,Left alt": ["Down", "Left"], "Down": ["Down"], "Left,Down alt": ["Left", "Down"], "Down+Left,Left alt": ["Down+Left", "Left"], "Up+Left": ["Up+Left"], "B": ["Left+B", "Left"], "idle": [""]}
for D in (60, 45, 36, 30, 24):
    for name, pat in pats.items():
        e.mload(root0); n = 0; hurt = None; tr = []
        while True:
            m = e.ram(0, 0x800); s = toad(m); mx = mine(m)
            if mx is None or s["x"] - mx <= D or n > 80: break
            e.step(("Left",), 1); n += 1
        start = (n, s["x"], mx)
        for i in range(70):
            e.step(bt(pat[i % len(pat)]), 1); m = e.ram(0, 0x800); s = toad(m)
            if i % 10 == 9: tr.append((s["x"], mine(m), s["an"], s["spd"]))
            if s["hp"] < 47: hurt = (i + 1, s["x"], mine(m), s["hp"]); break
        print(f"D {D} start {start} {name:18s} hurt {hurt} track {tr}", flush=True)
e.close()
