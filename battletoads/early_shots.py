"""EARLY track (2026-10-09): contact sheet of up14 itself, to lay beside the record's video sheets.
    python early_shots.py <first frame> <last frame> <step> <name> [cols=4]   -> logs/fix/<name>.jpg
Each cell is labelled with the up14 frame and the run clock (frame - 2074) / 60.0988."""
import sys
from PIL import Image, ImageDraw
from toads.emulator import BizHawk, LOGS_DIR, SHOTS_DIR

a, b, step, name = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 4
lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name="early_shots.log")
base = (a // 1000) * 1000
e.load(f"cap14_f{base}")
frames = list(range(a, b + 1, step))
cells = []
for i in range(base, b):
    e.step(bt(lines[i]), 1)
    if i + 1 in frames:
        p = e.screenshot("early_shots/tmp")
        cells.append((i + 1, Image.open(p).convert("RGB").resize((256, 224))))
e.close()
rows = (len(cells) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 256, rows * 224))
d = ImageDraw.Draw(sheet)
for k, (f, im) in enumerate(cells):
    x, y = (k % cols) * 256, (k // cols) * 224
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + 110, y + 11], fill=(0, 0, 0))
    d.text((x + 2, y), f"{f}  {(f - 2074) / 60.0988:.2f}s", fill=(255, 255, 0))
out = LOGS_DIR / "fix" / f"{name}.jpg"
sheet.save(out, quality=60)
print(out)
