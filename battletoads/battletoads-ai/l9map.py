"""Plot a reachability trace (L4S_TRACE file) in world coordinates with the TAS's Terra Tubes trajectory overlaid.
    python l9map.py <trace file> <root H abs> <out png> [i_from i_to]"""
import re, sys
from PIL import Image, ImageDraw
trace, hroot, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
i0, i1 = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 2000)
taslog = sys.argv[6] if len(sys.argv) > 6 else "tas/watch_all_log.txt"      # or tas/watch_1p_log.txt
pts = []
for ln in open(trace):
    p = ln.split()
    if len(p) >= 4: pts.append((int(p[0]), int(p[1]), int(p[2]) + hroot, int(p[3])))
# TAS trajectory, placement-anchored (frame 12282 = placement, h 112)
rows = []
for ln in open(taslog):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=\d+ an=(\d+) hp=\d+", ln)
    if m and (taslog != "tas/watch_all_log.txt" or 12282 <= int(m.group(1)) <= 21378): rows.append((int(m.group(2)), int(m.group(3)), int(m.group(5))))
start = next(i for i, r in enumerate(rows) if r[0] == 40 and r[1] == 112)
H = 0; prev = 112; tas = []
for i, (x, h, an) in enumerate(rows[start:]):
    H += (h - prev + 128) % 256 - 128; prev = h
    if i0 <= i <= i1: tas.append((i, x, H))
xs = [p[1] for p in pts] + [t[1] for t in tas]; hs = [p[2] for p in pts] + [t[2] for t in tas]
x0, x1, h0, h1 = min(xs) - 20, max(xs) + 20, min(hs) - 20, max(hs) + 20
S = 2; W, Hh = (x1 - x0) * S, (h1 - h0) * S
im = Image.new("RGB", (W, Hh), (20, 20, 30)); d = ImageDraw.Draw(im)
def P(x, h): return ((x - x0) * S, (h1 - h) * S)            # up = larger H
for gx in range(x0 // 100 * 100, x1, 100):
    d.line([P(gx, h0), P(gx, h1)], fill=(50, 50, 60)); d.text((P(gx, h1)[0] + 2, 2), str(gx), fill=(120, 120, 140))
for gh in range(h0 // 100 * 100, h1, 100):
    d.line([P(x0, gh), P(x1, gh)], fill=(50, 50, 60)); d.text((2, P(x0, gh)[1] + 2), str(gh), fill=(120, 120, 140))
smax = max(p[0] for p in pts) or 1
for st, x, h, z in pts:
    c = int(255 * st / smax); d.point(P(x, h), fill=(255 - c, c, 80) if z else (255 - c, c, 255))
for i, x, h in tas:
    d.rectangle([P(x, h)[0] - 1, P(x, h)[1] - 1, P(x, h)[0] + 1, P(x, h)[1] + 1], fill=(255, 255, 0))
    if i % 100 == 0: d.text((P(x, h)[0] + 3, P(x, h)[1] - 10), f"i{i}", fill=(255, 255, 0))
im.save(out); print(out, im.size, len(pts), "trace points", len(tas), "tas points")
