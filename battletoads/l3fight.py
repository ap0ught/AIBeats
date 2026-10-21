"""Level 3 on foot, the TAS's way with closed-loop fights (2026-10-02).

TAS #5093 kills every rat with two blows: a flying attack (jump, B in the air: -16 and a stun) and then the BOOT
(dash + B: a 24-frame wind-up, kills a stunned rat whatever its health). Its blind inputs stop working for us at
its two Left+Right frames (banned; an instant dash out of the boot's recovery), so from there the line is rebuilt
from TAS-shaped pieces whose few free parameters are scanned on savestates:

  pre     mash B through the warp screen to the placement, TAS inputs 13156..13919 (in sync, rats 1-3 die)
  A       wait 11, tap/gap/Right+A (legal dash-jump), TAS inputs 13921..14017: flying attack + boot on rat 915
  T1      TAS inputs 14018.. (the long jump over the first chasm), then Right until the turn point x >= Xt
  B       the rat that drops in BEHIND at 1128 (camera 1024): jump back Left with a flying attack, boot it
  T2      wait, legal dash-jump over the second chasm, Right until the turn point
  C       the rat that drops in at 1432 (camera 1280): back off Left, flying attack to the Right, boot
  T3      dash on to the bikes (x >= 1677)

    python l3fight.py     -> logs/pbeam_L3t.json (bookmark L1route_end), bookmark L3t_bikes
"""
import itertools
import json

from toads.emulator import BizHawk
from l4tas import conv
import l3tas

RATS = (0x47, 0xC7)
ROOT = __import__("os").environ.get("L3F_ROOT", "L1route_end")
TAG = __import__("os").environ.get("L3F_TAG", "t")          # bookmarks L3<TAG>_A/B/C/bikes, logs/pbeam_L3<TAG>.json


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def rats(m):
    return [(s, m[0x3FD + s] | m[0x3EE + s] << 8, m[0x51A + s]) for s in range(2, 15) if m[0x3C1 + s] in RATS]


class Line:
    def __init__(self, e):
        self.e = e
        self.ins = []

    def st(self, b, n=1):
        for _ in range(n):
            self.e.step(tuple(v for v in b.split("+") if v), 1)
            self.ins.append(b)
        return self.e.ram(0, 0x800)

    def ram(self):
        return self.e.ram(0, 0x800)

    def mark(self):
        return self.e.msave(), len(self.ins)

    def back(self, mk):
        self.e.mload(mk[0])
        del self.ins[mk[1]:]

    def idle_until_free(self, limit=80):
        """no input until the toad stands idle (anim 1) on the ground"""
        for _ in range(limit):
            m = self.ram()
            if m[0x3B5] == 1 and m[0x475] == 0:
                return True
            self.st("")
        return False


def alive(m, lives0, hp0):
    return m[0x11] == lives0 and m[0x51A] >= hp0 and m[0x10] == 3


