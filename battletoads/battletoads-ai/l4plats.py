"""Level 4 after checkpoint 5, the direct line (2026-10-01, from the record's video): from the pit's edge
(bookmark L4r_edge = L4r_cp5 + 2 idle + knowledge/l4s_L4r_cp5.json, toad at (178,94)) hop onto floating platform 1
as it heads back left, ride it crouched under the hanging spike, hop to platform 2, and jump off platform 2's
right side straight down onto the lower ledge (h 62, x >= 570) - no pillar top, no upper ledge.

Phase 1 scans the two hops (fastest arrival on platform 2 with full health kept if possible), phase 2 scans the
jump off platform 2. Writes knowledge/l4_plats_direct.json (inputs from L4r_edge) and bookmark L4r_lower.

    python l4plats.py
"""
import itertools
import json

from toads.emulator import BizHawk

ROOT = __import__("os").environ.get("L4PLATS_ROOT", "L4r_edge")


def plats(m):
    return sorted([(m[0x3FD + s] | m[0x3EE + s] << 8, m[0x439 + s]) for s in range(2, 15) if m[0x3C1 + s] == 0x3e],
                  key=lambda p: p[1])


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def main():
    e = BizHawk(log_name="l4plats.log")
    e.load(ROOT)
    root = e.msave()
    m = e.ram(0, 0x800)
    lives0, hp0 = m[0x11], m[0x51A]
    print("root: toad", tx(m), m[0x439], "hp", hp0, "plats", plats(m), flush=True)

    def to_p2(hopx, hold, hop2, hold2):
        e.mload(root)
        seq = []

        def st(b):
            e.step(tuple(v for v in b.split("+") if v), 1)
            seq.append(b)
            return e.ram(0, 0x800)

        last = None
        ok = False
        for _ in range(420):                                 # platform 1 heading left past hopx
            m = e.ram(0, 0x800)
            p = plats(m)
            if not p:
                st("")
                continue
            if last is not None and p[0][0] < last and p[0][0] <= hopx:
                ok = True
                break
            last = p[0][0]
            st("Right" if tx(m) < 174 else "Left" if tx(m) > 178 else "")
            if m[0x11] < lives0:
                return None
        if not ok:
            return None
        for _ in range(hold):
            st("Right+A")
        for _ in range(4):
            st("Right")
        for _ in range(60):
            m = st("")
            if m[0x4B1] & 16:
                break
        if not (m[0x4B1] & 16):
            return None
        for _ in range(320):                                 # ride crouched to platform 1's right end
            m = st("Down")
            if plats(m)[0][0] >= 344 or m[0x11] < lives0:
                break
        if m[0x11] < lives0:
            return None
        for _ in range(hop2):
            st("Down")
        for _ in range(hold2):
            st("Right+A")
        for _ in range(40):
            m = st("Right")
            if (m[0x4B1] & 16) and m[0x439] >= 130:
                return seq, m[0x51A]
            if m[0x11] < lives0:
                return None
        return None

    best = None
    for hopx, hold, hop2, hold2 in itertools.product(range(200, 236, 4), (8, 10), (0, 4, 8, 12, 16), (8, 12, 16)):
        r = to_p2(hopx, hold, hop2, hold2)
        if r and (best is None or (len(r[0]), -r[1]) < (len(best[0]), -best[1])):
            best = r
            print("on platform 2 in", len(r[0]), "hp", r[1], "hopx", hopx, "hold", hold, "hop2", hop2, "hold2", hold2, flush=True)
    if not best:
        print("no platform-2 landing")
        e.close()
        return
    seq1 = best[0]
    e.mload(root)
    for b in seq1:
        e.step(tuple(v for v in b.split("+") if v), 1)
    p2root = e.msave()
    m = e.ram(0, 0x800)
    H0 = m[0x439]
    print("phase 2 from platform 2: toad", tx(m), m[0x439], "plats", plats(m), flush=True)
    best2 = None
    for wait, btn, hold3 in itertools.product(range(0, 150, 6), ("Right+A", "Right"), (2, 6, 10, 14, 18)):
        e.mload(p2root)
        seq = []
        for _ in range(wait):
            e.step(("Right",), 1)                            # walk to/hold the platform's right end while it travels
            seq.append("Right")
        for _ in range(hold3):
            e.step(tuple(btn.split("+")), 1)
            seq.append(btn)
        got = None
        for k in range(90):
            e.step(("Right",), 1)
            seq.append("Right")
            m = e.ram(0, 0x800)
            if m[0x11] < lives0 or m[0x51A] == 0:
                break
            if m[0x475] == 0 and not (m[0x4B1] & 16) and m[0x439] == 62 and tx(m) >= 560:
                got = len(seq)
                break
        if got and (best2 is None or got < len(best2)):
            best2 = list(seq)
            print("lower ledge in", got, "after platform 2: wait", wait, btn, "hold", hold3, "x", tx(m), "hp", m[0x51A], flush=True)
    if not best2:
        print("no direct landing on the lower ledge")
        json.dump(seq1, open("knowledge/l4_plats_p2only.json", "w"))
        e.mload(p2root)
        e.save("L4r_onp2b")
        e.close()
        return
    full = seq1 + best2
    e.mload(root)
    for b in full:
        e.step(tuple(v for v in b.split("+") if v), 1)
    m = e.ram(0, 0x800)
    print("total", len(full), "frames from the edge; toad", tx(m), m[0x439], "hp", m[0x51A], "lives", m[0x11])
    json.dump(full, open("knowledge/l4_plats_direct.json", "w"))
    e.save("L4r_lower")
    e.close()


if __name__ == "__main__":
    main()
