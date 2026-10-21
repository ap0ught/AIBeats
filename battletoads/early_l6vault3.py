"""EARLY track (2026-10-09): Karnath warp room, part 3 - the flight from the head's top to the portal's ledge.

early_l6vault2.py found the first half of the record's line on a snapshot of up14: jump at the snake at r+98
(Right+A x16 from x 84), climb (the beam mostly just HOLDS A), top of the still-rising head at r+186, and with
Right+A held the toad walks over the head to its right side (x 128, H 7723) by r+200.  Its coarse flight grid only
found a slow portal (r+428; up14: r+372).  Here the flight is searched properly:
    root = the state after `cut` inputs of logs/fix/early_l6vault2_best.json (default 189 = on the head's top)
    beam, 2 frames per step, pad {-, Right, Left, A, Right+A, Left+A}, per-layer dedupe on (x, H, velocity bytes),
    ranked by x (and height while over the spikes), toads that are hurt are dropped
    goal = standing on the portal's ledge (z 0, H 7518, x >= 330); then Right until the portal engages ($E50D)

    python early_l6vault3.py [cut=189] [width=800]  -> logs/fix/early_l6vault3.txt, early_l6vault3_best.json
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR

ROOT, UP14_PORTAL = 11910, 372
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A")]
out = []


def say(t):
    print(t[:300], flush=True)
    out.append(t)


def rd(e):
    m = e.ram_all()
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11],
                spd=m[0x565], v1=m[0x448], v2=m[0x457], v3=m[0x466], v4=m[0x4C0], v5=m[0x4CF], rtn=m[0x23] | m[0x24] << 8)


def main():
    cut = int(sys.argv[1]) if len(sys.argv) > 1 else 189
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 800
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    pre = json.load(open(LOGS_DIR / "fix" / "early_l6vault2_best.json"))["inputs"][:cut]
    e = BizHawk(log_name="early_l6vault3.log")
    e.load("cap14_f11000")
    for i in range(11000, ROOT):
        e.step(bt(lines[i]), 1)
    for b in pre:
        e.step(bt(b), 1)
    s = rd(e)
    lives0 = s["lives"]
    say(f"root r+{cut}: toad x {s['x']} H {s['H']} anim {s['an']} z {s['z']}")
    layer = [(e.msave(), [])]
    best = None
    for step in range(110):
        nxt, seen = [], set()
        for sid, path in layer:
            for a in ACTS:
                e.mload(sid)
                e.step(a, 2)
                t = rd(e)
                if t["hp"] < 47 or t["lives"] < lives0:
                    continue
                p = path + ["+".join(a)] * 2
                if t["z"] == 0 and 7510 <= t["H"] <= 7526 and t["x"] >= 330:
                    # on the ledge: run to the portal
                    n = 0
                    tt = t
                    while n < 80 and tt["rtn"] != 0xE50D and tt["hp"] >= 47:
                        e.step(("Right",), 1)
                        n += 1
                        tt = rd(e)
                    if tt["rtn"] == 0xE50D:
                        total = cut + len(p) + n
                        if best is None or total < best[0]:
                            best = (total, pre + p + ["Right"] * n, (cut + len(p), t["x"]))
                            json.dump({"from_frame": ROOT, "inputs": best[1], "portal_r": total, "up14_portal_r": UP14_PORTAL,
                                       "ledge": best[2]}, open(LOGS_DIR / "fix" / "early_l6vault3_best.json", "w"))
                            say(f"  PORTAL at r+{total} (up14 r+{UP14_PORTAL}: saves {UP14_PORTAL - total}); on the ledge at r+{cut + len(p)} x {t['x']}")
                    continue
                key = (t["x"] // 2, t["H"] // 3, t["z"], t["v1"] // 16, t["v3"] // 16, t["v4"] // 16, t["spd"] // 16)
                if key in seen:
                    continue
                seen.add(key)
                rank = t["x"] + (0.35 * min(t["H"], 7760) if t["x"] < 300 else 0.35 * 7760 - 0.1 * abs(t["H"] - 7540))
                nxt.append((rank, e.msave(), p, t["x"], t["H"]))
        for sid, _ in layer:
            e.mfree(sid)
        nxt.sort(key=lambda n: -n[0])
        layer = [(n[1], n[2]) for n in nxt[:width]]
        for n in nxt[width:]:
            e.mfree(n[1])
        if step % 5 == 4:
            say(f"  step {step + 1} (r+{cut + 2 * (step + 1)}): {len(nxt)} states alive, front x {max(n[3] for n in nxt) if nxt else None}, "
                f"best-ranked ({nxt[0][3]}, {nxt[0][4]})" if nxt else f"  step {step + 1}: nothing alive")
        if not layer or (best and cut + 2 * (step + 1) > best[0] + 10):
            break
    say(f"best portal: r+{best[0] if best else None} (up14 r+{UP14_PORTAL}); saves {UP14_PORTAL - best[0] if best else None} frames in this room")
    open(LOGS_DIR / "fix" / "early_l6vault3.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()
