"""Acts 1-2 record trace: work/a56r2/record_trace.py (agent a56's method) on states/tmp/a12r2_vid/<seg>, with the
HUD mask lowered from y 72 to y 60 (1-1's roof route runs at the very top of the playfield, y 60-90).
    python work/a12r2/rtrace.py <seg> <control video frame> <end video frame> <out.json>"""
import sys
import numpy as np
sys.path.insert(0, "work/a56r2")
import record_trace as R
R.D0 = "states/tmp/a12r2_vid/"
TOP = 60


def ryu(im, prev):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    m = (b > r + 50) & (abs(r - g) < 35) & (b > 140)
    m[:TOP] = False
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


R.ryu = ryu
if __name__ == "__main__":
    R.main()
