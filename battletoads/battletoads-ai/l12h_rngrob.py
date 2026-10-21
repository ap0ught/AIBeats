"""L12h DEBUG probe (pokes on a snapshot only, never in a run): how sensitive is a tower segment to the random numbers?
Replay the segment to frame a, then for a few trials POKE other values into the RNG bytes $25-$28 and replay the rest; report the first
frame where the toad's track leaves the unpoked replay, and how each trial ends (level 13 reached unhurt or not).
    python l12h_rngrob.py <segment> <a> [b=end] [trials=4]"""
import json, random, sys
from l12h_lib import *
name, a = sys.argv[1], int(sys.argv[2]); b = int(sys.argv[3]) if len(sys.argv) > 3 and int(sys.argv[3]) > 0 else None
trials = int(sys.argv[4]) if len(sys.argv) > 4 else 4
ins = seg(name); b = b or len(ins)
e = BizHawk(log_name=f"fix_l12h_rngrob_{name}_{a}.log"); e.load(json.load(open(LOGS_DIR / f"pbeam_{name}.json"))["bookmark"])
run(e, ins[:a]); base = e.msave()
def track(pokes):
    e.mload(base)
    for ad, v in pokes: e.poke(ad, v)
    out = []; hurt = None; lvl13 = None
    for i in range(a, b):
        e.step(bt(ins[i]), 1); m = e.ram(0, 0x800)
        out.append((m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x10]))
        if m[0x10] == 5 and i > 20 and m[0x51A] < 47 and hurt is None: hurt = i + 1
        if m[0x10] == 13 and lvl13 is None: lvl13 = i + 1
    return out, hurt, lvl13
ref, hurt, l13 = track([])
print(name, f"[{a}:{b}] unpoked: hurt {hurt}, level 13 at {l13}", flush=True)
random.seed(7)
for t in range(trials):
    pk = [(0x25 + i, random.randrange(256)) for i in range(4)]
    tr, hurt, l13 = track(pk)
    div = next((a + i + 1 for i, (x, y) in enumerate(zip(ref, tr)) if x != y), None)
    print("  rng", [v for _, v in pk], "-> first divergence at", div, "| hurt at", hurt, "| level 13 at", l13, flush=True)
e.close()
