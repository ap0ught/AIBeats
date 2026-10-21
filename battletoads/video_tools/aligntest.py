import numpy as np, sys
from fx import *
cap = Cap("cap14")
src = VIDEO / "up14.mkv"
# frames with fast toad motion: queen fall 46050..46080, clinger 29960..29990
for A in (46040, 29960, 41560):
    n = 40
    fr = [np.asarray(f) for f in nes_frames(src, A, n + 20)]   # capture frames A..A+n+19
    res = {}
    for delta in range(0, 12):
        score = 0
        for r in range(A, A + n):
            tb = toad_box(cap, r)
            if not tb: continue
            img = fr[r - A + delta - 0] if 0 <= r - A + delta < len(fr) else None
            # capture frame index = r + delta  -> fr index = r + delta - A
            ci = r + delta - A
            if ci < 0 or ci >= len(fr): continue
            im = fr[ci]
            x0, y0, x1, y1 = [int(v) for v in tb[:4]]
            sub = im[max(0,y0):y1, max(0,x0):x1].astype(int)
            # toad green: G high, R low
            g = ((sub[..., 1] > 120) & (sub[..., 0] < 120) & (sub[..., 2] < 120)).sum()
            score += g
        res[delta] = score
    print(A, res)
