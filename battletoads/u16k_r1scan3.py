"""Track K: room 1, the last jump (3).  Root = L6c[:1708] + 24 idle + A x32 + 21 idle (standing on the snake at 1785,
28 px behind the head).  ONE Right hold of k frames (no second press: Right, gap, Right is a dash and runs off the head),
idle to index j, DASH JUMP (Right, -, Right+A x32, Right).  The exit is a capture zone (x >= ~366, H ~8100..8130): the
toad freezes there and room 2 loads 129 frames later.  Reports capture and the index the toad appears in room 2
(L6c: 2022).
    python u16k_r1scan3.py -> logs/fix/u16k_r1scan3.txt, best logs/fix/u16k_r1scan3_best.json"""
import json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
e = BizHawk(log_name="u16k_r1scan3.log")
e.load("L4c5_end0")
pre = ins0[:1708] + [""] * 24 + ["A"] * 32 + [""] * 21
for b in pre:
    e.step(bt(b), 1)
root = e.msave()
n0 = len(pre)
out, best = [], None


def st():
    m = e.ram(0, 0x800)
    hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], hp=m[0x51A], spd=m[0x565], head=hd[0] if hd else None)


for k in range(13, 25):
    e.mload(root)
    ride, seq = {}, []
    for n in range(n0 + 1, 1832):
        b = "Right" if n - n0 <= k else ""
        e.step(bt(b), 1)
        seq.append(b)
        t = st()
        if t["z"] != 0:
            break
        ride[n] = (e.msave(), list(seq), (t["x"], t["head"][0] if t["head"] else None, t["spd"]))
    for j in sorted(ride):
        sid, s, pos = ride[j]
        if j < 1797 or pos[2] != 0:
            e.mfree(sid)
            continue
        e.mload(sid)
        tail = ["Right", ""] + ["Right+A"] * 32 + ["Right"] * 70
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
            json.dump({"inputs": best[2], "room2": room2, "land": land}, open(LOGS_DIR / "fix" / "u16k_r1scan3_best.json", "w"))
        e.mfree(sid)
    open(LOGS_DIR / "fix" / "u16k_r1scan3.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:2] if best else None, "(L6c room 2 at 2022)")
e.close()
