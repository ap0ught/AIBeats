"""Sprite clusters -> RAM objects for the run1080 tracking cues. Like fx.objects_on_screen, but sprites are grouped by
palette and touching rectangles (not OAM order), so a big multi-tile boss such as the Dark Queen comes out as one box,
score pop-ups stay separate, and the toad's own tiles above 0x20 (its feet) join the toad.

Coordinates are raw OAM pixels (x, y + 1), as in fx: subtract 8 from y for the capture picture."""
from __future__ import annotations

from ramview import Cap

SKIP_IDS = (0x04, 0x0c, 0x22, 0x30, 0x41, 0x42, 0x44)


def _touch(a, b, gap):
    return a[0] <= b[2] + gap and b[0] <= a[2] + gap and a[1] <= b[3] + gap and b[1] <= a[3] + gap


def _clusters(rects, gap=2):
    """union of rectangles that touch (within gap); rects are [x0, y0, x1, y1, n]"""
    boxes = [list(r) for r in rects]
    merged = True
    while merged:
        merged = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                if _touch(boxes[i], boxes[j], gap):
                    a, b = boxes[i], boxes[j]
                    boxes[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), a[4] + b[4]]
                    del boxes[j]
                    merged = True
                    break
            if merged:
                break
    return boxes


def objects(cap: Cap, f):
    """[(box, obj)] for frame row f: the toad (slot 0) and every sprite cluster matched to a RAM object"""
    o = cap.oam[f]
    sp = [(int(o[i + 3]), int(o[i]) + 1, int(o[i + 1]), int(o[i + 2]) & 3) for i in range(0, 256, 4) if o[i] < 239]
    toad = [s for s in sp if 1 <= s[2] < 0x20]
    rest = [s for s in sp if not (1 <= s[2] < 0x20)]
    res = []
    if len(toad) < 3:
        return res
    tb = _clusters([[s[0], s[1], s[0] + 8, s[1] + 8, 1] for s in toad], gap=8)
    tb = max(tb, key=lambda b: b[4])
    tpals = {s[3] for s in toad}
    groups = {}
    for s in rest:
        groups.setdefault(s[3], []).append([s[0], s[1], s[0] + 8, s[1] + 8, 1])
    boxes = []
    for pal, rects in groups.items():
        for b in _clusters(rects):
            if pal in tpals and _touch(b, tb, 1) and b[4] <= 4:      # the toad's own extra tiles
                tb = [min(tb[0], b[0]), min(tb[1], b[1]), max(tb[2], b[2]), max(tb[3], b[3]), tb[4] + b[4]]
            elif b[4] >= 2:
                boxes.append(b)
    t0 = cap.obj(f, 0)
    off = t0["x"] - (tb[0] + tb[2]) / 2
    res.append((tuple(tb[:4]), t0))
    objs = [cap.obj(f, s) for s in range(2, 15)]
    objs = [ob for ob in objs if ob["id"] and ob["id"] not in SKIP_IDS]
    used = set()
    for ob in objs:                         # each object takes its nearest unclaimed cluster (bigger wins a tie)
        best = None
        for i, b in enumerate(boxes):
            if i in used:
                continue
            dist = abs(ob["x"] - off - (b[0] + b[2]) / 2)
            if dist <= 32 and (best is None or (dist - b[4], i) < best[0]):
                best = ((dist - b[4], i), i)
        if best:
            used.add(best[1])
            res.append((tuple(boxes[best[1]][:4]), ob))
    return res
