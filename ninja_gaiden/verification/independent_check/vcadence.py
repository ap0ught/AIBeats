"""Cadence of distinct images in the record video, START..END (timing-only analysis of the record VOD).
A 60.0988 Hz NES shown as 30 images/s on a real-time 60.000 fps timeline must slip: about every 10.1 s an image is
held 1 or 3 video frames instead of 2 (~68 slips over the run). An NES-locked timeline would never slip.
Writes vid/cadence_diffs.json (mean abs diff of each frame vs the previous, game area at 160x120)."""
import json
import numpy as np
import vid

prev = None
diffs = {}
for n, a in vid.frames(1700, 43245, vid.GAME, 160):
    g = a.astype(np.int16)
    if prev is not None:
        diffs[n] = round(float(np.abs(g - prev).mean()), 3)
    prev = g
json.dump(diffs, open("vid/cadence_diffs.json", "w"))
print(len(diffs))
