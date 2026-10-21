"""u17v_compare.py - up17 (logs/fix/u17v_run1.ram) against my own replay of the verified up16b2 (u17v_ref16b2.ram),
level by level: which stretches have the same toad track (new work = where they differ), level-end health / lives /
score, and a continuity check of every level (largest per-frame steps of the toad and of the camera)."""
import json
import sys
from pathlib import Path
from u17v_analyze import Cap, FIX

NAMES = {1: "Level 1 Ragnarok's Canyon", 3: "Level 3 Turbo Tunnel", 4: "Level 4 Arctic Caverns", 8: "Level 6 Karnath's Lair",
         7: "Level 8 Intruder Excluder", 11: "Level 9 Terra Tubes", 9: "Level 10 Rat Race", 10: "Level 11 Clinger-Winger",
         5: "Level 12 The Revolution", 13: "Level 13 Armageddon"}


def track(cap, f):
    r = cap.ram(f)
    return (r[0x3FD] + 256 * r[0x3EE], r[0x439] + 256 * r[0x42A], r[0x41B], r[0x3B5], r[0x51A])


def cam(cap, f):
    r = cap.ram(f)
    return (r[0x87] + 256 * r[0x88], r[0x89] + 256 * r[0x8A])


def main():
    new, ref = Cap("run1"), Cap("ref16b2")
    an = json.loads((FIX / "u17v_run1_analysis.json").read_text())
    ar = json.loads((FIX / "u17v_ref16b2_analysis.json").read_text())
    print("level | up17 first-last (frames) | up16b2 first-last (frames) | difference | end lives/health/score up17 = up16b2 ?")
    for a, b in zip(an["levels"], ar["levels"]):
        assert a["byte"] == b["byte"]
        same_end = (a["lives_end"], a["hp_end"], a["score_end"]) == (b["lives_end"], b["hp_end"], b["score_end"])
        print(f"{NAMES[a['byte']]:28s} | {a['first']}-{a['last']} ({a['frames']}) | {b['first']}-{b['last']} ({b['frames']}) | "
              f"{a['frames'] - b['frames']:+d} | {a['lives_end']}/{a['hp_end']}/{a['score_end']} vs {b['lives_end']}/{b['hp_end']}/{b['score_end']} "
              f"{'SAME' if same_end else 'DIFFERENT'}")
    print()
    print("toad track (x, height, depth, pose, health) compared frame by frame, aligned at the level's first frame, shifts -8..+8:")
    for a, b in zip(an["levels"], ar["levels"]):
        na, nb = a["frames"], b["frames"]
        ta = [track(new, a["first"] + i) for i in range(na)]
        tb = [track(ref, b["first"] + i) for i in range(nb)]
        best = None
        for sh in range(-8, 9):               # up17 frame i  <->  up16b2 frame i + sh
            lead = 0
            i = max(0, -sh) + 40                # skip the load
            start = i
            while i < na and 0 <= i + sh < nb and ta[i] == tb[i + sh]:
                i += 1
            lead = i - start
            if best is None or lead > best[1]:
                best = (sh, lead, i)
        # tail: aligned at the level's last frame
        tail = 0
        while tail < min(na, nb) and ta[na - 1 - tail] == tb[nb - 1 - tail]:
            tail += 1
        total_same = sum(1 for i in range(40, na) if 0 <= i + best[0] < nb and ta[i] == tb[i + best[0]])
        print(f"{NAMES[a['byte']]:28s}: identical from the start for {best[1]} frames (shift {best[0]:+d}; first difference at up17 frame "
              f"{a['first'] + best[2] if best[2] < na else 'none'}); identical counted back from the end: {tail} frames; "
              f"level length {na} vs {nb}")
    print()
    print("continuity, every level of up17 (in play = health > 0 and 60 frames after the load): largest per-frame steps")
    for which, cap, lv in (("up17", new, an["levels"]), ("up16b2", ref, ar["levels"])):
        print(which)
        for a in lv:
            f0, f1 = a["first"] + 60, a["last"]
            mx = {"x": (0, 0), "h": (0, 0), "cx": (0, 0), "cy": (0, 0)}
            big = []
            prev = None
            for f in range(f0, f1 + 1):
                t, c = track(cap, f), cam(cap, f)
                if prev is not None and t[4] > 0 and prev[0][4] > 0:
                    dx, dh = t[0] - prev[0][0], t[1] - prev[0][1]
                    dcx, dcy = c[0] - prev[1][0], c[1] - prev[1][1]
                    for k, v in (("x", dx), ("h", dh), ("cx", dcx), ("cy", dcy)):
                        if abs(v) > abs(mx[k][0]):
                            mx[k] = (v, f)
                    if abs(dx) > 8 or abs(dh) > 16 or abs(dcx) > 8 or abs(dcy) > 8:
                        big.append((f, dx, dh, dcx, dcy))
                prev = (t, c)
            print(f"   {NAMES[a['byte']]:28s} max step: toad x {mx['x'][0]:+d} (f{mx['x'][1]}), toad height {mx['h'][0]:+d} (f{mx['h'][1]}), "
                  f"camera x {mx['cx'][0]:+d} (f{mx['cx'][1]}), camera y {mx['cy'][0]:+d} (f{mx['cy'][1]}); frames with a step over "
                  f"8/16/8/8: {len(big)}")
            if big:
                # group
                grp = []
                for b in big:
                    if grp and b[0] - grp[-1][-1][0] <= 3:
                        grp[-1].append(b)
                    else:
                        grp.append([b])
                for g in grp[:40]:
                    print(f"        f{g[0][0]}..{g[-1][0]} ({len(g)}): first (dx {g[0][1]:+d}, dh {g[0][2]:+d}, dcamx {g[0][3]:+d}, dcamy {g[0][4]:+d})")


if __name__ == "__main__":
    main()
