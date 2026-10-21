"""Verifier's contact sheets from logs/fix/u16v_shots (labels drawn above each picture)."""
import re
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SH = HERE / "logs" / "fix" / "u16v_shots"
OUT = HERE / "logs" / "fix"


def sheet(name, items, cols=4, scale=2):
    """items = [(label, path)]"""
    items = [(l, p) for l, p in items if p.exists()]
    if not items:
        print("no pictures for", name)
        return
    w, h = 256 * scale, 224 * scale
    rows = (len(items) + cols - 1) // cols
    im = Image.new("RGB", (cols * (w + 6) + 6, rows * (h + 22) + 6), (40, 40, 40))
    d = ImageDraw.Draw(im)
    for i, (label, p) in enumerate(items):
        x = 6 + (i % cols) * (w + 6)
        y = 6 + (i // cols) * (h + 22)
        d.text((x + 2, y + 2), label, fill=(255, 255, 0))
        pic = Image.open(p).convert("RGB").resize((w, h), Image.NEAREST)
        im.paste(pic, (x, y + 16))
    o = OUT / f"u16v_sheet_{name}.png"
    im.save(o)
    print(o, im.size, len(items))


tag = sys.argv[1] if len(sys.argv) > 1 else "run2"
# 1 landing
sheet("landing", [(f"frame {f}", SH / f"{tag}_land_f{f:05d}.png") for f in range(2066, 2082)], cols=4)
# 2 levels: for every change into a real level, +150/+250/+400/+600
lv = {}
for p in sorted(SH.glob(f"{tag}_lv_f*_p*.png")):
    m = re.match(rf"{tag}_lv_f(\d+)_(\d+)to(\d+)_p(\d+)\.png", p.name)
    f, a, b, k = int(m[1]), int(m[2]), int(m[3]), int(m[4])
    lv.setdefault((f, a, b), {})[k] = p
items = []
for (f, a, b), d in sorted(lv.items()):
    if b not in (0, 254, 255):
        for k in (150, 250, 400, 600):
            if k in d:
                items.append((f"level byte {a}->{b} at {f}, +{k}", d[k]))
sheet("levels", items, cols=4)
# the cards between the levels: +5 after each change to 254/255
items = []
for (f, a, b), d in sorted(lv.items()):
    if b in (254, 255) and f > 2000:
        for k in (5,):
            if k in d:
                items.append((f"{a}->{b} at {f}, +{k}", d[k]))
sheet("cards", items, cols=6, scale=1)
# 3 last hit
items = [(f"last hit 44344 +{int(p.stem.split('_p')[1])}", p) for p in sorted(SH.glob(f"{tag}_lasthit_*"))]
sheet("lasthit", items, cols=4)
# 4 first cut, the route's own inputs
c1 = sorted(SH.glob(f"{tag}_cut1_f*_p*.png"))
sheet("cut1_route", [(f"cut1 {p.stem.split('_')[2][1:]} +{int(p.stem.split('_p')[1])} (route inputs)", p) for p in c1 if int(p.stem.split('_p')[1]) in (0, 1, 2, 5, 8, 9, 10, 11, 12, 13, 14, 16, 20, 25, 30, 40)], cols=4)
c1n = sorted(SH.glob(f"{tag}_cut1noinput_f*_p*.png"))
sheet("cut1_noinput", [(f"cut1 +{int(p.stem.split('_p')[1])} (NO input after the cut)", p) for p in c1n], cols=4)
# 5 second cut
c2 = sorted(SH.glob(f"{tag}_cut2_f*_p*.png"))
sheet("cut2_tbird", [(f"cut2 {p.stem.split('_')[2][1:]} +{int(p.stem.split('_p')[1])}", p) for p in c2 if int(p.stem.split('_p')[1]) in (0, 1, 2, 5, 8, 9, 10, 11, 12, 13, 15, 20, 25, 30, 35, 40)], cols=4)
