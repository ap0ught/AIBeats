"""Chase 3 (2026-10-06): walk RIGHT into the oncoming circling platform, jump (A held a) at frame j, land on it, pump A after d,
steer Left in the launch flight to the static platform (H 4727-4750), hop to the walker's platform (H >= 4762).
    -> knowledge/l12_chase.json, bookmark CHASE_best"""
import json
from toads.emulator import BizHawk
e = BizHawk(log_name="l12chase3.log"); e.load("BOOT_w12L"); root = e.msave()
F0 = 6352
def rd():
    m = e.ram(0, 0x800)
    p = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(2, 15) if m[0x3C1 + q] == 0x36]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], spd=m[0x565], hp=m[0x51A], lives=m[0x11], p=p)
def go(b, seq): e.step(tuple(v for v in b.split("+") if v), 1); seq.append(b); return rd()
best = None; nb = 0
for j in range(66, 100, 2):
    for a in (10, 13, 16):
        for post in ("Right", "", "Left"):                     # what to hold after the A hold (drift)
            e.mload(root); seq = []
            for i in range(j): s = go("Right", seq)
            for i in range(a): s = go("Right+A", seq)
            land = None
            for i in range(50):
                s = go(post, seq)
                if s["hp"] < 47 or s["lives"] < 4: break
                if s["z"] == 0 and s["H"] >= 4630: land = F0 + len(seq); break
            if not land: continue
            nb += 1
            if nb <= 8 or nb % 20 == 0: print("board: jump", F0 + j, "A", a, post or '-', "landed", land, "x", s["x"], "plat", s["p"], flush=True)
            base = e.msave(); bseq = list(seq)
            for d in (0, 2, 4, 6, 9, 12, 16, 20):
                e.mload(base); seq = list(bseq)
                for i in range(d): s = go("", seq)
                stage = 0; got = None; t1 = 0
                for i in range(150):
                    b = "A" if stage == 0 else (("Left+A" if i < t1 + 28 else "Left") if stage == 1 else "Left+A")
                    s = go(b, seq)
                    if s["hp"] < 47 or s["lives"] < 4: break
                    if stage == 0 and s["z"] == 8 and s["H"] > 4655: stage = 1; t1 = i
                    if stage == 1 and s["z"] == 0 and 4720 <= s["H"] <= 4750: stage = 2
                    if stage == 2 and s["z"] == 0 and s["H"] >= 4762: got = F0 + len(seq); break
                if got:
                    print("LAUNCH: board", land, "d", d, "-> walker platform at", got, "x", s["x"], "(old 6786; <= 6575 wins the lap)", flush=True)
                    if best is None or got < best[0]: best = (got, list(seq), j, a, post, d)
            e.mfree(base)
print(nb, "boardings;", "BEST:" if best else "no launch", best[0] if best else "", (best[2:] if best else ""), flush=True)
if best:
    json.dump({"from": "BOOT_w12L", "f0": F0, "inputs": best[1], "arrive": best[0]}, open("knowledge/l12_chase.json", "w"))
    e.mload(root)
    for b in best[1]: e.step(tuple(v for v in b.split("+") if v), 1)
    e.save("CHASE_best")
e.close()
