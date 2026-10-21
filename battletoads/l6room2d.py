"""Karnath's Lair room 2, the record's way, third try (2026-10-02). Facts so far: mashing Left+A / Right+A every
frame from frame 84 climbs the snake's left side (x 104) at ~2.85 px/frame and reaches the HEAD's top by frame
~150. From there the record gets over the head and flies ~215 px to the portal's ledge. This searches the first
`DEPTH` frames after frame f0 breadth-first (8 pad states), then holds Right; any line whose toad lands on the
ledge (x >= 336, h 94) or engages the warp counts.

    python l6room2d.py   -> knowledge/l6_room2_fast4.json
"""
import json

from toads.emulator import BizHawk
from l6 import toad, head

ACTS = ["", "Left", "Right", "A", "Left+A", "Right+A", "Down", "Up"]
DEPTH = 22


def main():
    e = BizHawk(log_name="l6room2.log")
    old = json.load(open("knowledge/l6_room2_fast.json"))
    e.load("L6r_room2")
    lives0 = e.byte(0x11)
    pre = old[:79] + [""] * 5
    for b in pre:
        e.step(tuple(v for v in b.split("+") if v), 1)
    mash = ["Left+A", "Right+A"]
    best = None
    n = len(pre)
    k = 0
    for f0 in range(126, 200, 6):
        while n < f0:
            b = mash[k % 2]
            e.step(tuple(b.split("+")), 1)
            pre = pre + [b]
            k += 1
            n += 1
        root = e.msave()
        r = e.ram_all()
        t, h = toad(r), head(r)
        print("f0", f0, "toad", t["x"], t["h"], "head", h and (h["x"], h["h"]), flush=True)
        layer = [(e.msave(), [])]
        seen = set()
        finals = []
        for depth in range(DEPTH):
            nxt = []
            for sid, path in layer:
                for a in ACTS:
                    e.mload(sid)
                    e.step(tuple(v for v in a.split("+") if v), 1)
                    r = e.ram_all()
                    t, h = toad(r), head(r)
                    if t["lives"] < lives0 or t["hp"] < 47:
                        continue
                    key = (t["x"], t["h"], t["z"], r[0x3B5], r[0x565] // 8, r[0x4A2] & 0x40, r[0x484] // 4, "A" in a)
                    if key in seen:
                        continue
                    seen.add(key)
                    nxt.append((e.msave(), path + [a]))
            for sid, _ in layer:
                e.mfree(sid)
            nxt.sort(key=lambda s: -toad_x(e, s))
            layer = nxt[:500]
            finals += [p for _, p in layer[:60]]
        ok = 0
        for sid, path in layer:
            e.mload(sid)
            tail = []
            got = None
            for _ in range(150):
                e.step(("Right",), 1)
                tail.append("Right")
                r = e.ram_all()
                t = toad(r)
                if (r[0x23], r[0x24]) == (0x0D, 0xE5):
                    got = len(pre) + len(path) + len(tail)
                    break
                if t["lives"] < lives0 or t["hp"] == 0:
                    break
            if got:
                ok += 1
                if best is None or got < len(best):
                    best = pre + path + tail
                    json.dump(best, open("knowledge/l6_room2_fast4.json", "w"))
                    print("  warp at", got, "path", path, flush=True)
        for sid, _ in layer:
            e.mfree(sid)
        print("  f0", f0, "warps", ok, flush=True)
        e.mload(root)
    print("best", best and len(best), "(old 370)")
    e.close()


def toad_x(e, s):
    e.mload(s[0])
    r = e.ram_all()
    return r[0x3FD] + 256 * r[0x3EE]


if __name__ == "__main__":
    main()
