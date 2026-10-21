"""Checkpoint 5: replay the follow search's line from L4n_ledge5 up to frame j (toad airborne, coming left over the
snowman at x 244 like TAS #5093), then Left+B for 2..14 frames and see whether the snowman dies; then stand on its
pile facing left and press B every ~30 frames until the barrier breaks (cp 5)."""
import json
from toads.emulator import BizHawk

def objs(m, oid): return [(s, m[0x3FD+s]|m[0x3EE+s]<<8, m[0x439+s], m[0x51A+s]) for s in range(2,15) if m[0x3C1+s] == oid]
def tx(m): return m[0x3FD] | m[0x3EE] << 8

live = json.load(open("knowledge/l4s_L4n_ledge5_live.json"))
e = BizHawk(log_name="l4cp5.log")
e.load("L4n_ledge5"); e.step((), 2)
path = []
for k, b in enumerate(live):
    m = e.ram(0, 0x800); path.append((k, tx(m), m[0x439], m[0x475]))
    e.step(tuple(v for v in b.split("+") if v), 1)
cands = [k for k, x, h, z in path if 250 <= x <= 330]
print("frames with x in 250..330:", cands[:5], "...", cands[-5:], [(p[1], p[2], p[3]) for p in path if p[0] in cands[:3]])
best = None
for j in cands:
    for hold in (2, 4, 8, 12):
        e.load("L4n_ledge5"); ins = [""] * 2; e.step((), 2)
        for b in live[:j]: e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b)
        for _ in range(hold): e.step(("Left", "B"), 1); ins.append("Left+B")
        dead = False
        for _ in range(50):
            m = e.ram(0, 0x800)
            sm = [o for o in objs(m, 0x33) if o[1] < 400]
            if not sm or sm[0][3] == 0: dead = True; break
            e.step(("Left",), 1); ins.append("Left")
        if not dead: continue
        # onto the pile (x <= 222), facing left, then B every 30 f
        for _ in range(120):
            m = e.ram(0, 0x800)
            if tx(m) <= 222 and m[0x475] == 0: break
            b = "Left" if len(ins) % 2 == 0 else ""; e.step((b,) if b else (), 1); ins.append(b)
        for _ in range(10):
            if e.byte(0x585) >= 5: break
            e.step(("B",), 1); ins.append("B")
            for _ in range(30):
                e.step((), 1); ins.append("")
                if e.byte(0x585) >= 5: break
        if e.byte(0x585) >= 5 and (best is None or len(ins) < len(best)):
            best = ins; print("j", j, "hold", hold, "cp5 after", len(ins) - 2, flush=True)
            json.dump(best[2:], open("knowledge/l4s_L4n_ledge5.json", "w"))
print("best", len(best) - 2 if best else None)
e.close()
