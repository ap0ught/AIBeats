"""crop tiles: python work/a34r2/crop.py <seg> <a> <b> <step> <x0> <y0> <x1> <y1> <scale> <cols> <out>"""
import sys
from PIL import Image, ImageDraw
seg, a, b, st = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
x0, y0, x1, y1 = map(int, sys.argv[5:9]); sc = float(sys.argv[9]); cols = int(sys.argv[10]); out = sys.argv[11]
fs = list(range(a, b, st)); tw, th = int((x1 - x0) * sc), int((y1 - y0) * sc) + 12
sh = Image.new("RGB", (cols * tw, ((len(fs) + cols - 1) // cols) * th), "white"); d = ImageDraw.Draw(sh)
for i, f in enumerate(fs):
    try:
        im = Image.open(f"states/tmp/a34r2_vid/{seg}/f{f:05d}.png").convert("RGB").crop((x0, y0, x1, y1)).resize((tw, th - 12), Image.NEAREST)
    except Exception:
        continue
    x, y = (i % cols) * tw, (i // cols) * th; sh.paste(im, (x, y + 12)); d.text((x + 2, y), str(f), fill="black")
sh.save(out)
