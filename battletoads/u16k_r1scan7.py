"""Track K: room 1, the last jump (6) = scan 5 behind the PAUSE-FREE ride (no Left x8 at index 1576: the head turns up D=6
frames sooner); every index of scan 5 is shifted by D.   python u16k_r1scan7.py W0 A1 AH [k list] [D=6]
Original notes: room 1, the last jump (5).  Root L6c[:1708] (toad parked at (126,7998)).  Boarding: idle W0, A x A1 (grab the
vertical body, cling jump, come down on the head just after it turns), stand by index 1768.  Then ONE Right hold of k
frames from 1769 (walk toward the head's front; the head's top carries from about head-30 to head+12; the head pauses one
frame every 48 px, which shifts the toad +2 and makes a one-frame z blip), idle to index j, DASH JUMP
(Right, -, Right+A x AH, Right).  The exit is a capture zone at x >= ~366, H ~8097..8130; room 2 loads 129 frames later.
    python u16k_r1scan7.py W0 A1 AH [k list] -> logs/fix/u16k_r1scan7_<W0>_<A1>_<AH>.txt, best ..._best.json (L6c: room 2 at 2022)"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

W0, A1, AH = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
KS = [int(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else list(range(4, 13))
D = int(sys.argv[5]) if len(sys.argv) > 5 else 6
NL = int(sys.argv[6]) if len(sys.argv) > 6 else 2      # Left frames just before the hop (face the snake, or A does not grab it)
TAG = f"{W0}_{A1}_{AH}_D{D}_L{NL}"
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
e = BizHawk(log_name=f"u16k_r1scan7_{TAG}.log")
e.load("L4c5_end0")
pre = ins0[:1576] + [""] * (1708 - D - 1576) + [""] * (W0 - NL) + ["Left"] * NL + ["A"] * A1 + [""] * (1768 - 1708 - W0 - A1)
for b in pre:
    e.step(bt(b), 1)
root = e.msave()
n0 = len(pre)
out, best = [], None


def st():
    m = e.ram(0, 0x800)
    hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], hp=m[0x51A], spd=m[0x565], head=hd[0] if hd else None)


t = st()
out.append(f"root {n0}: toad {t['x']},{t['H']} z{t['z']} head {t['head']}")
for k in KS:
    e.mload(root)
    ride, seq = {}, []
    for n in range(n0 + 1, 1826 - D):
        b = "Right" if n - n0 <= k else ""
        e.step(bt(b), 1)
        seq.append(b)
        t = st()
        if t["H"] < 8050 or not t["head"]:
            break
        if t["z"] == 0 and t["spd"] == 0 and n >= 1796 - D:
            ride[n] = (e.msave(), list(seq), (t["x"], t["head"][0]))
    out.append(f"walk {k}: rides to {n}; jump candidates {min(ride) if ride else None}..{max(ride) if ride else None}; rel at the first {ride[min(ride)][2][0] - ride[min(ride)][2][1] if ride else None}")
    for j in sorted(ride):
        sid, s, pos = ride[j]
        e.mload(sid)
        tail = ["Right", ""] + ["Right+A"] * AH + ["Right"] * (110 - AH)
        land, res, used = None, None, []
        for i, b in enumerate(tail):
            e.step(bt(b), 1)
            used.append(b)
            t = st()
            if t["hp"] < 47:
                res = f"HURT at {t['x']},{t['H']}"
                break
            if i > 12 and t["z"] == 0:
                land = (j + i + 1, t["x"], t["H"])
                break
        room2 = None
        if land and land[2] >= 8090:
            for i in range(200):
                e.step((), 1)
                used.append("")
                t = st()
                if t["x"] == 76 and t["H"] < 7600:
                    room2 = j + len(used)
                    break
        line = f"walk {k} jump at {j} (toad {pos[0]}, head {pos[1]}): land {land} room2 at {room2} {res or ''}"
        out.append(line)
        if room2 and (best is None or room2 < best[0]):
            best = (room2, line, pre + s + used)
            print(line, flush=True)
            json.dump({"inputs": best[2], "room2": room2, "land": land, "W0": W0, "A1": A1, "AH": AH, "k": k, "j": j},
                      open(LOGS_DIR / "fix" / f"u16k_r1scan7_{TAG}_best.json", "w"))
        e.mfree(sid)
    open(LOGS_DIR / "fix" / f"u16k_r1scan7_{TAG}.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:2] if best else None, "(L6c room 2 at 2022, K6 1992)")
e.close()
