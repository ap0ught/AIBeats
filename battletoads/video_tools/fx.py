"""The production layer: game footage framed at 1080p with a following camera, target brackets drawn from the real
sprite table, motion trails, slow motion, freeze-frames, title slams, screen shake and flashes.

Coordinates: NES pixels (256x224) unless a name ends in _o (output pixels)."""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from style import *  # noqa: F401,F403
from ramview import Cap

# ---------------------------------------------------------------- object names per level byte (ids from the RAM capture)
NAMES = {
    1: {0x20: "PSYKO-PIG"},
    3: {0x47: "RAT", 0x7f: "LEVEL END"},
    8: {0x4f: "EXIT HOLE"},
    7: {0x7d: "ROBO-MANUS"},
    9: {0x46: "RAT", 0x5a: "BOMB"},
    10: {0x7a: "BUZZBALL", 0x7b: "BUZZBALL"},
    5: {0x5c: "HORNHEAD", 0x62: "WALKER", 0x60: "WIND FACE", 0x5f: "POLE", 0x36: "SPRING", 0x34: "LIFT", 0x5d: "PLATFORM",
        0x7f: "LEVEL END"},
    13: {0x7e: "DARK QUEEN"},
}


def obj_name(cap, f, o):
    return NAMES.get(cap.r(f, 0x10), {}).get(o["id"] & 0x7F)


# ---------------------------------------------------------------- sprites -> objects
def _box(sp):
    return [min(s[0] for s in sp), min(s[1] for s in sp), max(s[0] for s in sp) + 8, max(s[1] for s in sp) + 8, len(sp)]


def objects_on_screen(cap: Cap, f):
    """[(box, obj or None)] for frame f. The toad is every sprite with a tile below 0x20 (its graphics are streamed
    into tiles 1..31); the rest are split into runs of consecutive OAM entries with the same palette and nearby tiles,
    and runs that touch are merged. Clusters are matched to RAM objects by x, using the toad's own RAM-x -> screen-x
    offset (that also works on the rotating tower, where the camera x means nothing)."""
    o = cap.oam[f]
    sp = [(int(o[i + 3]), int(o[i]) + 1 - 8, int(o[i + 1]), int(o[i + 2]) & 3) for i in range(4, 256, 4) if o[i] < 239]   # the capture starts at scanline 8
    toad = [s for s in sp if 1 <= s[2] < 0x20]
    rest = [s for s in sp if not (1 <= s[2] < 0x20)]
    runs = []
    for s in rest:
        if runs and runs[-1][-1][3] == s[3] and abs(runs[-1][-1][2] - s[2]) <= 4:
            runs[-1].append(s)
        else:
            runs.append([s])
    boxes = [_box(r) for r in runs]
    merged = True
    while merged:
        merged = False
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                if a[0] <= b[2] + 1 and b[0] <= a[2] + 1 and a[1] <= b[3] + 1 and b[1] <= a[3] + 1:
                    boxes[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]), a[4] + b[4]]
                    del boxes[j]; merged = True; break
            if merged:
                break
    res = []
    t0 = cap.obj(f, 0)
    off = None
    if len(toad) >= 3:
        tb = _box(toad)
        off = t0["x"] - (tb[0] + tb[2]) / 2
        t0["sx"] = (tb[0] + tb[2]) / 2
        res.append((tuple(tb), t0))
    objs = []
    for s in range(2, 15):
        ob = cap.obj(f, s)
        if ob["id"] and ob["id"] not in (0x04, 0x0c, 0x22, 0x30, 0x41, 0x42, 0x44):
            objs.append(ob)
    for b in boxes:
        if b[4] < 2:
            continue
        mx = (b[0] + b[2]) / 2
        best = None
        if off is not None and objs:
            best = min(objs, key=lambda ob: abs(ob["x"] - off - mx))
            if abs(best["x"] - off - mx) > 32:
                best = None
        res.append((tuple(b), best))
    return res


def toad_box(cap: Cap, f):
    for b, o in objects_on_screen(cap, f):
        if o and o["slot"] == 0:
            return b
    return None


