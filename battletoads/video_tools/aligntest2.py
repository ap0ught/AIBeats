import numpy as np
from fx import *
cap = Cap("cap14")
src = VIDEO / "up14.mkv"
for A in (2100, 28930, 41470, 41560, 46040, 29960):
    n = 50
    fr = [np.asarray(f) for f in nes_frames(src, A + 6 - 8, n + 20)]   # capture frames A-2 .. (row A shown at capture A+6)
    res = {}
    for df in range(-2, 8):
        score = 0
        for r in range(A, A + n):
            tb = toad_box(cap, r + df)                  # data row r+df vs picture of row r (capture r+6)
            if not tb: continue
            im = fr[r - A + 8]
            x0, y0, x1, y1 = [int(v) for v in tb[:4]]
            sub = im[max(0, y0):max(0, y1), max(0, x0):max(0, x1)].astype(int)
            score += ((sub[..., 1] > 120) & (sub[..., 0] < 120) & (sub[..., 2] < 120)).sum()
        res[df] = int(score)
    best = max(res, key=res.get)
    print(A, "best df", best, res)
