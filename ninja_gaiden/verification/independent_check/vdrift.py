"""Is the record video's timeline real time (60.000 fps clock) or locked to the NES (60.0988)?
Measure the background scroll between consecutive DISTINCT images in a stretch where Ryu runs right at 1.5 px/f.
2 NES frames per image -> 3 NES px; an extra NES frame slipped in (real-time capture of a 60.0988 Hz source)
-> 4-5 NES px, about once every 1/0.0988 = 10.1 s."""
import sys
import numpy as np
import vid

n0, n1 = int(sys.argv[1]), int(sys.argv[2])
prev = None
steps = []
for n, a in vid.frames(n0, n1, (620, 420, 1160, 200), None):
    prof = a.astype(np.float32).mean(axis=(0, 2))
    if prev is not None:
        d = float(np.abs(prof - prev[1]).mean())
        if d > 0.8:   # a new distinct image
            best = None
            for s in range(0, 40):
                e = float(np.abs(prof[: len(prof) - s] - prev[1][s:]).mean())
                if best is None or e < best[0]:
                    best = (e, s)
            steps.append((n, n - prev[0], round(best[1] * 256 / 1200, 2), round(best[0], 2)))
            prev = (n, prof)
    else:
        prev = (n, prof)
for s in steps:
    print(*s)