def main():
    rows = l3tas.load("tas/ram_l3_1p.txt")
    e = BizHawk(log_name="l3fight.log")
    e.load(ROOT)
    L = Line(e)
    for k in range(700):
        m = L.st("B" if k % 2 == 0 else "")
        if l3tas.placed(m):
            break
    for f in range(13156, 13920):
        m = L.st("+".join(conv(rows[f][0])))
    lives0, hp0 = m[0x11], m[0x51A]
    print("TAS line in sync to input", len(L.ins), "toad", tx(m), m[0x41B], "rats", rats(m), flush=True)

    import os
    if os.path.exists(f"knowledge/l3{TAG}_B.json"):                               # stages A and B already built
        L.ins = json.load(open(f"knowledge/l3{TAG}_B.json"))
        e.load(f"L3{TAG}_B")
        m = L.ram()
        return finish(e, L, m, lives0, hp0)
    # ---- A: rat 915 (walks at the toad)
    best = None
    mk = L.mark()
    for n in range(9, 16):
        L.back(mk)
        L.st("", n)
        L.st("Right")
        L.st("")
        L.st("Right+A")
        dead = None
        for f in range(13921, 14018 + 12):
            m = L.st("+".join(conv(rows[f][0])) if f <= 14017 else "Right")
            if not alive(m, lives0, hp0):
                break
            if not any(hp > 0 for s, x, hp in rats(m)):
                dead = len(L.ins)
                break
        print("A: wait", n, "rat dead at input", dead, flush=True)
        if dead and (best is None or dead < best[0]):
            best = (dead, list(L.ins), n)
    L.back(mk)
    for b in best[1][mk[1]:]:
        m = L.st(b)
    e.save(f"L3{TAG}_A")
    print("A done: input", len(L.ins), "toad", tx(m), m[0x41B], "cam", m[0x87] | m[0x88] << 8, flush=True)

    # ---- T1 + B: the chasm jump, the turn at the second chasm's edge, the rat dropping in behind at 1128
    tas_t1 = ["+".join(conv(rows[f][0])) for f in range(14018, 14188)]       # ends running Right at x ~1221
    mk = L.mark()
    best = None
    for cut, xt, a, nl in itertools.product((0, 4, 8), range(1211, 1231, 3), (26, 30, 34), (2, 3, 5)):
        L.back(mk)
        ok = True
        for b in tas_t1[:len(tas_t1) - 40]:
            m = L.st(b)
        for _ in range(120):                                                 # run on to the turn point
            m = L.ram()
            if tx(m) >= xt - cut or not alive(m, lives0, hp0):
                break
            L.st("Right")
        if not alive(m, lives0, hp0) or m[0x439] != 64:
            continue
        L.st("Left")
        L.st("")
        L.st("Left+A", a)
        L.st("Left+B", 2)
        L.st("Left", 12)
        hit = False
        for _ in range(70):
            m = L.st("")
            r = rats(m)
            if r and min(hp for s, x, hp in r) < 31:
                hit = True
            if m[0x3B5] == 1 and m[0x475] == 0:
                break
        if not hit or not alive(m, lives0, hp0):
            continue
        rx = [x for s, x, hp in rats(m) if hp > 0]
        if not rx:
            continue
        d = "Right" if rx[0] > tx(m) else "Left"                             # boot toward the rat after a short run-up away from it
        o = "Left" if d == "Right" else "Right"
        L.st(o)
        L.st("")
        L.st(o, nl)
        L.st(d + "+B")
        dead = None
        for _ in range(45):
            m = L.st(d)
            if not alive(m, lives0, hp0):
                break
            if not any(hp > 0 for s, x, hp in rats(m)):
                dead = len(L.ins)
                break
        if dead:
            print("B:", (cut, xt, a, nl), "rat dead at input", dead, "toad", tx(m), m[0x41B], flush=True)
            if best is None or dead < best[0]:
                best = (dead, list(L.ins))
    if not best:
        print("B: no kill")
        e.close()
        return
    L.back(mk)
    for b in best[1][mk[1]:]:
        m = L.st(b)
    e.save(f"L3{TAG}_B")
    print("B done: input", len(L.ins), "toad", tx(m), m[0x41B], "cam", m[0x87] | m[0x88] << 8, flush=True)
    json.dump(L.ins, open(f"knowledge/l3{TAG}_B.json", "w"))
    return finish(e, L, m, lives0, hp0)


