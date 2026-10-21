"""Summarise a stage 7 trace made by tools/s7_trace.py.

    python tools/s7_trace_view.py <name> [step_px]

Prints: row at which the camera first reaches every step_px, the loss against 1 px/frame, lag frames and pauses
per interval, stalls (camera not moving for >= 4 rows) and fast stretches.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
name = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 128
tr = json.loads((ROOT / "logs" / "s7" / f"{name}.trace.json").read_text())
# [cam, x, y, fc, lagged, pause, barrier, nbullets, nenemies, stop, auto, weapon, bossdef, lroutine]
first = {}
for i, r in enumerate(tr):
    if r[13] != 4:
        continue
    c = r[0]
    for m in range(0, c + 1, step):
        if m not in first:
            first[m] = i
prev = None
print("cam   row   loss(row-cam)  d_loss  lag  pause  wx  y")
for m in sorted(first):
    i = first[m]
    lo = prev[1] if prev else 0
    lag = sum(r[4] for r in tr[lo:i])
    pz = sum(1 for r in tr[lo:i] if r[5])
    loss = i - m
    print(f"{m:5d} {i:5d} {loss:5d} {loss - (prev[2] if prev else 0):5d} {lag:4d} {pz:4d}   {tr[i][0] + tr[i][1]:5d} {tr[i][2]:4d}")
    prev = (m, i, loss)
# stalls
print("stalls (cam unchanged >= 4 rows): start row, len, cam, x range, y, lag, pause")
i = 0
n = len(tr)
while i < n:
    j = i
    while j + 1 < n and tr[j + 1][0] == tr[i][0]:
        j += 1
    if j - i >= 4 and tr[i][13] == 4:
        seg = tr[i:j + 1]
        print(f"  row {i:5d} len {j - i + 1:4d} cam {tr[i][0]:5d} x {seg[0][1]}..{seg[-1][1]} y {seg[0][2]}..{seg[-1][2]} "
              f"lag {sum(r[4] for r in seg)} pause {sum(1 for r in seg if r[5])} fc {seg[0][3]}")
    i = j + 1
print("total lag", sum(r[4] for r in tr), "pause rows", sum(1 for r in tr if r[5]))
lagrows = [i for i, r in enumerate(tr) if r[4]]
print("lag rows:", lagrows)
