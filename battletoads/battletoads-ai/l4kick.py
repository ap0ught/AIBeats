"""Randomized search for the checkpoint-5 snowman kill (TAS #5093 kicks it airborne at x~272, h~160, right after its
throw). From the follow line's frame 230 (before its jump): random approach / jump / air-steer / B timing."""
import json, random
from toads.emulator import BizHawk

live = json.load(open("knowledge/l4s_L4n_ledge5_live.json"))
e = BizHawk(log_name="l4kick.log")
e.load("L4n_ledge5"); e.step((), 2)
for b in live[:230]: e.step(tuple(v for v in b.split("+") if v), 1)
root = e.msave()
rng = random.Random(3)
hits = []
for t in range(1500):
    seq = []
    seq += [rng.choice(["", "Left", "Right"])] * rng.randrange(0, 30)
    seq += [rng.choice(["Left+A", "A"])] * rng.randrange(2, 16)
    air = rng.choice(["", "Left", "Right"])
    n_air = rng.randrange(0, 30)
    seq += [air] * n_air
    seq += ["Left+B"] * rng.randrange(2, 16)
    seq += ["Left"] * 20
    e.mload(root)
    seen = False
    for k, b in enumerate(seq):
        e.step(tuple(v for v in b.split("+") if v), 1)
        m = e.ram(0, 0x800)
        sm = [s_ for s_ in range(2, 15) if m[0x3C1 + s_] == 0x33 and (m[0x3FD + s_] | m[0x3EE + s_] << 8) == 244]
        if sm and m[0x51A + sm[0]] > 0: seen = True
        if seen and (not sm or m[0x51A + sm[0]] == 0):
            hits.append((k + 1, seq[:k + 1])); break
        if m[0x51A] < 47 or m[0x11] < 2: break
    if hits and t % 100 == 0: print(t, "best", min(h[0] for h in hits), flush=True)
hits.sort(key=lambda h: h[0])
print("kills:", len(hits), [h[0] for h in hits[:10]])
if hits: json.dump(hits[0][1], open("knowledge/l4_cp5_kick.json", "w"))
e.close()
