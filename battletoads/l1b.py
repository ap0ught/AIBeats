"""Level 1 rebuilt in stages (2026-10-02), after the record's line (its run 0-3.6 s): kill the LEFT pig the moment it
can be hurt, be dashing RIGHT straight afterwards, ram the right pig on the way, dash-jump onto the rock, portal.
Our old segment (l1.py, random timings) headbutted the first pig leftwards, slid to x 31, whiffed a punch at the
second pig and walked the last stretch: 300 frames from the landing; the record ~210.

Each stage scans a few parameters on savestates and keeps the fastest:
  stage 1  first pig dead and the toad back at x >= 110 moving right
  stage 2  second pig dead
  stage 3  warp engaged (routine pointer $E50D)

    python l1b.py      -> logs/pbeam_L1b.json (bookmark L1_go, like pbeam_L1.json)
"""
import itertools
import json

from toads.emulator import BizHawk
from l1 import rd

LAND = 156                                                # frames from L1_go to the landing


class Line:
    def __init__(self, e):
        self.e = e
        self.ins = []

    def st(self, b, n=1):
        for _ in range(n):
            self.e.step(tuple(v for v in b.split("+") if v), 1)
            self.ins.append(b)
        return self.e.ram_all()

    def mark(self):
        return self.e.msave(), len(self.ins)

    def back(self, mk):
        self.e.mload(mk[0])
        del self.ins[mk[1]:]


def pig(r, slot):
    return (r[0x3FD + slot] + 256 * ((r[0x3EE + slot] + 128) % 256 - 128), r[0x41B + slot], r[0x51A + slot]) if r[0x3C1 + slot] else None


def dash(L, d, extra=""):
    L.st(d + extra)
    L.st(extra.lstrip("+"))
    return L.st(d + extra)


def stage1(L, hp0):
    mk = L.mark()
    best = None
    for side, dx, fa, att in itertools.product(("R", "L"), range(12, 66, 6), range(204, 234, 2), ("B", "dirB", "head2", "head4", "head6", "dashB")):
        L.back(mk)
        r = L.e.ram_all()
        px, py, _ = pig(r, 4)
        want = px + dx if side == "R" else px - dx
        if want < 8:
            continue
        toward = "Left" if side == "R" else "Right"
        ok = True
        while len(L.ins) < fa:                              # walk to the spot beside the pig's pod and face the pig
            r = L.e.ram_all()
            tx, ty, lvl, pigs, spd, z = rd(r)
            h = "Right" if tx < want - 2 else "Left" if tx > want + 2 else ""
            v = "Down" if py > ty + 1 else "Up" if py < ty - 1 else ""
            b = "+".join(x for x in (h, v) if x)
            if not b and (r[0x4A2] & 0x40 != 0) != (toward == "Left") and spd == 0:
                b = toward                                  # one tap to face the pig
            L.st(b)
        r = L.e.ram_all()
        tx, ty, lvl, pigs, spd, z = rd(r)
        if abs(tx - want) > 6 or abs(ty - py) > 3:
            continue
        if att == "B":
            L.st("B", 2)
        elif att == "dirB":
            L.st(toward + "+B", 2)
        elif att == "dashB":
            dash(L, toward)
            L.st(toward + "+B", 2)
        else:
            L.st(toward)
            L.st("")
            L.st(toward, int(att[4:]))
            L.st(toward + "+B", 2)
        dead = None
        for _ in range(40):
            r = L.st(toward if att != "B" else "")
            p = pig(r, 4)
            if r[0x51A] < hp0:
                ok = False
                break
            if p is None or p[2] == 0:
                dead = len(L.ins)
                break
        if not ok or dead is None:
            continue
        got = None                                          # now get going Right: dash as soon as the game lets us
        k = 0
        for _ in range(90):
            r = L.e.ram_all()
            tx, ty, lvl, pigs, spd, z = rd(r)
            if r[0x51A] < hp0:
                break
            if tx >= 110 and spd >= 150 and (r[0x4A2] & 0x40) == 0:
                got = len(L.ins)
                break
            if spd < 150 and z == 0 and k % 3 == 0:
                L.st("Right")
                L.st("")
                k = 1
            else:
                L.st("Right")
                k += 1 if spd < 150 else 0
        if got and (best is None or got < best[0]):
            best = (got, list(L.ins), (side, dx, fa, att, dead))
            print("stage 1:", best[2], "pig 1 dead at", dead, "dashing right at x>=110 at", got, flush=True)
    return best


