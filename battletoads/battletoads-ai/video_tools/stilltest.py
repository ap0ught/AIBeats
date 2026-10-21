import sys
from fx import *
cap = Cap("cap14")
S = sys.argv[1]
fr = [int(x) for x in sys.argv[2:]]
tiles = []
for f in fr:
    nes = next(nes_frames(VIDEO / "up14.mkv", 6 + f, 1))
    im = nes.resize((768, 672), Image.NEAREST); d = ImageDraw.Draw(im)
    for box, o in objects_on_screen(cap, f):
        b = [v * 3 for v in box[:4]]
        if o and o["slot"] == 0:
            brackets(d, b, TOAD, 4); chip(d, b[0], b[1] - 4, "TOAD", TOAD, 18)
        elif o and obj_name(cap, f, o):
            brackets(d, b, RED, 4); chip(d, b[0], b[1] - 4, f"{obj_name(cap, f, o)} hp{o['hp']}", RED, 18, fg=WHITE)
        else:
            d.rectangle(b, outline=(90, 90, 90))
            if o: d.text((b[0], b[3] + 2), f"{o['id']:02x}", fill=(200, 200, 200))
    d.text((6, 6), str(f), fill=WHITE)
    tiles.append(im)
sheet = Image.new("RGB", (768 * 3, 672 * ((len(tiles) + 2) // 3)))
for i, t in enumerate(tiles): sheet.paste(t, ((i % 3) * 768, (i // 3) * 672))
sheet.resize((sheet.width // 2, sheet.height // 2)).save(S)
