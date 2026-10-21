"""u17v_align.py - piecewise alignment of up17's toad track with up16b2's, per level: stretches of >= 30 frames where
(x, height, depth, pose, health, camera) are identical at some constant shift = re-used play; the rest = new play."""
import json
from u17v_analyze import Cap, FIX
from u17v_compare import NAMES


def trk(cap, f):
    r = cap.ram(f)
    return (r[0x3FD], r[0x3EE], r[0x439], r[0x42A], r[0x41B], r[0x3B5], r[0x51A], r[0x87], r[0x88], r[0x89], r[0x8A])


new, ref = Cap("run1"), Cap("ref16b2")
an = json.loads((FIX / "u17v_run1_analysis.json").read_text())
ar = json.loads((FIX / "u17v_ref16b2_analysis.json").read_text())
out = {}
for a, b in zip(an["levels"], ar["levels"]):
    na, nb = a["frames"], b["frames"]
    ta = [trk(new, a["first"] + i) for i in range(na)]
    tb = [trk(ref, b["first"] + i) for i in range(nb)]
    index = {}
    for j in range(nb - 8):
        index.setdefault(tuple(tb[j:j + 8]), []).append(j)
    segs = []
    i = 0
    newf = 0
    while i < na:
        best = (0, None)
        for j in index.get(tuple(ta[i:i + 8]), []):
            n = 0
            while i + n < na and j + n < nb and ta[i + n] == tb[j + n]:
                n += 1
            if n > best[0]:
                best = (n, j)
        if best[0] >= 30:
            segs.append((i, best[1], best[0]))
            i += best[0]
        else:
            i += 1
            newf += 1
    out[a["first"]] = segs
    print(f"{NAMES[a['byte']]} (up17 {a['first']}-{a['last']}, {na} f; up16b2 {b['first']}-{b['last']}, {nb} f): "
          f"{na - newf} frames re-used in {len(segs)} stretches, {newf} frames new")
    # merge segments with the same shift separated by short gaps for a readable list
    merged = []
    for i, j, n in segs:
        if merged and merged[-1][3] == j - i and i - (merged[-1][0] + merged[-1][2]) <= 40:
            merged[-1][2] = i + n - merged[-1][0]
        else:
            merged.append([i, j, n, j - i])
    pos = 0
    for i, j, n, sh in merged:
        if i > pos:
            print(f"     NEW   up17 {a['first'] + pos}-{a['first'] + i - 1} ({i - pos} f)")
        print(f"     same  up17 {a['first'] + i}-{a['first'] + i + n - 1} ({n} f) = up16b2 {b['first'] + j}-{b['first'] + j + n - 1} "
              f"(level-relative shift {sh:+d})")
        pos = i + n
    if pos < na:
        print(f"     NEW   up17 {a['first'] + pos}-{a['first'] + na - 1} ({na - pos} f)")