def finish(e, L, m, lives0, hp0):
    import os
    if os.path.exists(f"knowledge/l3{TAG}_C.json"):
        L.ins = json.load(open(f"knowledge/l3{TAG}_C.json"))
        e.load(f"L3{TAG}_C")
        m = L.ram()
        return finish3(e, L, m, lives0, hp0)

    # ---- T2 + C: second chasm, the rat dropping in at 1432
    mk = L.mark()
    best = None
    for n, yt, xt, nb, ni, a in itertools.product((16, 20), (213, 216, 219), (1445, 1452, 1459), (24, 28, 32), (7, 11, 15), (6, 8, 10)):
        L.back(mk)
        L.idle_until_free()
        L.st("", n)
        L.st("Right")
        L.st("")
        m = L.st("Right+A", 36)
        if m[0x565] < 160:
            continue                                                         # no dash: the boot's recovery was not over
        for _ in range(140):
            m = L.ram()
            if tx(m) >= xt or not alive(m, lives0, hp0):
                break
            L.st("Right+Up" if m[0x475] == 0 and m[0x41B] > yt else "Right+Down" if m[0x475] == 0 and m[0x41B] < yt - 1 else "Right")   # onto the rat's lane
        if not alive(m, lives0, hp0) or tx(m) < xt:
            continue
        L.st("Left")
        L.st("")
        L.st("Left", nb)
        L.st("", ni)
        L.st("Right")
        L.st("")
        L.st("Right+A", a)
        L.st("Right+A+B")
        L.st("Right+B")
        hit = False
        for _ in range(80):
            m = L.st("Right")
            r = rats(m)
            if r and min(hp for s, x, hp in r) < 47:
                hit = True
            if m[0x3B5] == 1 and m[0x475] == 0:
                break
        if not hit or not alive(m, lives0, hp0):
            continue
        L.st("")
        L.st("Right")
        L.st("Right+B")
        dead = None
        for _ in range(45):
            m = L.st("Right")
            if not alive(m, lives0, hp0):
                break
            if not any(hp > 0 for s, x, hp in rats(m)):
                dead = len(L.ins)
                break
        if dead:
            print("C:", (n, yt, xt, nb, ni, a), "rat dead at input", dead, "toad", tx(m), m[0x41B], flush=True)
            if best is None or dead < best[0]:
                best = (dead, list(L.ins))
    if not best:
        print("C: no kill")
        json.dump(L.ins, open("knowledge/l3t_partial.json", "w"))
        e.close()
        return
    L.back(mk)
    for b in best[1][mk[1]:]:
        m = L.st(b)
    e.save(f"L3{TAG}_C")
    print("C done: input", len(L.ins), "toad", tx(m), m[0x41B], "cam", m[0x87] | m[0x88] << 8, flush=True)
    json.dump(L.ins, open(f"knowledge/l3{TAG}_C.json", "w"))

    return finish3(e, L, m, lives0, hp0)


def finish3(e, L, m, lives0, hp0):
    # ---- T3: on to the bikes
    mk = L.mark()
    best = None
    for n, k, a, yt in itertools.product((0, 2, 4, 8, 12, 16), range(0, 44, 4), (0, 1, 8, 16, 30), (212, 218)):
        L.back(mk)
        L.idle_until_free()
        L.st("", n)
        L.st("Right")
        L.st("")
        m = L.st("Right")
        if m[0x565] < 160:
            continue
        got = None
        j = 0
        for _ in range(160):
            m = L.ram()
            v = "+Down" if m[0x41B] < yt - 1 else "+Up" if m[0x41B] > yt + 1 else ""
            if j == k and a:
                m = L.st("Right+A" + v, a)
            else:
                m = L.st("Right" + v)
            j += 1
            if not alive(m, lives0, hp0):
                break
            if tx(m) >= 1677 and any(m[0x3C1 + s] == 0x18 for s in range(1, 15)) and m[0x439] == 64:
                got = len(L.ins)
                break
        if got and (best is None or got < best[0]):
            best = (got, list(L.ins))
            print("T3:", (n, k, a, yt), "bikes at input", got, "toad", tx(m), m[0x41B], "h", m[0x439], "spd", m[0x565], "timers", m[0x0B], m[0x0C], flush=True)
    if not best:
        print("T3: not reached")
        e.close()
        return
    L.back(mk)
    for b in best[1][mk[1]:]:
        m = L.st(b)
    e.save(f"L3{TAG}_bikes")
    json.dump({"bookmark": ROOT, "inputs": L.ins,
               "note": "LEVEL 3 on foot, the TAS's way: every rat gets a flying attack and then the boot (dash + B) - two blows, "
                       "about 95 frames from the moment it drops in.||" + f"{len(L.ins)} frames to the bikes"},
              open(f"logs/pbeam_L3{TAG}.json", "w"))
    print(f"saved logs/pbeam_L3{TAG}.json:", len(L.ins), "frames to the bikes (was 2847)")
    e.close()


if __name__ == "__main__":
    main()
