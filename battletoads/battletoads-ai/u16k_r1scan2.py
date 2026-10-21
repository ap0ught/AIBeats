"""Track K: room 1, the last jump, refined.  Root as u16k_r1scan.py (standing on the snake at index 1785, 28 px behind
the head).  Controller: hold Right while the toad is left of head+off, else nothing (ride at the head's front edge);
at index j DASH JUMP (Right, -, Right+A x a, then Right); after the landing idle until the toad appears in room 2
(x 76, H < 7600).  L6c: room 2 at index 2022.
    python u16k_r1scan2.py [off=10] -> logs/fix/u16k_r1scan2_<off>.txt, best logs/fix/u16k_r1scan2_<off>_best.json"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

off = int(sys.argv[1]) if len(sys.argv) > 1 else 10
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
e = BizHawk(log_name=f"u16k_r1scan2_{off}.log")
e.load("L4c5_end0")
pre = ins0[:1708] + [""] * 24 + ["A"] * 32 + [""] * 21
for b in pre:
    e.step(bt(b), 1)
n0 = len(pre)
out, best = [], None


def st():
    m = e.ram(0, 0x800)
    hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], hp=m[0x51A], spd=m[0x565], head=hd[0] if hd else None,
                ids=[m[0x3C1 + q] for q in range(1, 15)])


# ride phase once, savestate per index
ride, seq, t = {}, [], st()
for n in range(n0 + 1, 1846):
    b = "Right" if (t["head"] and (t["x"] - t["head"][0]) + t["spd"] * t["spd"] / 512 < off - 1 and t["z"] == 0) else ""
    e.step(bt(b), 1)
    seq.append(b)
    t = st()
    if t["z"] != 0 and n > n0 + 3:
        out.append(f"fell off the head at {n} ({t['x']} vs head {t['head']})")
        break
    ride[n] = (e.msave(), list(seq), (t["x"], t["head"][0] if t["head"] else None))
print(f"off {off}: riding to {max(ride)}; at 1812 (toad x, head x) {ride.get(1812, (0, 0, None))[2]}", flush=True)
for j in sorted(ride):
    if j < 1800:
        continue
    for a in (32, 24):
        sid, s, pos = ride[j]
        e.mload(sid)
        tail = ["Right", ""] + ["Right+A"] * a + ["Right"] * 70
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
        if land and land[2] >= 8100:
            for i in range(200):
                e.step((), 1)
                used.append("")
                t = st()
                if t["x"] == 76 and t["H"] < 7600:
                    room2 = j + len(used)
                    break
        line = f"jump at {j} (toad {pos[0]}, head {pos[1]}) A{a}: land {land} room2 at {room2} {res or ''}"
        out.append(line)
        if room2 and (best is None or room2 < best[0]):
            best = (room2, line, pre + s + used)
            print(line, flush=True)
            json.dump({"inputs": best[2], "room2": room2, "land": land}, open(LOGS_DIR / "fix" / f"u16k_r1scan2_{off}_best.json", "w"))
open(LOGS_DIR / "fix" / f"u16k_r1scan2_{off}.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:2] if best else None, "(L6c room 2 at 2022)")
e.close()