# ---------------------------------------------------------------- framing
class Camera:
    """an 8x (or any scale) window onto the NES frame that eases toward a target point"""

    def __init__(self, scale=8.0, cx=128, cy=112, follow=0.12):
        self.scale, self.cx, self.cy, self.follow = scale, cx, cy, follow

    def view(self):
        vw, vh = W / self.scale, H / self.scale
        x0 = min(max(self.cx - vw / 2, 0), 256 - vw) if vw < 256 else (256 - vw) / 2
        y0 = min(max(self.cy - vh / 2, 0), 224 - vh) if vh < 224 else (224 - vh) / 2
        return x0, y0

    def toward(self, tx, ty, scale=None):
        self.cx += (tx - self.cx) * self.follow
        self.cy += (ty - self.cy) * self.follow
        if scale:
            self.scale += (scale - self.scale) * self.follow

    def to_out(self, x, y):
        x0, y0 = self.view()
        return (x - x0) * self.scale, (y - y0) * self.scale

    def render(self, nes: Image.Image, bg=None):
        """the NES frame through this camera, nearest-neighbour, filling 1920x1080"""
        x0, y0 = self.view()
        s = self.scale
        if W / s >= 256:      # frame narrower than the screen: on a blurred copy, placed exactly where view() says
            gw, gh = int(256 * s), int(224 * s)
            out = bg.copy() if bg is not None else backdrop(nes)
            out.paste(nes.resize((gw, gh), Image.NEAREST), (int(round(-x0 * s)), int(round(-y0 * s))))
            return out
        # crop a little extra, scale with nearest, then crop exactly
        ix0, iy0 = int(math.floor(x0)), int(math.floor(y0))
        ix1, iy1 = min(256, int(math.ceil(x0 + W / s)) + 1), min(224, int(math.ceil(y0 + H / s)) + 1)
        crop = nes.crop((ix0, iy0, ix1, iy1))
        big = crop.resize((int((ix1 - ix0) * s), int((iy1 - iy0) * s)), Image.NEAREST)
        ox, oy = int((x0 - ix0) * s), int((y0 - iy0) * s)
        out = big.crop((ox, oy, ox + W, oy + H))
        if out.size != (W, H):
            o2 = Image.new("RGB", (W, H), BG); o2.paste(out, (0, 0)); out = o2
        return out


