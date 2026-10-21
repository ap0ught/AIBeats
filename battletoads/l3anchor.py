"""Re-join the old approach to the bikes from the new, faster gauntlet so the tunnel skip fires as before.

The skip's respawn depends on the level's global timers ($0B frame counter, $0C half rate = period 512). The old
route stood still at (1416, y 218) before its last dash-jump; from there its inputs lead to the bikes and the
skip. So: from L3n_r3 (new gauntlet, last rat dead, toad standing near x 1428) walk to (1416, 218), stand, idle
until ($0B, $0C) equal the old run's at that standing frame, then replay the old inputs.

    python l3anchor.py  -> knowledge/l3_f4.json (replaces the f4 section), bookmark L3n_f4
"""
import json
import re

from toads.emulator import BizHawk


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def main():
    def g(s, k):
        m = re.search(r"\b" + k + r"=(-?\d+)", s)
        return int(m.group(1)) if m else None
    lines = open("logs/newrun3.trace.txt").read().splitlines()
    F0 = None
    for ln in lines[5800:6268]:
        i, b, s = ln.split("\t")
        if g(s, "x") + 256 * g(s, "xh") == 1416 and g(s, "xspd") == 0 and g(s, "height") == 64:
            F0 = int(i)
    old = [l.rstrip("\n") for l in open("logs/newrun3.inputs.txt") if not l.startswith("#")]
    e = BizHawk(log_name="l3anchor.log")
    for b in old[:F0]:
        e.step(tuple(v for v in b.replace("+", ",").split(",") if v), 1)
    o = e.ram(0, 0x800)
    print("old anchor frame", F0, "toad", tx(o), o[0x41B], "spd", o[0x565], "timers", o[0x0B], o[0x0C], "face", o[0x4A2], flush=True)
    tail = [b.replace(",", "+") for b in old[F0:6268]]
    e.load("L3n_r3")
    ins = []

    def st(b):
        e.step(tuple(v for v in b.split("+") if v), 1)
        ins.append(b)
        return e.ram(0, 0x800)

    for _ in range(60):                                     # depth first
        m = e.ram(0, 0x800)
        if m[0x41B] == o[0x41B]:
            break
        st("Down" if m[0x41B] < o[0x41B] else "Up")
    for _ in range(60):                                     # let it stop
        m = e.ram(0, 0x800)
        if m[0x565] == 0 and m[0x475] == 0:
            break
        st("")
    # exact spot and facing: breadth-first over ('', Left, Right) from here
    goal = lambda m: tx(m) == 1416 and m[0x565] == 0 and m[0x475] == 0 and m[0x4A2] == o[0x4A2] and m[0x41B] == o[0x41B]
    layer = [(e.msave(), [])]
    found = None
    seen = set()
    for depth in range(70):
        nxt = []
        for sid, path in layer:
            for b in ("", "Left", "Right"):
                e.mload(sid)
                e.step((b,) if b else (), 1)
                m = e.ram(0, 0x800)
                if goal(m):
                    found = path + [b]
                    break
                k = (tx(m), m[0x565], m[0x4A2], m[0x3B5])
                if k in seen or abs(tx(m) - 1416) > 40:
                    continue
                seen.add(k)
                nxt.append((e.msave(), path + [b]))
            if found:
                break
        for sid, _ in layer:
            e.mfree(sid)
        if found:
            break
        layer = nxt[:400]
    if not found:
        print("could not reach the exact anchor spot"); e.close(); return
    e.mload(layer[0][0]) if False else None
    # replay the found path from the pre-search state: rebuild by reloading and re-applying everything
    pre = list(ins)
    e.load("L3n_r3")
    ins.clear()
    for b in pre + found:
        st(b)
    m = e.ram(0, 0x800)
    print("new at", tx(m), m[0x41B], "spd", m[0x565], "face", m[0x4A2], "timers", m[0x0B], m[0x0C], "after", len(ins), flush=True)
    e.save("L3n_anchor")
    base = list(ins)
    e.load("L3_bikes_seen")
    bs = e.ram(0, 0x800)
    sk = json.load(open("logs/pbeam_L3skip.json"))["inputs"]
    N_old = o[0x0B] + 256 * (o[0x0C] * 2 // 256 % 2)          # frame counter mod 512 ($0C = N // 2 mod 256)
    for off in (-11, -10, -12, -9, -13, -8, -14, 0):
        e.load("L3n_anchor")
        ins[:] = base
        want = (o[0x0B] + off) % 256
        want_c = (o[0x0C] * 2 + (o[0x0B] & 1) + off) // 2 % 256
        for _ in range(600):
            m = e.ram(0, 0x800)
            if m[0x0B] == want and m[0x0C] == want_c:
                break
            st("")
        for b in tail:
            st(b)
        m = e.ram(0, 0x800)
        d = [hex(i) for i in range(0x3C1, 0x700) if m[i] != bs[i]]
        print("offset", off, "wait total", len(ins), "| at the bikes: toad", tx(m), m[0x41B], "spd", m[0x565], "timers", m[0x0B], m[0x0C],
              "vs old", bs[0x0B], bs[0x0C], "diffs", len(d), d[:10], flush=True)
        if (m[0x0B], m[0x0C]) != (bs[0x0B], bs[0x0C]):
            continue
        e.save("L3n_f4")
        spawn = None
        for k, b in enumerate(sk):
            e.step(tuple(v for v in b.split("+") if v), 1)
            if spawn is None and 0x7F in e.ram(0x3C1, 15):
                spawn = k
        print("  skip: 0x7F at", spawn, "end level", e.byte(0x10), "(old: 470, level 254)", flush=True)
        if spawn and e.byte(0x10) != 3:
            json.dump(ins, open("knowledge/l3_f4.json", "w"))
            print("  saved knowledge/l3_f4.json:", len(ins), "frames (the sprint f4 was 120)")
            break
    e.close()


if __name__ == "__main__":
    main()
