"""EARLY track (2026-10-09): Karnath warp room, part 5 - the JUMP off the snake's left side over its head.

Parts 2/3: the toad can climb above the head and walk over it by r+200, but from there it only falls and lands in the
spikes 60 px short of the ledge (early_l6vault3.py).  The record's toad rises ~15 px relative to the head in the 6
frames it takes to cross (video 187.80 -> 187.90) and then flies at ~3.3 px/frame: a real jump, started from the left
side when its top is about 5 px under the head's top.  Parts 2's let-go moves all KEPT A held (the beam climbs by
holding A), so no fresh press was ever tested.  Here: the same jump-grab (x 84, Right+A x16 at r+98) and climb beam,
and from the 8 highest states of every layer from r+146 on: release for g frames (nothing / Right / Left), then
Right+A for h frames, then Right.  A toad right of the head (x >= 126) and at least 10 px above its coordinate while
the head still rises counts as a jump; each such state gets a flight beam to the ledge.

    python early_l6vault5.py   -> logs/fix/early_l6vault5.txt, early_l6vault5_best.json
"""
import itertools
import json

from early_l6vault2 import rd, bt, ROOT, UP14_PORTAL, LOGS_DIR, BizHawk

out = []


def say(t):
    print(t[:300], flush=True)
    out.append(t)


def flight(e, sid, lives0, base_len, width=500, steps=75):
    """beam from a state just right of the head to the portal ledge; returns (total frames to the portal, inputs) or None"""
    ACTS = [(), ("Right",), ("Left",), ("A",), ("Right", "A"), ("Left", "A")]
    layer, best = [(sid, [])], None
    own = []
    for step in range(steps):
        nxt, seen = [], set()
        for s_id, path in layer:
            for a in ACTS:
                e.mload(s_id)
                e.step(a, 2)
                t = rd(e)
                if t["hp"] < 47 or t["lives"] < lives0:
                    continue
                p = path + ["+".join(a)] * 2
                if t["z"] == 0 and 7510 <= t["H"] <= 7526 and t["x"] >= 330:
                    n, tt = 0, t
                    while n < 80 and tt["rtn"] != 0xE50D and tt["hp"] >= 47:
                        e.step(("Right",), 1)
                        n += 1
                        tt = rd(e)
                    if tt["rtn"] == 0xE50D and (best is None or base_len + len(p) + n < best[0]):
                        best = (base_len + len(p) + n, p + ["Right"] * n)
                    continue
                m = e.ram_all()
                key = (t["x"] // 2, t["H"] // 3, t["z"], m[0x448] // 16, m[0x466] // 16, m[0x4C0] // 16, t["spd"] // 16)
                if key in seen:
                    continue
                seen.add(key)
                rank = t["x"] + (0.35 * min(t["H"], 7780) if t["x"] < 300 else 0.35 * 7780 - 0.1 * abs(t["H"] - 7540))
                nxt.append((rank, e.msave(), p))
        for s_id, _ in layer:
            if s_id != sid:
                e.mfree(s_id)
        nxt.sort(key=lambda n: -n[0])
        layer = [(n[1], n[2]) for n in nxt[:width]]
        for n in nxt[width:]:
            e.mfree(n[1])
        if not layer or (best and base_len + 2 * (step + 1) > best[0] + 6):
            break
    for s_id, _ in layer:
        if s_id != sid:
            e.mfree(s_id)
    return best


def main():
    lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
    e = BizHawk(log_name="early_l6vault5.log")
    e.load("cap14_f11000")
    for i in range(11000, ROOT):
        e.step(bt(lines[i]), 1)
    lives0 = rd(e)["lives"]
    # the jump-grab of part 2 (x0 84, rj 98, a 16), then up14's rhythm to r+135
    ins = []
    for r in range(135):
        t0 = rd(e)
        if r < 98:
            inp = ("Right",) if t0["x"] < 83 and t0["z"] == 0 else (("Left",) if t0["x"] > 85 and t0["z"] == 0 else ())
        elif r < 114:
            inp = ("Right", "A")
        else:
            inp = ("Left", "A") if ((r - 114) // 4) % 2 == 0 else ("Right", "A")
        e.step(inp, 1)
        ins.append("+".join(inp))
    t = rd(e)
    say(f"grab state r+135: toad x {t['x']} H {t['H']} anim {t['an']} rel {t['H'] - t['head'][1]}")
    ACTS = [(), ("A",), ("Left", "A"), ("Right", "A"), ("Left",), ("Right",)]
    layer = [(e.msave(), list(ins))]
    jumps, portal = [], None
    for r in range(135, 200):
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
        layer = [(n[1], n[2]) for n in nxt[:250]]
        for n in nxt[250:]:
            e.mfree(n[1])
        if r + 1 >= 146:
            hits = 0
            for rel, sid, path, x, an in nxt[:8]:
                for rel_btn, g, h in itertools.product(((), ("Right",), ("Left",)), (1, 2, 3), (3, 8, 14, 22, 32)):
                    e.mload(sid)
                    seq = [rel_btn] * g + [("Right", "A")] * h + [("Right",)] * (26 - h if h < 26 else 0)
                    done = []
                    for b in seq[:30]:
                        e.step(b, 1)
                        done.append("+".join(b))
                        t = rd(e)
                        if t["hp"] < 47:
                            break
                        if t["x"] >= 126 and t["head"] and t["head"][1] < 7758 and t["H"] - t["head"][1] >= 10:
                            hits += 1
                            jumps.append((r + 1, rel, "+".join(rel_btn) or "-", g, h, len(done), t["x"], t["H"], t["H"] - t["head"][1], t["an"], t["spd"]))
                            if len(jumps) <= 12:
                                say(f"  JUMP OVER: from r+{r + 1} rel {rel}: release '{'+'.join(rel_btn) or '-'}' x{g}, Right+A x{h}: after {len(done)} f toad x {t['x']} H {t['H']} rel {t['H'] - t['head'][1]} anim {t['an']} spd {t['spd']}")
                            st = e.msave()
                            fl = flight(e, st, lives0, len(path) + len(done))
                            e.mfree(st)
                            if fl and (portal is None or fl[0] < portal[0]):
                                portal = (fl[0], path + done + fl[1])
                                json.dump({"from_frame": ROOT, "inputs": portal[1], "portal_r": portal[0], "up14_portal_r": UP14_PORTAL},
                                          open(LOGS_DIR / "fix" / "early_l6vault5_best.json", "w"))
                                say(f"  PORTAL at r+{portal[0]} (up14 r+{UP14_PORTAL}: saves {UP14_PORTAL - portal[0]})")
                            break
            if (r + 1) % 4 == 0:
                say(f"  r+{r + 1}: best rel {nxt[0][0]} (x {nxt[0][3]}), jumps over so far {len(jumps)}")
        if not layer:
            break
    say(f"{len(jumps)} fresh-press jumps got over the rising head; best portal {portal[0] if portal else None} (up14 r+{UP14_PORTAL})")
    open(LOGS_DIR / "fix" / "early_l6vault5.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
    e.close()


if __name__ == "__main__":
    main()
