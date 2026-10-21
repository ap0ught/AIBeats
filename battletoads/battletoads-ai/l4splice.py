"""Splice: from L4n_ledge5 (new fast first half, toad on the ledge at x 636) idle d frames, then replay the OLD
route's inputs from its ledge arrival (old L4a index 6521) and report how far they carry: checkpoints reached and
whether the warp (level 8) fires. The global timer $0B drives the floating platform, so d ~ (241-197) mod 256."""
import json, sys
from toads.emulator import BizHawk

L4 = json.load(open("logs/pbeam_L4a.json"))["inputs"]
tail = L4[6521:]
e = BizHawk(log_name="l4splice.log")
res = []
for d in [int(a) for a in sys.argv[1:]] or list(range(38, 52)) + [0, 20, 60, 100]:
    e.load("L4n_ledge5")
    for _ in range(d): e.step((), 1)
    cps = {}; warp = None; died = None
    for k, b in enumerate(tail):
        e.step(tuple(v for v in b.split("+") if v), 1)
        m = e.ram(0, 0x800)
        cp = m[0x585]
        if cp not in cps: cps[cp] = k
        if m[0x11] < 2 and died is None: died = k
        if m[0x10] != 4: warp = (k, m[0x10]); break
        if died is not None and k - died > 200: break
    print("idle", d, "cps", cps, "died", died, "warp", warp, flush=True)
    res.append((d, cps, died, warp))
e.close()
