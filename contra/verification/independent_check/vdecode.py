"""Decode the compact crops returned by the in-page analysis of the record's video (verify1 browser session) into
PNGs for looking at. Format: "<W>x<H>:<palette, 3 hex digits per colour (12-bit RGB)>:<RLE: [count]symbol ...>"
symbols a-z A-Z = palette index. Input: a JSON file {name: string}. Output: video_crops/<name>.png (enlarged).
    python vdecode.py crops_start.json [scale_x scale_y]
"""
import json
import re
import sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SYM = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
src = json.loads((HERE / sys.argv[1]).read_text(encoding="utf-8"))
sx = int(sys.argv[2]) if len(sys.argv) > 2 else 4
sy = int(sys.argv[3]) if len(sys.argv) > 3 else 4
(HERE / "video_crops").mkdir(exist_ok=True)
for name, s in src.items():
    dim, pal, rle = s.split(":")
    W, H = (int(v) for v in dim.split("x"))
    cols = [tuple(int(pal[i + k], 16) * 17 for k in range(3)) for i in range(0, len(pal), 3)]
    px = []
    for cnt, ch in re.findall(r"(\d*)([a-zA-Z])", rle):
        px.extend([cols[SYM.index(ch)]] * (int(cnt) if cnt else 1))
    if len(px) != W * H:
        print(name, "LENGTH MISMATCH", len(px), W * H, "(transcription error?)")
        px = (px + [(255, 0, 255)] * (W * H))[:W * H]
    im = Image.new("RGB", (W, H))
    im.putdata(px)
    im = im.resize((W * sx, H * sy), Image.NEAREST)
    im.save(HERE / "video_crops" / f"{name}.png")
    print(name, W, H, "ok")
