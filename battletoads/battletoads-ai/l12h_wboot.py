"""L12h probe: does the big boot (sprint >= ~32 frames, then direction+B) work on the walker (0x62)? From the walker's spawn (piece s3c + hop):
wait w, double-tap sprint in direction d for m frames, d+B, hold d; report the walker's health drops."""
import sys
from l12h_lib import *
p = load_piece("s3c"); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name="fix_l12h_wboot.log"); e.load(p["base"]); run(e, p["inputs"])
k = k0
for i in range(14): e.step(("Left", "A"), 1); k += 1
s = rd(e)
while not [d for d in s["objs"] if d[0] == 0x62]: e.step(("Left",), 1); k += 1; s = rd(e)
while s["z"] != 0: e.step((), 1); k += 1; s = rd(e)
print("spawned, toad landed at", k, s["x"], [d for d in s["objs"] if d[0] == 0x62], flush=True)
base = e.msave(); kb = k
def hpw(s): return sum(d[3] for d in s["objs"] if d[0] == 0x62)
for d in ("Left", "Right"):
    for w in range(0, 60, 3):
        for m in (30, 34, 38):
            e.mload(base); k = kb; ev = []
            seq = [""] * w + [d, ""] + [d] * m + [d + "+B"] + [d] * 50
            prev = 79; hurt = None
            for b in seq:
                e.step(bt(b), 1); k += 1; s = rd(e)
                h = hpw(s)
                if h < prev: ev.append((k, prev, h, s["an"])); prev = h
                if not alive(s): hurt = k; break
            if ev: print(d, "w", w, "m", m, "hits", ev, "hurt", hurt, flush=True)
e.close()
