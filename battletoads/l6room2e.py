"""Karnath's Lair room 2, fourth try (2026-10-02): the record's toad must be STANDING on the rising head when it
jumps (its arc is a full jump). Mash-climb the left side (Left+A / Right+A every frame from frame 84, x 104) to
frame f0, then breadth-first over the pad for DEPTH frames looking for z == 0 above the head (standing on it);
from every standing state try jump-offs to the right: [tap, gap,] Right+A held n, then Right until the warp.

    python l6room2e.py   -> knowledge/l6_room2_fast5.json
"""
import itertools
import json

from toads.emulator import BizHawk
from l6 import toad, head

ACTS = ["", "Left", "Right", "A", "Left+A", "Right+A", "Down", "Up"]
DEPTH = 34


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
    n, k = len(pre), 0
    for f0 in (120, 132, 144, 156, 168):
        while n < f0:
            b = mash[k % 2]
            e.step(tuple(b.split("+")), 1)
            pre = pre + [b]
            k += 1
            n += 1
        root = e.msave()
        layer = [(e.msave(), [])]
        seen = set()
        stands = []
        for depth in range(DEPTH):
            nxt = []
            for sid, path in layer:
                for a in ACTS:
                    e.mload(sid)
                    e.step(tuple(v for v in a.split("+") if v), 1)
                    r = e.ram_all()
                    t, h = toad(r), head(r)
                    if t["lives"] < lives0 or t["hp"] < 47 or not h:
                        continue
                    rel = (t["h"] - h["h"] + 128) % 256 - 128
                    key = (t["x"], rel, t["z"], r[0x3B5], r[0x565] // 8, r[0x4A2] & 0x40, r[0x484] // 4, "A" in a)
                    if key in seen:
                        continue
                    seen.add(key)
                    p = path + [a]
                    if t["z"] == 0 and rel > 8:
                        stands.append((e.msave(), p, t["x"], rel))
                    else:
                        nxt.append((e.msave(), p, rel))
            for s in layer:
                e.mfree(s[0])
            nxt.sort(key=lambda s: -s[2])                    # highest first
            layer = [(s[0], s[1]) for s in nxt[:400]]
            for s in nxt[400:]:
                e.mfree(s[0])
            if len(stands) >= 40:
                break
        print("f0", f0, "standing-on-head states:", len(stands), [(len(p), x, rel) for _, p, x, rel in stands[:6]], flush=True)
        for sid, path, x, rel in stands:
            for wait, dash, hold in itertools.product((0, 4, 8, 16, 24, 32, 44), (0, 1), (12, 20, 32)):
                e.mload(sid)
                tail = [""] * wait + (["Right", ""] if dash else []) + ["Right+A"] * hold
                got = None
                dead = False
                for b in tail + ["Right"] * 150:
                    e.step(tuple(v for v in b.split("+") if v), 1)
                    r = e.ram_all()
                    t = toad(r)
                    if (r[0x23], r[0x24]) == (0x0D, 0xE5):
                        got = True
                        break
                    if t["lives"] < lives0 or t["hp"] == 0:
                        dead = True
                        break
                    tail = tail if len(tail) > 400 else tail
                if got:
                    # count frames precisely by replaying
                    e.mload(sid)
                    seq = [""] * wait + (["Right", ""] if dash else []) + ["Right+A"] * hold
                    cnt = 0
                    for b in seq + ["Right"] * 150:
                        e.step(tuple(v for v in b.split("+") if v), 1)
                        cnt += 1
                        r = e.ram_all()
                        if (r[0x23], r[0x24]) == (0x0D, 0xE5):
                            break
                    total = len(pre) + len(path) + cnt
                    full = pre + path + (seq + ["Right"] * 150)[:cnt]
                    if best is None or total < len(best):
                        best = full
                        json.dump(best, open("knowledge/l6_room2_fast5.json", "w"))
                        print("  warp at", total, "stand after", len(path), "at x", x, "rel", rel, "wait", wait, "dash", dash, "hold", hold, flush=True)
        for s in stands:
            e.mfree(s[0])
        for s in layer:
            e.mfree(s[0])
        e.mload(root)
    print("best", best and len(best), "(old 370)")
    e.close()


if __name__ == "__main__":
    main()
