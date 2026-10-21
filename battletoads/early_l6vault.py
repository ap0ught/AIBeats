"""EARLY track (2026-10-09): Karnath's Lair warp room - VAULT over the rising snake head (the record's line).

Read off the record's video (logs/fix/wr_karnath_2.jpg, 0.1-s steps): his toad climbs the snake's left side about as
fast as ours, but when it reaches the head (snake clock S ~105-110, ours r+176..182) it goes OVER the still-rising
head to the right and flies to the portal's ledge: ~55 px above the first star (world x 231, H ~7647), then down
under the next two (x 316 / 351, H ~7677).  up14 stays under the head until it turns (r+228), runs along the body
and drops off: ledge at r+332, portal at r+372.  The 2026-10-02 searches (l6room2d/e.py) looked for a toad STANDING on
the head, or held Right for the whole flight (which dies on the stars at x 257-290).

Two stages on a snapshot of up14 (root = frame 11910 + f0, up14's own inputs up to there):
  1. breadth-first over the pad (8 states, 1 frame each, DEPTH frames), states ranked by height above the head:
     collect states RIGHT of the head (x >= 126) at or above its top, alive
  2. from each: flight shaping - Right for h1 frames, nothing/Left for h2, Right to the end (A kept for n frames)
     success = the portal's routine pointer ($E50D) with hp 47

    python early_l6vault.py [f0 list, default 170,176,182,188]  -> logs/fix/early_l6vault.txt, early_l6vault_best.json
"""
import itertools
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR

ROOT = 11910
UP14_PORTAL = 372
ACTS = [(), ("Left",), ("Right",), ("A",), ("Left", "A"), ("Right", "A"), ("Up",), ("Down",)]
DEPTH, WIDTH = 44, 400
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
out = []


def say(*a):
    t = " ".join(str(x) for x in a)
    print(t, flush=True)
    out.append(t)


def rd(e):
    m = e.ram_all()
    hd = None
    for q in range(1, 15):
        if m[0x3C1 + q] == 0x4C:
            hd = (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8)
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                spd=m[0x565], face=m[0x4A2] & 0x40, lift=m[0x484], rtn=m[0x23] | m[0x24] << 8, head=hd)


def main():
    f0s = [int(v) for v in sys.argv[1].split(",")] if len(sys.argv) > 1 else [170, 176, 182, 188]
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l6vault.log")
    e.load("cap14_f11000")
    for i in range(11000, ROOT):
        e.step(bt(lines[i]), 1)
    room = e.msave()
    best = None
    for f0 in f0s:
        e.mload(room)
        for i in range(ROOT, ROOT + f0):
            e.step(bt(lines[i]), 1)
        s = rd(e)
        lives0 = s["lives"]
        say(f"=== f0 r+{f0}: toad x {s['x']} H {s['H']} anim {s['an']} head {s['head']} dH {s['H'] - s['head'][1]}")
        layer = [(e.msave(), [])]
        over, maxx = [], 0
        for depth in range(DEPTH):
            nxt = []
            seen = set()                                         # per layer: the head moves, so the same relative state at a later frame is a NEW state
            for sid, path in layer:
                for a in ACTS:
                    e.mload(sid)
                    e.step(a, 1)
                    t = rd(e)
                    if t["lives"] < lives0 or t["hp"] < 47 or not t["head"]:
                        continue
                    rel = t["H"] - t["head"][1]
                    key = (t["x"], rel, t["z"], t["an"], t["spd"] // 8, t["face"], t["lift"] // 4, "A" in a)
                    if key in seen:
                        continue
                    seen.add(key)
                    p = path + ["+".join(a)]
                    if rel >= -45:
                        maxx = max(maxx, t["x"])
                    if t["x"] >= 126 and rel >= -30:
                        over.append((e.msave(), p, t["x"], rel, t["an"], t["spd"]))
                    else:
                        nxt.append((rel + 0.5 * (t["x"] - 95), e.msave(), p))
            for sid, _ in layer:
                e.mfree(sid)
            nxt.sort(key=lambda n: -n[0])
            layer = [(sid, p) for _, sid, p in nxt[:WIDTH]]
            for _, sid, _ in nxt[WIDTH:]:
                e.mfree(sid)
            if depth % 6 == 5:
                say(f"  depth {depth + 1}: layer {len(layer)}, best rank {nxt[0][0] if nxt else None}, rightmost x near the head {maxx}, right-of-head states {len(over)}")
            if len(over) >= 120 or not layer:
                break
        say(f"  over-the-head states: {len(over)}; first: {[(len(p), x, rel, an, spd) for _, p, x, rel, an, spd in over[:8]]}")
        for sid, path, x, rel, an, spd in over:
            for h1, h2, mid, keep_a in itertools.product((0, 8, 16, 24, 32, 40, 50, 60, 200), (0, 6, 12, 18, 24, 32), ("", "Left"), (0, 10, 20)):
                if h1 == 200 and (h2 or mid):
                    continue
                e.mload(sid)
                seq = [("Right",)] * h1 + [bt(mid)] * h2 + [("Right",)] * 220
                seq = [tuple(sorted(set(b) | {"A"})) if j < keep_a else b for j, b in enumerate(seq)]
                got, n = None, 0
                for b in seq[:230]:
                    e.step(b, 1)
                    n += 1
                    t = rd(e)
                    if t["rtn"] == 0xE50D:
                        got = n
                        break
                    if t["lives"] < lives0 or t["hp"] < 47:
                        break
                if got:
                    total = f0 + len(path) + got
                    if best is None or total < best[0]:
                        full = [lines[i] for i in range(ROOT, ROOT + f0)] + path + ["+".join(b) for b in seq[:got]]
                        best = (total, full)
                        json.dump({"from_frame": ROOT, "inputs": full, "portal_r": total, "up14_portal_r": UP14_PORTAL},
                                  open(LOGS_DIR / "fix" / "early_l6vault_best.json", "w"))
                        say(f"  PORTAL at r+{total} (up14 r+{UP14_PORTAL}: saves {UP14_PORTAL - total}); vault {len(path)} f from r+{f0}, over at x {x} rel {rel}, "
                            f"flight Right {h1} / '{mid}' {h2} / Right, A kept {keep_a}")
        for sid, *_ in over:
            e.mfree(sid)
        for sid, _ in layer:
            e.mfree(sid)
    say(f"best: {best[0] if best else None} (up14 r+{UP14_PORTAL})")
    open(LOGS_DIR / "fix" / "early_l6vault.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()
