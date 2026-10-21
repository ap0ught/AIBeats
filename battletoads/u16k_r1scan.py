"""Track K: room 1, the last jump.  Root = L6c[:1708] + 24 idle + A x32 (grab the vertical body, hop over the turning head,
land on the snake at index 1785, 28 px behind the head).  Then: Right for k frames (walk toward the head's front), idle
to index j, DASH JUMP (Right, -, Right+A x a, Right) -> index of the first frame the toad stands on the exit ledge
(H 8120).  L6c stands there at 1897..1900.
    python u16k_r1scan.py -> logs/fix/u16k_r1scan.txt"""
import json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
e = BizHawk(log_name="u16k_r1scan.log")
e.load("L4c5_end0")
pre = ins0[:1708] + [""] * 24 + ["A"] * 32 + [""] * 21
for b in pre:
    e.step(bt(b), 1)
root = e.msave()
n0 = len(pre)
out, best = [], None


def st(m):
    hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], hp=m[0x51A], spd=m[0x565], head=hd[0] if hd else None)


for k in (0, 6, 12, 18, 24, 30):
    for j in range(1800, 1850, 3):
        for a in (32, 20):
            e.mload(root)
            seq = ["Right"] * k + [""] * max(0, j - n0 - k) + ["Right", ""] + ["Right+A"] * a + ["Right"] * 60
            ledge, at_jump, res = None, None, None
            for i, b in enumerate(seq):
                e.step(bt(b), 1)
                t = st(e.ram(0, 0x800))
                n = n0 + i + 1
                if n == j + 2:
                    at_jump = (t["x"], t["H"], t["z"], t["head"][0] if t["head"] else None)
                if t["hp"] < 47:
                    res = f"HURT {n} at {t['x']},{t['H']}"
                    break
                if t["z"] == 0 and t["H"] == 8120:
                    ledge = (n, t["x"])
                    break
                if n > j + 12 and t["z"] == 0:
                    res = f"landed {n} at {t['x']},{t['H']}"
                    break
            line = f"walk {k} jump at {j} A{a}: at jump (x,H,z,head x) {at_jump} -> ledge {ledge} {res or ''}"
            out.append(line)
            if ledge and (best is None or ledge[0] < best[0]):
                best = (ledge[0], line, pre + seq[:ledge[0] - n0])
                print(line, flush=True)
                json.dump({"inputs": best[2], "ledge": ledge[0]}, open(LOGS_DIR / "fix" / "u16k_r1scan_best.json", "w"))
open(LOGS_DIR / "fix" / "u16k_r1scan.txt", "w").write("\n".join(out) + "\n")
print("BEST", best[:2] if best else None)
e.close()
