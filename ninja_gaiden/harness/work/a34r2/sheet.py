"""contact sheet: python work/a34r2/sheet.py <seg> <a> <b> <step> <out.png> [cols] [scale]"""
import sys
from PIL import Image, ImageDraw
seg, a, b, st, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 4
sc = float(sys.argv[7]) if len(sys.argv) > 7 else 0.75
fs = list(range(a, b, st))
tw, th = int(256 * sc), int(240 * sc) + 12
rows = (len(fs) + cols - 1) // cols
sh = Image.new("RGB", (cols * tw, rows * th), "white")
d = ImageDraw.Draw(sh)
for i, f in enumerate(fs):
    try:
        im = Image.open(f"states/tmp/a34r2_vid/{seg}/f{f:05d}.png").convert("RGB").resize((tw, th - 12))
    except Exception:
        continue
    x, y = (i % cols) * tw, (i // cols) * th
    sh.paste(im, (x, y + 12))
    d.text((x + 2, y), str(f), fill="black")
sh.save(out)