def backdrop(nes):
    """blurred, darkened full-bleed copy of the frame for letterboxed shots"""
    b = nes.resize((W // 8, int(W // 8 * 224 / 256)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    b = b.resize((W, int(W * 224 / 256)), Image.BILINEAR)
    b = ImageEnhance.Brightness(b).enhance(0.35)
    top = (b.height - H) // 2
    return b.crop((0, top, W, top + H))


def fit_frame(nes, scale=4.5):
    """whole NES frame centred at `scale` on the blurred backdrop"""
    return Camera(scale).render(nes)


# ---------------------------------------------------------------- overlays
def chip(d, x, y, text, col=GOLD, size=26, fg=(10, 10, 10), anchor="lb"):
    f = mono(size, True)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    w, h = r - l + 16, b - t + 10
    if anchor == "lb":
        x0, y0 = x, y - h
    elif anchor == "lt":
        x0, y0 = x, y
    elif anchor == "mb":
        x0, y0 = x - w / 2, y - h
    else:
        x0, y0 = x - w / 2, y
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=col)
    d.text((x0 + 8 - l, y0 + 5 - t), text, font=f, fill=fg)
    return x0, y0, x0 + w, y0 + h


def brackets(d, box_o, col=GOLD, width=5, k=0.28, grow=0.0):
    x0, y0, x1, y1 = box_o
    g = grow
    x0, y0, x1, y1 = x0 - g, y0 - g, x1 + g, y1 + g
    lx, ly = (x1 - x0) * k, (y1 - y0) * k
    for (ax, ay, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line((ax, ay, ax + sx * lx, ay), fill=col, width=width)
        d.line((ax, ay, ax, ay + sy * ly), fill=col, width=width)


def bar(d, x, y, w, h, frac, col, bg=(30, 30, 30)):
    d.rectangle((x, y, x + w, y + h), fill=bg, outline=(0, 0, 0), width=2)
    d.rectangle((x + 2, y + 2, x + 2 + (w - 4) * max(0, min(1, frac)), y + h - 2), fill=col)


def dashed(d, p0, p1, col, width=4, dash=18, gap=10):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    t = 0
    while t < L:
        e = min(L, t + dash)
        d.line((x0 + ux * t, y0 + uy * t, x0 + ux * e, y0 + uy * e), fill=col, width=width)
        t += dash + gap


def scanlines(im, alpha=0.10):
    """faint CRT scanlines over game footage"""
    global _SCAN
    try:
        sl = _SCAN
    except NameError:
        sl = Image.new("L", (W, H), 0)
        dd = ImageDraw.Draw(sl)
        for y in range(0, H, 4):
            dd.line((0, y, W, y), fill=255)
        _SCAN = sl
    dark = ImageEnhance.Brightness(im).enhance(1 - alpha)
    return Image.composite(dark, im, _SCAN)


def vignette(im, strength=0.45):
    global _VIG
    try:
        v = _VIG
    except NameError:
        v = Image.radial_gradient("L").resize((W, H)).point(lambda p: int(255 * min(1, (p / 255) ** 2.2 * 1.6)))
        _VIG = v
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(black, im, v.point(lambda p: int(p * strength)))


def shake(im, t, amp=24, seed=0):
    """screen shake that decays over t in [0,1]"""
    if t >= 1:
        return im
    r = random.Random(int(t * 1000) + seed)
    a = amp * (1 - t) ** 2
    dx, dy = int(r.uniform(-a, a)), int(r.uniform(-a, a))
    out = Image.new("RGB", (W, H), (0, 0, 0))
    out.paste(im, (dx, dy))
    return out


def flash(im, t, col=(255, 255, 255)):
    """white flash that fades over t in [0,1]"""
    if t >= 1:
        return im
    return Image.blend(im, Image.new("RGB", (W, H), col), max(0.0, 0.85 * (1 - t) ** 2))


# ---------------------------------------------------------------- title slam
_LOGO_CACHE = {}


def logo(text, size=150, **kw):
    key = (text, size, tuple(sorted(kw.items())))
    if key not in _LOGO_CACHE:
        _LOGO_CACHE[key] = logo_text(text, size, face=kw.pop("face", "ROCKEB.TTF"), **kw)
    return _LOGO_CACHE[key]


def slam(im, text, t, dur, sub=None, size=150, y=None, colors=None, out_t=0.25):
    """composite a slammed title onto `im` at time t (s) of a slam lasting `dur` s:
    0-0.18 s zooms in from 3x and lands with a shake + flash, then holds, then whips out to the left."""
    kw = {} if not colors else dict(top=colors[0], bottom=colors[1], extrude=colors[2])
    lg = logo(text, size, **kw)
    land = 0.18
    yc = y if y is not None else H // 2 - (40 if sub else 0)
    if t < land:
        k = t / land
        sc = 3.0 - 2.0 * ease(k)
        al = min(1.0, k * 2)
    else:
        sc, al = 1.0, 1.0
    xoff = 0
    if t > dur - out_t:
        k = (t - (dur - out_t)) / out_t
        xoff = -int((W + lg.width) * ease(k) ** 1.6)
    g = lg if abs(sc - 1) < 1e-3 else lg.resize((max(1, int(lg.width * sc)), max(1, int(lg.height * sc))), Image.BILINEAR)
    if al < 1:
        a = g.split()[3].point(lambda p: int(p * al)); g = g.copy(); g.putalpha(a)
    base = im
    if t >= land:
        base = shake(im, (t - land) / 0.35, amp=26)
    base = base.copy()
    base.paste(g, (int(W / 2 - g.width / 2 + xoff), int(yc - g.height / 2)), g)
    if sub and t >= land:
        k = min(1, (t - land) / 0.25)
        d = ImageDraw.Draw(base)
        f = font("arialbd.ttf", 44)
        l, tt, r, b = d.textbbox((0, 0), sub, font=f)
        sx = W / 2 - (r - l) / 2 + xoff
        sy = yc + lg.height / 2 + 18 + (1 - ease(k)) * 30
        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3), (3, 3)):
            d.text((sx + ox, sy + oy), sub, font=f, fill=(0, 0, 0))
        d.text((sx, sy), sub, font=f, fill=WHITE)
    if land <= t < land + 0.12:
        base = flash(base, (t - land) / 0.12)
    return base


def darken(im, k=0.45):
    return ImageEnhance.Brightness(im).enhance(k)
