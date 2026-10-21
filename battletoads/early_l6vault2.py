"""EARLY track (2026-10-09): Karnath warp room, second attempt at the record's line (see early_l6vault.py for the reading
of the video).  Clock: r = frames since up14 frame 11910; the head starts rising at r+71; the record's frames map to
r = 101 + (video - 186.5) * 60: jump at r+113, hanging on the snake ~60 px up at r+119, level with the head's top at
r+173, through the head and out on its right side at r+176..185, black at r+281 (up14: r+357).

up14 starts climbing from the floor at r+106 and is still 32 px under the head at r+176; from there nothing gets it
past the head before the turn (early_l6vault.py, early_l6eject.py).  So:
  stage 1  jump-grab: walk to x0, at r = rj hold Right+A for a frames, then up14's climb rhythm (Left+A x4 / Right+A x4)
           -> the (x0, rj, a) with the highest toad at r+135 relative to the head
  stage 2  beam from that grab, one frame per step, 6 pad states, ranked by height relative to the head (per-layer
           dedupe) to r+190; from the 12 highest states of every 3rd layer try 'let go' moves for 16 frames
           (nothing / A / Right / Right+A / Down / Left+A) and report any toad that gets RIGHT of the head (x >= 126)
           while the head is still rising, and how the flight ends when Right is then held / released

    python early_l6vault2.py   -> logs/fix/early_l6vault2.txt (+ early_l6vault2_best.json on a portal)
"""
import itertools
import json

from toads.emulator import BizHawk, LOGS_DIR

ROOT, UP14_PORTAL = 11910, 372
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
out = []


def say(t):
    print(t[:300], flush=True)
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
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l6vault2.log")
    e.load("cap14_f11000")
    for i in range(11000, ROOT):
        e.step(bt(lines[i]), 1)
    room = e.msave()
    lives0 = rd(e)["lives"]
    # ---- stage 1
    best1 = None
    for x0, rj, a in itertools.product((84, 88, 92, 96, 100), range(98, 124, 2), (4, 8, 12, 16, 20)):
        e.mload(room)
        ins, t = [], None
        for r in range(135):
            t0 = rd(e) if r % 1 == 0 else t0
            if r < rj:
                inp = ("Right",) if t0["x"] < x0 - 1 and t0["z"] == 0 else (("Left",) if t0["x"] > x0 + 1 and t0["z"] == 0 else ())
            elif r < rj + a:
                inp = ("Right", "A")
            else:
                inp = ("Left", "A") if ((r - rj - a) // 4) % 2 == 0 else ("Right", "A")
            e.step(inp, 1)
            ins.append("+".join(inp))
        t = rd(e)
        if t["hp"] < 47 or not t["head"] or t["an"] not in (88, 89):
            continue
        rel = t["H"] - t["head"][1]
        if best1 is None or rel > best1[0]:
            best1 = (rel, x0, rj, a, list(ins), t["x"], t["H"])
    if best1 is None:
        say("stage 1: no jump-grab holds to r+135")
        e.close()
        return
    say(f"stage 1: best jump-grab x0 {best1[1]} rj {best1[2]} A{best1[3]}: at r+135 toad x {best1[5]} H {best1[6]}, {best1[0]} relative to the head "
        f"(up14 at r+135: 7530 - 7584 = -54)")
    # ---- stage 2
    e.mload(room)
    for b in best1[4]:
        e.step(bt(b), 1)
    ACTS = [(), ("A",), ("Left", "A"), ("Right", "A"), ("Left",), ("Right",)]
    LETGO = [(), ("A",), ("Right",), ("Right", "A"), ("Down",), ("Left", "A"), ("Up",)]
    layer = [(e.msave(), list(best1[4]))]
    found, portal_best = [], None
    for r in range(135, 196):
        nxt, seen = [], set()
        for sid, path in layer:
            for a in ACTS:
                e.mload(sid)
                e.step(a, 1)
                t = rd(e)
                if t["hp"] < 47 or not t["head"]:
                    continue
                rel = t["H"] - t["head"][1]
                key = (t["x"], rel, t["z"], t["an"], t["spd"] // 8, t["lift"] // 4, "A" in a)
                if key in seen:
                    continue
                seen.add(key)
                nxt.append((rel, e.msave(), path + ["+".join(a)], t["x"], t["an"]))
        for sid, _ in layer:
            e.mfree(sid)
        nxt.sort(key=lambda n: -n[0])
        layer = [(n[1], n[2]) for n in nxt[:300]]
        for n in nxt[300:]:
            e.mfree(n[1])
        if (r - 135) % 3 == 2:
            say(f"  r+{r + 1}: best height relative to the head {nxt[0][0]} (x {nxt[0][3]} anim {nxt[0][4]}), layer {len(layer)}")
            for rel, sid, path, x, an in nxt[:12]:
                for a in LETGO:
                    e.mload(sid)
                    seq, hit = [], None
                    for j in range(16):
                        e.step(a, 1)
                        seq.append("+".join(a))
                        t = rd(e)
                        if t["hp"] < 47:
                            break
                        if t["x"] >= 126 and t["head"] and t["head"][1] < 7758:
                            hit = (j + 1, t["x"], t["H"], t["H"] - t["head"][1], t["an"], t["z"], t["spd"])
                            break
                    if hit:
                        found.append((r + 1, rel, "+".join(a) or "-", hit))
                        if len(found) <= 10:
                            say(f"    RIGHT OF THE HEAD: from r+{r + 1} (rel {rel}) holding '{'+'.join(a) or '-'}': {hit}")
                        through = e.msave()
                        base = path + seq
                        for h1, h2, mid, keep_a in itertools.product((0, 8, 16, 24, 32, 44, 200), (0, 8, 16, 24), ("", "Left"), (0, 8, 16)):
                            if h1 == 200 and (h2 or mid):
                                continue
                            e.mload(through)
                            fl = [("Right",)] * h1 + [bt(mid)] * h2 + [("Right",)] * 220
                            fl = [tuple(sorted(set(b) | {"A"})) if j < keep_a else b for j, b in enumerate(fl)]
                            for n, b in enumerate(fl[:230]):
                                e.step(b, 1)
                                t = rd(e)
                                if t["rtn"] == 0xE50D:
                                    total = len(base) + n + 1
                                    if portal_best is None or total < portal_best[0]:
                                        portal_best = (total, base + ["+".join(x) for x in fl[:n + 1]])
                                        json.dump({"from_frame": ROOT, "inputs": portal_best[1], "portal_r": total, "up14_portal_r": UP14_PORTAL},
                                                  open(LOGS_DIR / "fix" / "early_l6vault2_best.json", "w"))
                                        say(f"    PORTAL at r+{total} (up14 r+{UP14_PORTAL}: saves {UP14_PORTAL - total}) flight Right {h1} / '{mid}' {h2} / Right, A kept {keep_a}")
                                    break
                                if t["hp"] < 47 or t["lives"] < lives0:
                                    break
                        e.mfree(through)
        if not layer:
            break
    say(f"stage 2: {len(found)} let-go moves put the toad right of the rising head; best portal {portal_best[0] if portal_best else None} (up14 r+{UP14_PORTAL})")
    open(LOGS_DIR / "fix" / "early_l6vault2.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()
