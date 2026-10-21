"""Track END probe: on which frame is the picture black relative to the level-byte changes at the two cuts (up14)?
Screenshots of every frame around cut1 (46751), back (46762) and cut2 (47253) -> mean luminance per frame."""
from PIL import Image
from toads.emulator import BizHawk, LOGS_DIR, SHOTS_DIR

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name="end_black.log")
e.load("cap14_f46000")
f = 46000
out = []
while f < 47270:
    b = bt(lines[f]) if f < len(lines) else (("A",) if f + 1 == 46762 else ())
    e.step(b, 1)
    f += 1
    if 46745 <= f <= 46800 or 47245 <= f <= 47268:
        p = e.screenshot(f"end_black/f{f:06d}")
        im = Image.open(p).convert("L")
        lum = sum(im.getdata()) / (im.size[0] * im.size[1])
        out.append((f, e.byte(0x10), e.byte(0x0B), round(lum, 1)))
        print(*out[-1], flush=True)
(LOGS_DIR / "fix" / "end_black.tsv").write_text("frame\tlevel\tt0b\tlum\n" + "\n".join("\t".join(map(str, r)) for r in out) + "\n")
e.close()
