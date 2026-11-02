"""Contact sheet: python tools/contact.py <out.png> <png>... (labels each tile with its file stem)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

if __name__ == "__main__":
    out, files = sys.argv[1], sys.argv[2:]
    cols = 6
    w, h = 256, 240
    sc = 0.5
    tw, th = int(w * sc), int(h * sc) + 12
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), "white")
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((tw, th - 12))
        x, y = (i % cols) * tw, (i // cols) * th
        sheet.paste(im, (x, y + 12))
        d.text((x + 2, y), Path(f).stem, fill="black")
    sheet.save(out)
