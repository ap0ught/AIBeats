"""Record-video route trace (agent a56 round 2).

For a stage segment of the record video (frames extracted to states/tmp/a56r2_vid/<dir>/fNNNNN.png, game area
cropped 1200x900 at (600,140) and scaled to 256x240 = 1 NES px per px horizontally), per distinct image:
  room index (black screens = room changes), cumulative horizontal scroll since the room start (background shift),
  Ryu's screen position (densest cluster of Ryu-blue pixels), the HUD timer is not read.
    python work/a56r2/record_trace.py <dir> <video control frame> <video end frame> <out.json>
Times: t_nes = (f - control) * 60.0988 / 60 (NES frames after the stage's control frame).
"""
import json
import sys

import numpy as np
from PIL import Image

D0 = "states/tmp/a56r2_vid/"


def load(d, f):
    return np.asarray(Image.open(f"{D0}{d}/f{f:05d}.png").convert("RGB")).astype(int)


def ryu(im, prev):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    m = (b > r + 50) & (abs(r - g) < 35) & (b > 140)
    m[:72] = False
    ys, xs = np.nonzero(m)
    if len(xs) < 5:
        return None
    best = None
    for cx, cy in zip(xs[::2], ys[::2]):
        n = int(np.sum((abs(xs - cx) < 10) & (abs(ys - cy) < 14)))
        if prev is not None:
            n -= int((abs(cx - prev[0]) + abs(cy - prev[1])) / 12)
        if best is None or n > best[0]:
            best = (n, cx, cy)
    n, cx, cy = best
    sel = (abs(xs - cx) < 10) & (abs(ys - cy) < 14)
    if sel.sum() < 5:
        return None
    return int(round(xs[sel].mean())), int(round(ys[sel].mean())), int(sel.sum())


def shift(cur, prev):
    best = None
    for dx in range(-8, 9):
        if dx >= 0:
            dd = np.abs(cur[:, :248 - dx] - prev[:, dx:248]).mean()
        else:
            dd = np.abs(cur[:, -dx:248] - prev[:, :248 + dx]).mean()
        if best is None or dd < best[0]:
            best = (dd, dx)
    return best[1]


def main():
    d, c, e, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    rows = []
    room = 0
    cum = 0
    prevg = None
    prevr = None
    black = False
    for f in range(c - 4, e):
        try:
            im = load(d, f)
        except Exception:
            continue
        g = im[75:235].mean(axis=2)
        isblack = g.mean() < 8
        if isblack:
            if not black and f > c + 30:
                room += 1
            black = True
            prevg = None
            continue
        if black:
            black = False
            cum = 0
        if prevg is not None and np.abs(g - prevg).mean() < 1.0:
            continue                      # second copy of the same NES image
        if prevg is not None:
            cum += shift(g, prevg)
        prevg = g
        rp = ryu(im, prevr)
        if rp:
            prevr = rp
        rows.append({"f": f, "t": round((f - c) * 60.0988 / 60, 1), "room": room, "scroll": cum,
                     "sx": rp[0] if rp else None, "sy": rp[1] if rp else None, "n": rp[2] if rp else 0})
    json.dump({"dir": d, "control_video": c, "end_video": e, "rows": rows}, open(out, "w"))
    for r in rows[::15]:
        print(r)


if __name__ == "__main__":
    main()
