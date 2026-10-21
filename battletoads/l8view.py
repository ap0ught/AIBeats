"""Replay a searched section and make a contact sheet: python l8view.py <bookmark> [every=30]"""
import json, sys
from PIL import Image, ImageDraw
from toads.emulator import BizHawk, PROJECT
bm = sys.argv[1]; every = int(sys.argv[2]) if len(sys.argv) > 2 else 30
jname = sys.argv[3] if len(sys.argv) > 3 else f"l4s_{bm}"                  # e.g. l4s_L9_s3_best
ins = json.loads((PROJECT / "knowledge" / f"{jname}.json").read_text())
e = BizHawk(log_name=f"l8view_{bm}.log"); e.load(bm); e.step((), 2)
H = 0; prev = None; shots = []
def rd():
    r = e.ram_all(); return r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x51A], r[0x89] + 256 * r[0x8A]
x, h, hp, camy = rd(); prev = h
for i, s in enumerate(ins):
    e.step(tuple(b for b in s.split("+") if b), 1)
    x, h, hp, camy = rd(); H += (h - prev + 128) % 256 - 128; prev = h
    if i % every == 0 or i == len(ins) - 1:
        p = f"l8v_{bm}_{i}"; e.screenshot(p); shots.append((p, i, x, H, hp, camy, s))
e.close()
ims = []
for p, i, x, Hh, hp, camy, s in shots:
    im = Image.open(PROJECT / "shots" / f"{p}.png").convert("RGB"); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 150, 10), fill=(0, 0, 0)); d.text((2, 0), f"f{i} x{x} H{Hh} hp{hp} {s}", fill=(255, 255, 0)); ims.append(im)
cols = 8; w, hh = ims[0].size; rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + 4), rows * (hh + 4)))
for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * (w + 4), (k // cols) * (hh + 4)))
sheet.save(PROJECT / "shots" / f"l8view_{bm}.png"); print("sheet", len(ims), "frames", len(ins))
