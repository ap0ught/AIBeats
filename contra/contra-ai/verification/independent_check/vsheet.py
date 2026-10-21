"""Contact sheet of emulator frames for looking at. python vsheet.py <out.png> <first> <last> [step] [crop x0,y0,x1,y1] [scale] [cols]"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
out, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
step = int(sys.argv[4]) if len(sys.argv) > 4 else 1
crop = tuple(int(v) for v in sys.argv[5].split(",")) if len(sys.argv) > 5 and sys.argv[5] != "-" else None
scale = int(sys.argv[6]) if len(sys.argv) > 6 else 2
cols = int(sys.argv[7]) if len(sys.argv) > 7 else 4
run = sys.argv[8] if len(sys.argv) > 8 else "runA"
frames = list(range(a, b + 1, step))
tiles = []
for f in frames:
    im = Image.open(HERE / run / f"f{f:05d}.png").convert("RGB")
    if crop:
        im = im.crop(crop)
    im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    t = Image.new("RGB", (im.width + 4, im.height + 14), (40, 40, 40))
    t.paste(im, (2, 12))
    ImageDraw.Draw(t).text((2, 0), str(f), fill=(255, 255, 0))
    tiles.append(t)
w, h = tiles[0].size
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * w, (i // cols) * h))
(HERE / "sheets").mkdir(exist_ok=True)
sheet.save(HERE / "sheets" / out)
print(sheet.size)
