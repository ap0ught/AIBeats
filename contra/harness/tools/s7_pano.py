"""Panorama of stage 7 from the screenshots of tools/s7_trace.py (shots/s7cmp/<name>_cam*_row*.png).

    python tools/s7_pano.py <name>

Writes shots/s7cmp/<name>_pano.png (full) and <name>_pano_<k>.png (1024-px-wide pieces with a world-x ruler).
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
name = sys.argv[1]
d = ROOT / "shots" / "s7cmp"
shots = []
for p in sorted(d.glob(f"{name}_cam*_row*.png")):
    m = re.search(r"_cam(\d+)_row(\d+)", p.name)
    shots.append((int(m.group(1)), int(m.group(2)), p))
W = max(c for c, _, _ in shots) + 256
pano = Image.new("RGB", (W, 240))
for c, r, p in reversed(shots):          # earlier shots on top for their left part
    im = Image.open(p).convert("RGB")
    if im.size != (256, 240):
        im = im.resize((256, 240), Image.NEAREST)
    pano.paste(im, (c, 0))
pano.save(d / f"{name}_pano.png")
k = 0
for x0 in range(0, W, 960):
    piece = pano.crop((x0, 0, min(W, x0 + 1024), 240)).resize((min(W, x0 + 1024) - x0, 240))
    canvas = Image.new("RGB", (1024, 262), (0, 0, 0))
    canvas.paste(piece, (0, 22))
    dr = ImageDraw.Draw(canvas)
    for x in range((x0 + 63) // 64 * 64, x0 + 1024, 64):
        dr.line([(x - x0, 14), (x - x0, 22)], fill=(255, 255, 0))
        dr.text((x - x0 + 2, 2), str(x), fill=(255, 255, 0))
    canvas = canvas.resize((2048, 524), Image.NEAREST)
    canvas.save(d / f"{name}_pano_{k}.png")
    k += 1
print("pieces", k, "width", W)
