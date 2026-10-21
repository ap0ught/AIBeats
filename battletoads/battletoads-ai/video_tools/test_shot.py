"""Test: the Hornhead big boot (up14 frames ~41300-41560) with a following camera, target brackets, a slow-mo on
the boot and a title slam at the start."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from fx import *

cap = Cap("cap14")
LEAD = 6
A, B = 41300, 41560
src = VIDEO / "up14.mkv"
w = Writer(OUT / "test_shot.mp4")
cam = Camera(scale=5.0, follow=0.10)
trail = []
frames = list(nes_frames(src, LEAD + A, B - A))
for i, nes in enumerate(frames):
    f = A + i
    tb = toad_box(cap, f)
    if tb:
        tx, ty = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
        cam.toward(tx, ty)
        trail.append((tx, ty))
    reps = 3 if 41380 <= f <= 41420 else 1          # slow motion on the boot
    for r in range(reps):
        im = cam.render(nes)
        im = scanlines(im, 0.12)
        d = ImageDraw.Draw(im)
        for j, (px, py) in enumerate(trail[-24:]):
            ox, oy = cam.to_out(px, py)
            a = j / 24
            rad = 4 + 6 * a
            d.ellipse((ox - rad, oy - rad, ox + rad, oy + rad), fill=tuple(int(c * a) for c in TOAD))
        for box, o in objects_on_screen(cap, f):
            x0, y0 = cam.to_out(box[0], box[1]); x1, y1 = cam.to_out(box[2], box[3])
            if o and o["slot"] == 0:
                brackets(d, (x0, y0, x1, y1), TOAD, 5)
                chip(d, x0, y0 - 6, "TOAD", TOAD)
            elif o:
                name = NAMES.get(cap.r(f, 0x10), {}).get(o["id"] & 0x7F, f"OBJ {o['id']:02X}")
                brackets(d, (x0, y0, x1, y1), RED, 5)
                cx0, cy0, cx1, cy1 = chip(d, x0, y0 - 6, f"{name}  HP {o['hp']}", RED, fg=WHITE)
                if tb:
                    tx0, ty0 = cam.to_out((tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2)
                    dashed(d, (tx0, ty0), ((x0 + x1) / 2, (y0 + y1) / 2), GOLD, 3)
                    dist = abs((o["x"]) - cap.obj(f, 0)["x"])
                    chip(d, (tx0 + (x0 + x1) / 2) / 2, (ty0 + (y0 + y1) / 2) / 2, f"{dist} px", GOLD, 22, anchor="mt")
        if reps > 1:
            chip(d, 60, 1020, "SLOW MOTION  x1/3", WHITE, 28)
        chip(d, 1860, 60, f"FRAME {f}", (20, 20, 20), 22, fg=TEXT, anchor="mt")
        t = w.n / NES_FPS
        if t < 1.6:
            im = slam(darken(im, 0.55) if t < 1.6 else im, "THE BIG BOOT", t, 1.6, sub="kick, walk away, turn back")
        w.put(vignette(im, 0.35))
w.close()
print("frames", w.n)
