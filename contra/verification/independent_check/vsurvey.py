"""Survey sheets: every Nth frame of runA from START to END, downscaled, 6x6 per sheet. python vsurvey.py step"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
HERE = Path(__file__).resolve().parent
step = int(sys.argv[1]) if len(sys.argv) > 1 else 120
frames = list(range(594, 34510, step))
W, H = 160, 140 + 10
(HERE / "sheets").mkdir(exist_ok=True)
for s in range(0, len(frames), 36):
    sheet = Image.new("RGB", (6 * W, 6 * H), (0, 0, 0))
    for i, f in enumerate(frames[s:s + 36]):
        im = Image.open(HERE / "runA" / f"f{f:05d}.png").convert("RGB").resize((160, 140), Image.BILINEAR)
        t = Image.new("RGB", (W, H), (40, 40, 40)); t.paste(im, (0, 10))
        ImageDraw.Draw(t).text((2, 0), str(f), fill=(255, 255, 0))
        sheet.paste(t, ((i % 6) * W, (i // 6) * H))
    sheet.save(HERE / "sheets" / f"survey_{s // 36:02d}.png")
print(len(frames))
