"""Our run's clock from the rendered pictures only (runA/f#####.png, 256x224, NesHawk, top/bottom 8 lines clipped).

START: first frame whose picture contains a life medal (template = the medal as drawn in a later gameplay frame,
       searched at the HUD position; also a colour count that needs no template).
END:   first frame after the heart is destroyed on which Bill's sprite is the tall standing shape, having been the
       flat prone shape on the frame before, with Down (or Up) held in the input file on both frames.
Prints the evidence and writes vclock.out.json.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
RUN = HERE / "runA"
FPS = 60.0988


def img(f):
    return np.asarray(Image.open(RUN / f"f{f:05d}.png").convert("RGB")).astype(np.int16)


def inputs():
    rows = []
    for l in (HERE.parent / "chain2" / "run_chain2.inputs.txt").read_text(encoding="utf-8").split("\n")[:-1]:
        if l.startswith("#"):
            continue
        rows.append(frozenset(t for t in l.rstrip("\r").split("+") if t))
    return rows


ROWS = inputs()
held = lambda f: ROWS[f - 2] if 0 <= f - 2 < len(ROWS) else frozenset()   # row i -> frame i + 2
out = {}

# ---------------------------------------------------------------- START
# template: the HUD strip of a gameplay frame well inside stage 1 where the sky behind the medals is black
ref = img(700)
hud = ref[0:32, 0:64]
nonblack = (hud.sum(axis=2) > 60)
ys, xs = np.nonzero(nonblack)
print("HUD non-black bbox in frame 700 (x0,y0,x1,y1):", xs.min(), ys.min(), xs.max(), ys.max(), "pixels", nonblack.sum())
# the medal's blue ribbon colour = the most common non-black colour in rows 8..15 of the strip
cols, counts = np.unique(hud[nonblack].reshape(-1, 3), axis=0, return_counts=True)
print("HUD colours in frame 700:", [(tuple(int(v) for v in c), int(n)) for c, n in zip(cols, counts)])
blue = cols[np.argmax(cols[:, 2] - cols[:, 0] - cols[:, 1] // 2)]
print("ribbon blue:", tuple(int(v) for v in blue))
# first medal's bounding box: leftmost connected column group
isblue = (np.abs(hud - blue).sum(axis=2) == 0)
colhit = isblue.any(axis=0)
x0 = int(np.argmax(colhit))
x1 = x0
while x1 + 1 < 64 and colhit[x1 + 1]:
    x1 += 1
x0 -= 1; x1 += 1                      # the round part of the medal is one pixel wider than the ribbon on each side
rowhit = nonblack[:, x0:x1 + 1].any(axis=1)
y0 = int(np.argmax(rowhit))
y1 = int(len(rowhit) - 1 - np.argmax(rowhit[::-1]))
tmpl = hud[y0:y1 + 1, x0:x1 + 1].copy()
tmask = nonblack[y0:y1 + 1, x0:x1 + 1]
print("first medal template box:", (x0, y0, x1, y1), "non-black pixels", int(tmask.sum()))


def medal_metrics(f):
    a = img(f)
    strip = a[0:32, 0:64]
    nblue = int((np.abs(strip - blue).sum(axis=2) == 0).sum())
    win = a[y0:y1 + 1, x0:x1 + 1]
    match = int(((np.abs(win - tmpl).sum(axis=2) == 0) & tmask).sum())
    return nblue, match


first_blue = first_tmpl = None
series = {}
for f in range(2, 1200):
    nb, m = medal_metrics(f)
    series[f] = (nb, m)
    if first_blue is None and nb > 0:
        first_blue = f
    if first_tmpl is None and m == int(tmask.sum()):
        first_tmpl = f
print("first frame with any ribbon-blue pixel in the HUD strip:", first_blue)
print("first frame with the complete first-medal template:", first_tmpl)
print("metrics (blue pixels, template pixels matched) around it:", {f: series[f] for f in range(first_blue - 3, first_blue + 4)})
gaps = [f for f in range(first_tmpl, 1200) if series[f][1] != int(tmask.sum())]
print("frames in", first_tmpl, "..1199 without the full template:", gaps[:10], len(gaps))
START = first_tmpl
out["START_picture_frame"] = START
out["START_first_blue_pixel_frame"] = first_blue
out["START_buttons_held"] = sorted(held(START))

# ---------------------------------------------------------------- END
# Stage 8, final room. Bill's sprite is found by colour: his skin and his blue trousers do not occur in the room's
# background near the floor. Take the colours from a frame where he is known (by eye) to be prone, then box them.
def bill_box(f, x_lo=70, x_hi=150, y_lo=140, y_hi=189):
    a = img(f)[y_lo:y_hi, x_lo:x_hi]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    skin = (r > 200) & (g > 120) & (g < 215) & (b > 90) & (b < 200)          # light flesh
    trou = (b > 180) & (r < 120) & (g < 140)                                   # blue trousers
    m = skin | trou
    if m.sum() < 12:
        return None
    ys, xs = np.nonzero(m)
    return (int(xs.min()) + x_lo, int(ys.min()) + y_lo, int(xs.max()) + x_lo, int(ys.max()) + y_lo, int(m.sum()),
            int(skin.sum()), int(trou.sum()))


rowsout = []
for f in range(34250, 34700):
    bb = bill_box(f)
    h = held(f)
    w = (bb[2] - bb[0] + 1, bb[3] - bb[1] + 1) if bb else None
    rowsout.append((f, bb, w, "+".join(sorted(h))))
# print run-length compressed
prev = None
print("frame  box(x0,y0,x1,y1,npix,skin,blue)  (w,h)  buttons")
for i, (f, bb, w, h) in enumerate(rowsout):
    key = (bb, h)
    if key != prev or i == len(rowsout) - 1:
        print(f, bb, w, h)
    prev = key


def pose(f):
    bb = bill_box(f)
    if not bb:
        return "none"
    w, h = bb[2] - bb[0] + 1, bb[3] - bb[1] + 1
    # the box is cut at the floor line (y = 188): standing Bill is about 30 rows tall above it, prone about 15
    if h >= 27 and w <= 28:
        return "stand"
    if h <= 17 and w >= 26:
        return "prone"
    return f"other({w}x{h})"


poses = {f: pose(f) for f in range(34250, 34700)}
# heart destroyed: the room palette changes and explosions start; found below from the picture as the first frame
# where the heart region differs strongly from the frame before the kill. Here: END = first prone -> stand change
# with Down/Up held on both frames.
END = None
for f in range(34400, 34700):
    if poses[f] == "stand" and poses[f - 1] == "prone" and (held(f) & {"Up", "Down"}) and (held(f - 1) & {"Up", "Down"}):
        END = f
        break
print("pose run lengths:")
prevp = None
for f in range(34250, 34700):
    if poses[f] != prevp:
        print(" ", f, poses[f], "| held:", "+".join(sorted(held(f))))
        prevp = poses[f]
print("END picture frame:", END, "held on END-1:", sorted(held(END - 1)), "held on END:", sorted(held(END)))
out["END_picture_frame"] = END
out["END_buttons_prev_frame"] = sorted(held(END - 1))
out["END_buttons"] = sorted(held(END))
out["END_box_prev"] = bill_box(END - 1)
out["END_box"] = bill_box(END)
# Down held continuously from which frame?
f = END
while (held(f - 1) & {"Down"}):
    f -= 1
out["down_held_from_frame"] = f
g = END
while (held(g + 1) & {"Down"}):
    g += 1
out["down_held_to_frame"] = g
print("Down held continuously on frames", f, "..", g)
span = END - START
out["span_frames"] = span
out["span_seconds_at_60.0988"] = span / FPS
m, s = divmod(span / FPS, 60)
out["span_text"] = f"{int(m)}:{s:06.3f}"
print("START", START, "END", END, "span", span, "frames =", span / FPS, "s =", out["span_text"])
(HERE / "vclock.out.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
