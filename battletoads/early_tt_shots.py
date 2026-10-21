"""EARLY track (2026-10-09): screenshots of what hurts the toad right of the Terra Tubes staircase top (see early_tt_run3.py).
    python early_tt_shots.py   -> logs/fix/tt_hurt.jpg"""
from PIL import Image, ImageDraw
from early_tt_run3 import *   # noqa

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
e = BizHawk(log_name="early_tt_shots.log", fields=F)
e.load("cap14_f25000")
for i in range(25000, ROOT):
    s = e.step(bt(lines[i]), 1)
root = e.msave()
cells = []


def shot(label):
    p = e.screenshot("early_shots/tt")
    cells.append((label, Image.open(p).convert("RGB").resize((512, 448))))


for x0, k, mid, end, cut, label in ((860, 60, "", "", 2, "drop at x0 860"), (900, 60, "", "", 2, "drop at x0 900")):
    ins, t, res = flight(e, root, s, x0, k, mid, end)
    e.mload(root)
    for b in ins[:-cut]:
        t = e.step(bt(b), 1)
    shot(f"{label}: {cut} f before {res} toad {t.x | t.xh << 8},{t.height | t.hh << 8}")
    t = e.step(bt(ins[-cut]), 1); t = e.step(bt(ins[-1]), 1)
    shot(f"{label}: at {res}")
ins, t, res = flight(e, root, s, 888, 12, "Left", "", stop_on_land=True)
shot(f"ledge landing {res} cam {t.camx | t.camxh << 8}")
for d in ("Right", "Left"):
    e.mload(root)
    for b in ins:
        e.step(bt(b), 1)
    last = None
    for j in range(80):
        t = e.step((d,), 1)
        if t.hp < 47:
            shot(f"ledge, walk {d}: hurt at +{j + 1} toad {t.x | t.xh << 8},{t.height | t.hh << 8} anim {t.anim}")
            break
        if j % 8 == 7:
            last = j
    else:
        shot(f"ledge, walk {d}: no hurt in 80")
e.close()
sheet = Image.new("RGB", (512 * 3, 448 * ((len(cells) + 2) // 3)))
d = ImageDraw.Draw(sheet)
for k, (label, im) in enumerate(cells):
    x, y = (k % 3) * 512, (k // 3) * 448
    sheet.paste(im, (x, y))
    d.rectangle([x, y, x + 511, y + 12], fill=(0, 0, 0))
    d.text((x + 2, y), label, fill=(255, 255, 0))
sheet.save(LOGS_DIR / "fix" / "tt_hurt.jpg", quality=70)
print("saved", [c[0] for c in cells])
