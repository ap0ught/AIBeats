"""Level 4 spike-pit damage boost (the record's line after checkpoint 5): from the pit's edge (bookmark L4r_edge)
stand at x 189, let the shaft's ice ball knock the toad down, get up, step right into the spikes and fall.
Holding Left during the fall avoids the snap to ledge 3 (576,222); this scans what to press after that.

    python l4fall.py trace <plan>      # frame-by-frame print of one plan
    python l4fall.py scan              # scan plans, save the fastest deep landing (knowledge/l4_boost.json, L4r_dip)

A plan is a comma list of <button>:<until Hd below this>, e.g.  Left:-110,Right:-200,:-999
"""
import itertools
import json
import sys

from toads.emulator import BizHawk


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def run(e, root, lives0, plan, trace=False, target=189):
    e.mload(root)
    seq = []
    hit = up = fell = None
    Hd = 0
    prev = e.byte(0x439)
    cool = 0
    path = []
    pi = 0
    for k in range(700):
        m = e.ram(0, 0x800)
        x = tx(m)
        if hit is None and m[0x51A] < 47:
            hit = k
        if hit is None:
            if cool > 0 or m[0x475] != 0 or m[0x565] != 0:
                b = ""
                cool = max(0, cool - 1)
            elif x < target:
                b = "Right"
                cool = 4
            else:
                b = ""
        elif up is None:
            b = ""
            if k > hit + 60 and m[0x475] == 0 and m[0x3B5] not in (48, 19, 20, 21):
                up = k
        elif fell is None:
            if m[0x475] != 0 or m[0x439] != 94:
                fell = k
                b = plan[0][0]
            elif cool > 0:
                b = ""
                cool -= 1
            else:
                b = "Right"
                cool = 2
        else:
            while pi < len(plan) - 1 and Hd < plan[pi][1]:
                pi += 1
            b = plan[pi][0]
        e.step(tuple(v for v in b.split("+") if v), 1)
        seq.append(b)
        m = e.ram(0, 0x800)
        Hd += (m[0x439] - prev + 128) % 256 - 128
        prev = m[0x439]
        if fell:
            path.append((tx(m), Hd))
            if trace:
                print(k, repr(b), "x", tx(m), "h", m[0x439], "Hd", Hd, "z", m[0x475], "anim", m[0x3B5], "st", m[0x4B1], "hp", m[0x51A],
                      "cam", m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8, "cp", m[0x585], flush=True)
        if m[0x51A] == 0 or m[0x11] < lives0:
            return ("dead", k, tx(m), Hd), seq, path
        if fell and m[0x475] == 0 and Hd < -100 and k > fell + 20:
            return ("LANDED", len(seq), tx(m), m[0x439], Hd, m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8, m[0x51A], m[0x585]), seq, path
    return ("alive", tx(m), m[0x439], Hd), seq, path


def parse(s):
    return [(p.split(":")[0], int(p.split(":")[1])) for p in s.split(",")]


def main():
    e = BizHawk(log_name="l4fall.log")
    e.load("L4r_edge")
    root = e.msave()
    lives0 = e.byte(0x11)
    if sys.argv[1] == "trace":
        out, seq, path = run(e, root, lives0, parse(sys.argv[2]), trace=True)
        print(out)
    else:
        best = None
        for h1, b2, h2, b3 in itertools.product((-60, -90, -105, -120, -135, -150, -170), ("", "Right", "Down"), (-180, -210, -240, -999), ("", "Left", "Right")):
            if h2 == -999 and b3:
                continue
            plan = [("Left", h1), (b2, h2), (b3, -999)]
            out, seq, path = run(e, root, lives0, plan)
            print(plan, out, path[::12][-8:], flush=True)
            if out[0] == "LANDED" and out[4] < -200 and (best is None or out[1] < best[0][1]):
                best = (out, seq)
        if best:
            json.dump(best[1], open("knowledge/l4_boost.json", "w"))
            e.mload(root)
            for b in best[1]:
                e.step(tuple(v for v in b.split("+") if v), 1)
            e.save("L4r_dip")
            print("SAVED L4r_dip", best[0])
    e.close()


if __name__ == "__main__":
    main()