def stage2(L, hp0):
    mk = L.mark()
    best = None
    for dyo, dmin, dmax, att in itertools.product((-4, -2, 0, 2, 4), (20, 30, 40, 50), (8, 16), ("ram", "head2", "head4")):
        L.back(mk)
        dead = None
        fired = False
        for _ in range(140):
            r = L.e.ram_all()
            tx, ty, lvl, pigs, spd, z = rd(r)
            p = pig(r, 5)
            if r[0x51A] < hp0:
                break
            if p is None or p[2] == 0:
                dead = len(L.ins)
                break
            px, py, _ = p
            v = "Down" if py + dyo > ty + 1 else "Up" if py + dyo < ty - 1 else ""
            d = px - tx
            if not fired and dmin <= d <= dmin + dmax and abs(py + dyo - ty) <= 3 and z == 0:
                if att == "ram":
                    L.st("Right+B", 2)
                else:
                    L.st("Right")
                    L.st("")
                    L.st("Right", int(att[4:]))
                    L.st("Right+B", 2)
                fired = True
                continue
            b = "Right" + ("+" + v if v else "")
            if spd < 150 and z == 0 and not fired:
                L.st(b)
                L.st(v)
            L.st(b)
        if dead and (best is None or dead < best[0]):
            best = (dead, list(L.ins), (dyo, dmin, dmax, att))
            r = L.e.ram_all()
            print("stage 2:", best[2], "pig 2 dead at", dead, "toad", rd(r)[:2], flush=True)
    return best


def stage3(L, hp0):
    mk = L.mark()
    best = None
    for wait, depth, jx, hold in itertools.product((0, 4, 8, 14, 20, 28, 36), (72, 78, 86, 96), range(196, 264, 6), (14, 20, 26, 32)):
        L.back(mk)
        L.st("Right", wait)
        got = None
        jumped = False
        for _ in range(170):
            r = L.e.ram_all()
            tx, ty, lvl, pigs, spd, z = rd(r)
            if lvl != 1:
                got = len(L.ins)
                break
            if r[0x51A] < hp0:
                break
            up = "+Up" if ty > depth else ""
            if not jumped and tx >= jx and z == 0 and r[0x439] < 150:
                if spd < 150:
                    L.st("Right" + up)
                    L.st(up.lstrip("+"))
                L.st("Right+A" + up, hold)
                jumped = True
                continue
            if spd < 150 and z == 0 and not jumped:
                L.st("Right" + up)
                L.st(up.lstrip("+"))
            L.st("Right" + up)
        if got and (best is None or got < best[0]):
            best = (got, list(L.ins), (wait, depth, jx, hold))
            print("stage 3:", best[2], "warp at", got, "=", got - LAND, "frames from the landing", flush=True)
    return best


def main():
    e = BizHawk(log_name="l1b.log")
    e.load("L1_go")
    L = Line(e)
    old = json.load(open("logs/pbeam_L1.json"))["inputs"]
    for b in old[:16]:                                      # the drop: nothing matters until the landing
        L.st(b)
    L.st("", LAND - 16)
    hp0 = e.byte(0x51A)
    for name, fn in (("1", stage1), ("2", stage2), ("3", stage3)):
        best = fn(L, hp0)
        if not best:
            print("stage", name, "failed")
            e.close()
            return
        L.e.load("L1_go")
        L.ins = []
        for b in best[1]:
            L.st(b)
    json.dump({"bookmark": "L1_go", "inputs": L.ins,
               "note": "LEVEL 1: the left pig is killed the moment it can be hurt, then one dash to the right: ram the second pig on "
                       "the way, dash-jump onto the rock, into the portal.||Staged scan on savestates; the first version headbutted "
                       "leftwards and had to come back"},
              open("logs/pbeam_L1b.json", "w"))
    print("saved logs/pbeam_L1b.json:", len(L.ins), "inputs =", len(L.ins) - LAND, "frames from the landing (old 300)")
    e.close()


if __name__ == "__main__":
    main()
