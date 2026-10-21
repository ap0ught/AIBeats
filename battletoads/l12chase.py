"""Chase the circling platform after the big-boot kill (2026-10-06): from BOOT_w12L run Left, jump on at frame j, press A at
landing+d, look for the launch and a landing on the static platform (H 4727) then the walker's platform (H 4766).
    python l12chase.py  -> knowledge/l12_chase.json (best inputs from BOOT_w12L), bookmark CHASE_best"""
import json
from toads.emulator import BizHawk
e = BizHawk(log_name="l12chase.log"); e.load("BOOT_w12L"); root = e.msave()
F0 = 6352
def rd():
    m = e.ram(0, 0x800)
    p = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(2, 15) if m[0x3C1 + q] == 0x36]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], spd=m[0x565], hp=m[0x51A], lives=m[0x11], p=p, b=m[0x0B])
best = None
# phase 1: run left; at frame j press Left+A (jump), then hold Left; see if we land on the platform (H 4637, z 0) by j+60
boards = []
for j in range(40, 130, 2):
    e.mload(root); ins = []
    for i in range(j): e.step(("Left",), 1); ins.append("Left")
    e.step(("Left", "A"), 1); ins.append("Left+A")
    land = None
    for i in range(60):
        e.step(("Left",), 1); ins.append("Left"); s = rd()
        if s["hp"] < 47 or s["lives"] < 4: break
        if s["z"] == 0 and s["H"] >= 4630 and i > 3: land = (F0 + len(ins), s); break
    if land: boards.append((j, land[0], land[1]["x"], land[1]["p"], ins)); print("board: jump at", F0 + j, "landed", land[0], "x", land[1]["x"], "plat", land[1]["p"], "spd", land[1]["spd"], flush=True)
print(len(boards), "boardings", flush=True)
# phase 2: from each boarding, after d idle frames hold A (and Left), look for the launch -> static platform -> walker platform
for j, lf, lx, lp, ins in boards:
    for d in range(0, 40, 2):
        e.mload(root)
        for b in ins: e.step(tuple(v for v in b.split("+") if v), 1)
        seq = list(ins)
        for i in range(d): e.step((), 1); seq.append("")
        got = None; stage = 0
        for i in range(140):
            b = ("Left", "A") if stage < 2 else ("Left", "A")
            e.step(b, 1); seq.append("Left+A"); s = rd()
            if s["hp"] < 47 or s["lives"] < 4: break
            if stage == 0 and s["z"] == 8 and s["H"] > 4660: stage = 1          # launched
            if stage == 1 and s["z"] == 0 and 4720 <= s["H"] <= 4740: stage = 2   # on the static platform
            if stage == 2 and s["z"] == 0 and s["H"] >= 4762: got = (F0 + len(seq), s["x"], s["H"]); break
        if got:
            print("LAUNCH: board", lf, "A at +", d, "-> walker platform at", got, "(old 6786)", flush=True)
            if best is None or got[0] < best[0]: best = (got[0], seq, j, d)
if best:
    print("BEST: walker platform at", best[0], "jump at", F0 + best[2], "A after", best[3], "frames; inputs", len(best[1]), flush=True)
    json.dump({"from": "BOOT_w12L", "f0": F0, "inputs": best[1], "arrive": best[0]}, open("knowledge/l12_chase.json", "w"))
    e.mload(root)
    for b in best[1]: e.step(tuple(v for v in b.split("+") if v), 1)
    e.save("CHASE_best")
else:
    print("no launch found", flush=True)
e.close()
