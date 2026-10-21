"""Animated data graphics for the Battletoads video (1920x1080 at the NES frame rate).

Each graphic is a function `name(out_path, dur=...)` that renders an mp4 through style.Writer and writes a sound-cue
list next to it (`<name>.sfx.json`: [{"t": seconds, "sfx": "slam"|"whoosh"|"blip"|"tick"|"riser"|"ding"}]).
`python charts.py [name ...]` renders them all (or the named ones) into yt/clips/.

Layout is drawn on a 1920x1080 canvas with content kept inside x 100..1820, y 90..990, because every frame then goes
through a slow camera push-in (up to ~2.5 %) that eats into the edges."""
from __future__ import annotations

import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from style import *  # noqa: F401,F403,E402
import fx  # noqa: E402

DEEP = (4, 7, 5)
RED_HI = (255, 96, 80)
TEAL = (40, 150, 130)


# ================================================================ small helpers
def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def prog(t, t0, d):
    return clamp((t - t0) / d) if d > 0 else float(t >= t0)


def eout(k):
    k = clamp(k)
    return 1 - (1 - k) ** 3


def eback(k, s=1.7):
    return ease_out_back(clamp(k), s)


def mix(c1, c2, k):
    k = clamp(k)
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * k)) for i in range(3))


def fade(c, a):
    """colour faded toward the background (for opaque drawing on the base layer)"""
    return mix(BG, c, a)


def glowc(c, a):
    """colour faded toward black (for drawing on the additive glow layer)"""
    return mix((0, 0, 0), c, a)


def tw(d, s, f):
    return d.textlength(s, font=f)


def label_font(size, bold=True):
    return mono(size, bold)


# ================================================================ background, HUD, glow, camera
_BG = {}


def background(t):
    """near-black green with a two-level grid, crosshair marks and a soft centre lift; drifts slowly"""
    if "img" not in _BG:
        S, m = 80, 80
        w, h = W + 2 * m, H + 2 * m
        im = Image.new("RGB", (w, h), BG)
        d = ImageDraw.Draw(im)
        minor = (13, 19, 15)
        for x in range(0, w, S // 2):
            d.line((x, 0, x, h), fill=GRID if x % S == 0 else minor)
        for y in range(0, h, S // 2):
            d.line((0, y, w, y), fill=GRID if y % S == 0 else minor)
        for x in range(0, w, S * 4):
            for y in range(0, h, S * 4):
                d.line((x - 8, y, x + 8, y), fill=(46, 64, 52), width=2)
                d.line((x, y - 8, x, y + 8), fill=(46, 64, 52), width=2)
        rad = Image.radial_gradient("L").resize((w, h), Image.BILINEAR)
        lift = ImageChops.add(im, Image.new("RGB", (w, h), (7, 17, 10)))
        im = Image.composite(im, lift, rad.point(lambda p: min(255, int(p * 1.3))))
        _BG["img"] = im
    im = _BG["img"]
    ox = int(80 - min(80, t * 6))
    oy = int(80 - min(80, t * 3))
    return im.crop((ox, oy, ox + W, oy + H))


def hud(d, t, tag):
    c = (38, 56, 44)
    L = 26
    for (x, y, sx, sy) in ((46, 46, 1, 1), (W - 46, 46, -1, 1), (46, H - 46, 1, -1), (W - 46, H - 46, -1, -1)):
        d.line((x, y, x + sx * L, y), fill=c, width=2)
        d.line((x, y, x, y + sy * L), fill=c, width=2)
    f = mono(17)
    d.text((84, H - 50), tag, font=f, fill=(58, 80, 64), anchor="ls")
    blink = (int(t * 2) % 2) == 0
    d.ellipse((W - 92 - 10, H - 50 - 12, W - 92, H - 50 - 2), fill=(170, 40, 34) if blink else (60, 24, 22))
    d.text((W - 110, H - 50), "CLAUDE // BATTLETOADS ANY% NCW", font=f, fill=(58, 80, 64), anchor="rs")


def add_glow(base, G, r=5, gain=1.25):
    sm = G.resize((W // 4, H // 4), Image.BOX).filter(ImageFilter.GaussianBlur(r))
    if gain != 1:
        sm = ImageEnhance.Brightness(sm).enhance(gain)
    up = sm.resize((W, H), Image.BILINEAR)
    sm2 = G.resize((W // 2, H // 2), Image.BOX).filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BILINEAR)
    out = ImageChops.add(base, up)
    out = ImageChops.add(out, ImageEnhance.Brightness(sm2).enhance(0.6))
    return ImageChops.lighter(out, G)


def add_at(base, spr, x, y):
    """additively blend an RGB sprite onto base at (x, y), clipped to the frame"""
    x, y = int(x), int(y)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + spr.width), min(H, y + spr.height)
    if x1 <= x0 or y1 <= y0:
        return
    reg = base.crop((x0, y0, x1, y1))
    s = spr.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    base.paste(ImageChops.add(reg, s), (x0, y0))


_GSPR = {}


def put_logo(base, lg, cx, cy, scale=1.0, alpha=1.0, glow=None, glow_k=0.8):
    """paste a logo (RGBA) centred at (cx, cy), with optional additive glow behind it"""
    if scale <= 0.02 or alpha <= 0.01:
        return None
    sw, sh = max(1, int(lg.width * scale)), max(1, int(lg.height * scale))
    g = lg if (sw, sh) == lg.size else lg.resize((sw, sh), Image.BILINEAR)
    if alpha < 1:
        g = g.copy()
        g.putalpha(g.getchannel("A").point(lambda p: int(p * alpha)))
    x, y = int(cx - sw / 2), int(cy - sh / 2)
    if glow:
        key = (id(lg), glow)
        if key not in _GSPR:
            pad = 48
            a = Image.new("L", (lg.width + 2 * pad, lg.height + 2 * pad), 0)
            a.paste(lg.getchannel("A"), (pad, pad))
            a = a.filter(ImageFilter.GaussianBlur(20))
            spr = ImageChops.multiply(Image.new("RGB", a.size, glow), Image.merge("RGB", (a, a, a)))
            _GSPR[key] = (spr, pad)
        spr, pad = _GSPR[key]
        k = glow_k * alpha
        s2 = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BILINEAR)
        if k != 1:
            s2 = ImageEnhance.Brightness(s2).enhance(k)
        add_at(base, s2, cx - s2.width / 2, cy - s2.height / 2)
    base.paste(g, (x, y), g)
    return (x, y, x + sw, y + sh)


def small_logo(text, size, colors=None):
    kw = dict(outline=max(4, size // 11), depth=max(5, size // 9))
    if colors:
        kw.update(top=colors[0], bottom=colors[1], extrude=colors[2])
    return fx.logo(text, size, **kw)


GREEN_LOGO = ((210, 255, 150), (70, 185, 35), (15, 60, 10))
WHITE_LOGO = ((255, 255, 255), (175, 205, 185), (30, 50, 38))
RED_LOGO = ((255, 170, 150), (225, 45, 35), (70, 10, 5))


class Post:
    """impacts drive a zoom punch, a camera shake and a flash; plus a slow push-in, drift and a vignette"""

    def __init__(self, dur, impacts=(), z=(1.0, 1.022)):
        self.dur, self.impacts, self.z = dur, list(impacts), z

    def __call__(self, im, t):
        k = ease(t / self.dur)
        z = self.z[0] + (self.z[1] - self.z[0]) * k
        sx = sy = 0.0
        fl = None
        for imp in self.impacts:
            te, amp = imp[0], imp[1]
            if t < te:
                continue
            q = (t - te) / 0.45
            if q < 1:
                z += 0.014 * (amp / 20) * (1 - q) ** 2
                r = random.Random(int((t - te) * 600) + int(te * 97))
                a = amp * (1 - q) ** 2
                sx += r.uniform(-a, a)
                sy += r.uniform(-a, a)
            if len(imp) > 2 and imp[2] > 0:
                qf = (t - te) / 0.22
                if qf < 1:
                    s = imp[2] * (1 - qf) ** 2
                    col = imp[3] if len(imp) > 3 else WHITE
                    fl = (s, col) if fl is None or s > fl[0] else fl
        vw, vh = W / z, H / z
        cx = W / 2 + 14 * math.sin(t * 0.45) + sx
        cy = H / 2 + 8 * math.cos(t * 0.37) + sy
        x0 = clamp(cx - vw / 2, 0, W - vw)
        y0 = clamp(cy - vh / 2, 0, H - vh)
        if abs(z - 1) > 1e-4 or x0 or y0:
            im = im.transform((W, H), Image.AFFINE, (1 / z, 0, x0, 0, 1 / z, y0), Image.BILINEAR)
        if fl:
            im = Image.blend(im, Image.new("RGB", (W, H), fl[1]), clamp(fl[0]))
        return fx.vignette(im, 0.5)


# ================================================================ particles
def sparks(d, t, t0, x, y, n=28, seed=1, cols=(GOLD, WHITE), spd=900, life=0.75, g=1400, width=3, spread=None):
    dt = t - t0
    if dt < 0 or dt > life:
        return
    r = random.Random(seed)
    for i in range(n):
        if spread:
            a = r.uniform(spread[0], spread[1])
        else:
            a = r.uniform(0, 2 * math.pi)
        v = spd * r.uniform(0.3, 1.0)
        lf = life * r.uniform(0.45, 1.0)
        if dt > lf:
            continue
        vx, vy = math.cos(a) * v, math.sin(a) * v
        px = x + vx * dt
        py = y + vy * dt + 0.5 * g * dt * dt
        vy2 = vy + g * dt
        k = 1 - dt / lf
        col = glowc(cols[i % len(cols)], k ** 0.7)
        d.line((px - vx * 0.03, py - vy2 * 0.03, px, py), fill=col, width=width)


def ring(d, t, t0, x, y, r1=520, life=0.6, col=WHITE, width=14, squash=1.0):
    dt = t - t0
    if dt < 0 or dt > life:
        return
    k = dt / life
    r = r1 * eout(k)
    w = max(1, int(width * (1 - k)))
    d.ellipse((x - r, y - r * squash, x + r, y + r * squash), outline=glowc(col, (1 - k) ** 0.8), width=w)


def debris(d, t, t0, x, y, n=40, seed=3, cols=(GOLD, ORANGE, (120, 60, 20)), spd=1100, life=1.6, g=1500,
           box=(0, 0, 0, 0)):
    """chunky tumbling shards that fly out of a rectangle and fall"""
    dt = t - t0
    if dt < 0 or dt > life:
        return
    r = random.Random(seed)
    for i in range(n):
        sx = r.uniform(box[0], box[2]) if box[2] else x
        sy = r.uniform(box[1], box[3]) if box[3] else y
        a = math.atan2(sy - y, sx - x) + r.uniform(-0.6, 0.6) if box[2] else r.uniform(0, 2 * math.pi)
        a -= 0.5 * abs(math.cos(a)) * r.random()
        v = spd * r.uniform(0.25, 1.0)
        sz = r.uniform(6, 18)
        spin = r.uniform(-14, 14)
        lf = life * r.uniform(0.5, 1.0)
        if dt > lf:
            continue
        px = sx + math.cos(a) * v * dt
        py = sy + math.sin(a) * v * dt + 0.5 * g * dt * dt
        ang = spin * dt + i
        k = 1 - dt / lf
        pts = [(px + sz * math.cos(ang + j * 2.1) * (1 if j else 1.4), py + sz * math.sin(ang + j * 2.1) * (1 if j else 1.4))
               for j in range(3)]
        d.polygon(pts, fill=glowc(cols[i % len(cols)], k ** 0.6))


# ================================================================ odometer digits
_STRIPS = {}


def digit_strip(size, col, blur=False):
    key = (size, col, blur)
    if key not in _STRIPS:
        f = mono(size, True)
        cw = int(f.getlength("0"))
        ch = int(size * 1.0)
        im = Image.new("RGB", (cw, ch * 11), (0, 0, 0))
        d = ImageDraw.Draw(im)
        for i in range(11):
            d.text((cw / 2, ch * i + ch / 2), str(i % 10), font=f, fill=col, anchor="mm")
        if blur:
            im = vblur(im, ch // 3)
        _STRIPS[key] = (im, cw, ch)
    return _STRIPS[key]


def vblur(im, r):
    """cheap vertical motion blur: average shifted copies"""
    acc = im.copy()
    n = 1
    for k in range(1, r, max(1, r // 6)):
        acc = Image.blend(acc, ImageChops.offset(im, 0, k), 1 / (n + 1))
        n += 1
    return acc


def odometer(N, ndig):
    """per-digit float positions (most significant first) for a mechanical odometer showing N"""
    pos = []
    lower = 0.0
    for p in range(ndig):
        whole = math.floor(N / 10 ** p) % 10
        if p == 0:
            v = N % 10
        else:
            v = whole + max(0.0, lower - 9.0)
        pos.append(v)
        lower = v
    return pos[::-1]


# ================================================================ sfx cue lists and the render loop
def write_sfx(out_path, cues):
    p = Path(out_path)
    sp = p.with_name(p.stem + ".sfx.json")
    cues = sorted(({"t": round(float(t), 3), "sfx": s} for t, s in cues), key=lambda c: c["t"])
    tmp = sp.with_suffix(".tmp")
    nl = chr(10)
    tmp.write_text("[" + nl + ("," + nl).join(" " + json.dumps(c) for c in cues) + nl + "]" + nl, encoding="utf-8")
    tmp.replace(sp)
    return sp


STILLS = None   # (outdir, [t, ...]) -> render() saves PNG stills at those times instead of encoding


def render(out_path, dur, frame, cues):
    out_path = Path(out_path)
    if STILLS:
        od, times = STILLS
        for t in times:
            frame(min(t, dur - 1 / NES_FPS)).save(Path(od) / f"{out_path.stem}_{t:05.2f}.png")
        return out_path
    w = Writer(out_path)
    n = nframes(dur)
    for i in range(n):
        w.put(frame(i / NES_FPS))
    w.close()
    write_sfx(out_path, cues)
    print(f"{out_path.name}: {n} frames, {n / NES_FPS:.2f} s")
    return out_path


def title_pop(base, lg, t, t0, cx, cy, glow=(90, 60, 0)):
    """logo drops in from above with overshoot"""
    k = prog(t, t0, 0.5)
    if k <= 0:
        return
    put_logo(base, lg, cx, cy - (1 - eback(k)) * 90, scale=0.75 + 0.25 * eback(k), alpha=min(1, k * 3), glow=glow,
             glow_k=0.55)


# ================================================================ 1. progression
PROG = [("18:04.08", 1084.08, "DAY 5", "FIRST FINISH"), ("12:58.87", 778.87, "DAY 8", "UP5"),
        ("12:53.79", 773.79, "DAY 8", "UP6"), ("12:37.73", 757.73, "DAY 9", "UP9"),
        ("12:35.67", 755.67, "DAY 10", "UP10"), ("12:34.64", 754.64, "DAY 10", "UP11"),
        ("12:31.08", 751.08, "DAY 12", "UP12"), ("12:28.60", 748.60, "DAY 12", "UP13"),
        ("12:23.39", 743.39, "DAY 12", "UP14")]
REC = 749.25


def progression(out_path, dur=10.0):
    X0, DX = 330, 171.25
    YT, YB, VT, VB = 340, 900, 780.0, 740.0
    OFF_Y = 236

    def px(i):
        return X0 + i * DX

    def py(v):
        if v > VT + 1:
            return OFF_Y
        return YB - (v - VB) * (YB - YT) / (VT - VB)

    pts = [(px(i), py(v)) for i, (_, v, _, _) in enumerate(PROG)]
    ry = py(REC)
    T = [1.45 + i * 0.6 for i in range(8)] + [6.75]
    T_BEAT = T[7]
    # where the up12 -> up13 segment crosses the record line
    (ax, ay), (bx, by) = pts[6], pts[7]
    cross = (ax + (bx - ax) * (ry - ay) / (by - ay), ry)
    T_CROSS = T[7] - 0.3 + 0.3 * (ry - ay) / (by - ay)
    T_BIG = T[8] + 0.35
    lg_title = small_logo("CUTTING THE CLOCK", 62)
    lg_big = fx.logo("12:23.39", 150)
    f_ax = mono(24)
    f_lab = mono(28, True)
    f_x1 = mono(22, True)
    f_x2 = mono(19)
    f_rec = mono(26, True)
    post = Post(dur, impacts=[(T_CROSS, 10, 0.35, (255, 230, 150)), (T[7] + 0.12, 14), (T_BIG, 22, 0.5)])

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "DATA // verified routes, speedrun clock (starts when the toad lands)")
        # axes
        ka = eout(prog(t, 0.25, 0.6))
        if ka > 0:
            for v, s in ((780, "13:00"), (770, "12:50"), (760, "12:40"), (750, "12:30"), (740, "12:20")):
                y = py(v)
                xe = 240 + (1770 - 240) * ka
                d.line((240, y, xe, y), fill=(26, 40, 31), width=2)
                d.text((222, y), s, font=f_ax, fill=fade(DIM, ka), anchor="rm")
            d.line((240, YB, 240, YB - (YB - 205) * ka), fill=fade((70, 96, 78), ka), width=3)
            if ka > 0.7:
                # axis break: two slashes across the axis
                for yy in (300, 314):
                    d.line((228, yy + 6, 252, yy - 6), fill=fade(TEXT, (ka - 0.7) / 0.3), width=3)
                d.rectangle((238, 301, 242, 313), fill=BG)
                d.text((222, OFF_Y), "18:04", font=f_ax, fill=fade(DIM, (ka - 0.7) / 0.3), anchor="rm")
            # x labels
            for i, (_, _, dt_, nm) in enumerate(PROG):
                kx = prog(t, T[i] - 0.15, 0.3)
                if kx > 0:
                    d.text((px(i), 928 + (1 - eout(kx)) * 12), dt_, font=f_x1, fill=fade(TEXT, kx), anchor="ms")
                    d.text((px(i), 956 + (1 - eout(kx)) * 12), nm, font=f_x2, fill=fade(DIM, kx), anchor="ms")
        title_pop(base, lg_title, t, 0.0, 960, 132)
        # record line
        kr = eout(prog(t, 0.7, 0.7))
        if kr > 0:
            xe = 240 + (1770 - 240) * kr
            beaten = prog(t, T_CROSS, 0.25)
            pulse = 0.55 + 0.45 * math.sin(t * 5) if t > T_CROSS else 1
            g.line((240, ry, xe, ry), fill=glowc(GOLD, 0.95 if beaten == 0 else 0.6 + 0.4 * pulse), width=4)
            kl = prog(t, 1.0, 0.4)
            if kl > 0:
                d.text((256, ry - 14 - (1 - eout(kl)) * 10), "WORLD RECORD 12:29.25 (jay_cee)", font=f_rec,
                       fill=fade(GOLD, kl), anchor="ls")
        # line segments, drawn progressively
        for i in range(1, len(pts)):
            k = eout(prog(t, T[i] - 0.32, 0.32))
            if k <= 0:
                continue
            (x0, y0), (x1, y1) = pts[i - 1], pts[i]
            xe, ye = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
            col = TOAD if i < 8 else GOLD
            if i == 1:
                fx.dashed(g, (x0, y0), (xe, ye), glowc(TOAD, 0.75), width=4, dash=14, gap=10)
            else:
                g.line((x0, y0, xe, ye), fill=col, width=5)
        sparks(g, t, T_CROSS, cross[0], cross[1], n=40, seed=7, cols=(GOLD, WHITE, (255, 160, 40)), spd=700)
        ring(g, t, T_CROSS, cross[0], cross[1], r1=150, life=0.5, col=GOLD, width=8)
        # points + labels
        for i, (lab, v, _, _) in enumerate(PROG):
            k = prog(t, T[i], 0.4)
            if k <= 0:
                continue
            x, y = pts[i]
            s = eback(k, 2.5)
            col = GOLD if i == 8 else (TOAD if i < 7 else (180, 255, 120))
            r = 10 * s
            g.ellipse((x - r, y - r, x + r, y + r), fill=col)
            rr = 10 + 26 * eout(k)
            if k < 1:
                g.ellipse((x - rr, y - rr, x + rr, y + rr), outline=glowc(col, 1 - k), width=3)
            d.ellipse((x - 4 * s, y - 4 * s, x + 4 * s, y + 4 * s), fill=BG) if s > 0.3 else None
            kl = eout(prog(t, T[i] + 0.05, 0.3))
            if i == 0:
                d.text((x + 22, y - 12 + (1 - kl) * 10), lab, font=f_lab, fill=fade(WHITE, kl), anchor="ls")
                d.text((x + 22 + tw(d, lab + "  ", f_lab), y - 12 + (1 - kl) * 10), "FIRST TIME BEATEN",
                       font=mono(22, True), fill=fade(DIM, kl), anchor="ls")
            elif i in (7, 8):
                if i == 8:
                    continue
                d.text((x - 14, y + 16 + (1 - kl) * 10), lab, font=f_lab, fill=fade((190, 255, 140), kl), anchor="rt")
            else:
                d.text((x + 12, y - 16 + (1 - kl) * 10), lab, font=f_lab, fill=fade(TEXT, kl), anchor="ls")
        sparks(g, t, T[7], pts[7][0], pts[7][1], n=24, seed=11, cols=(TOAD, WHITE), spd=600)
        # "RECORD BEATEN" chip near up13
        kc = prog(t, T[7] + 0.12, 0.35)
        if kc > 0:
            sc = 1.6 - 0.6 * eback(kc, 2.2)
            fch = mono(int(32 * sc), True)
            cx, cy = pts[7][0], 610
            txt = "RECORD BEATEN"
            wch, hch = tw(d, txt, fch) + 26, 32 * sc * 1.25
            d.rectangle((cx - wch / 2, cy - hch / 2, cx + wch / 2, cy + hch / 2), fill=fade(GOLD, min(1, kc * 3)))
            d.text((cx, cy + 1), txt, font=fch, fill=(12, 10, 4), anchor="mm")
            if kc >= 1:
                d.line((cx, cy + hch / 2, cx, ry - 6), fill=GOLD, width=2)
        G2 = G
        base = add_glow(base, G2)
        # the final time, big (its burst goes behind it)
        if T_BIG <= t < T_BIG + 0.8:
            G3 = Image.new("RGB", (W, H), (0, 0, 0))
            g3 = ImageDraw.Draw(G3)
            sparks(g3, t, T_BIG, 1370, 405, n=50, seed=21, cols=(GOLD, WHITE, ORANGE), spd=1200, life=0.8, width=4)
            ring(g3, t, T_BIG, 1370, 405, r1=600, life=0.55, col=(255, 220, 120), width=12, squash=0.6)
            base = ImageChops.add(base, G3)
        kb = prog(t, T_BIG - 0.18, 0.18)
        if kb > 0:
            sc = 2.6 - 1.6 * ease(kb)
            put_logo(base, lg_big, 1370, 405, scale=sc, alpha=min(1, kb * 2), glow=(110, 70, 0), glow_k=0.9)
            dd = ImageDraw.Draw(base)
            ks = prog(t, T_BIG + 0.3, 0.35)
            if ks > 0:
                fx.chip(dd, 1370, 510 + (1 - eout(ks)) * 16, "5.86 s UNDER THE RECORD", col=fade(TOAD, ks), size=30,
                        anchor="mt")
            kk = prog(t, T_BIG + 0.5, 0.35)
            if kk > 0:
                dd.text((1370, 300 - (1 - eout(kk)) * 10), "UP14 · DAY 12 · FINAL ROUTE", font=mono(24, True),
                        fill=fade(TEXT, kk), anchor="ms")
        return post(base, t)

    cues = [(0.0, "whoosh"), (0.7, "whoosh")] + [(T[i], "blip") for i in range(7)] + \
           [(T[6] + 0.1, "riser"), (T_CROSS, "tick"), (T[7] + 0.12, "slam"), (T[8], "blip"), (T_BIG, "slam"), (T_BIG + 0.3, "ding")]
    return render(out_path, dur, frame, cues)


# ================================================================ 2. level_losses
LEVELS = [("L1", "RAGNAROK'S CANYON", 4.8, 4.3), ("L3", "TURBO TUNNEL", 203.6, 43.0),
          ("L4", "ARCTIC CAVERNS", 202.5, 85.4), ("L6", "KARNATH'S LAIR", 44.3, 32.1),
          ("L8", "INTRUDER EXCLUDER", 84.5, 88.0), ("L9", "TERRA TUBES", 170.0, 161.9),
          ("L10", "RAT RACE", 38.2, 35.8), ("L11", "CLINGER-WINGER", 123.3, 113.6),
          ("L12", "REVOLUTION", 179.1, 143.3), ("L13", "DARK QUEEN", 33.9, 41.8)]


def level_losses(out_path, dur=10.0):
    BX, SCALE = 520, 4.2
    RY0, RH = 268, 66
    LX = 492
    DCX = 1640
    TOP = {1: 4.0, 2: 4.75, 8: 5.5}
    T_DIM = 3.55
    T_CAP = 6.5
    lg_title = small_logo("WHERE THE TIME WENT", 66)
    f_lv = mono(27, True)
    f_nm = mono(25, True)
    f_val = mono(21, True)
    f_sub = mono(22)
    f_dl = mono(25, True)
    post = Post(dur, impacts=[(TOP[k] + 0.35, 14) for k in TOP] + [(T_CAP, 8)])

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "DATA // first finished run (day 5) vs the record, per level")
        title_pop(base, lg_title, t, 0.0, 960, 136)
        ks = prog(t, 0.35, 0.4)
        if ks > 0:
            d.text((120, 222), "SECONDS PER LEVEL", font=mono(22, True), fill=fade(DIM, ks), anchor="ls")
            # legend, right aligned
            x = BX
            for txt, col in (("AI, FIRST FINISH 18:04.08", TOAD), ("WORLD RECORD 12:29.25", GOLD)):
                d.rectangle((x, 222 - 17, x + 18, 222 - 1), fill=fade(col, ks))
                d.text((x + 30, 222), txt, font=f_sub, fill=fade(TEXT, ks), anchor="ls")
                x += 30 + tw(d, txt, f_sub) + 48
        dimk = eout(prog(t, T_DIM, 0.5))
        for i, (lv, nm, ours, rec) in enumerate(LEVELS):
            t0 = 0.6 + i * 0.16
            k = eout(prog(t, t0, 0.85))
            if k <= 0:
                continue
            y = RY0 + i * RH
            hot = i in TOP
            a = 1.0 if hot else 1 - 0.5 * dimk
            kin = prog(t, t0 - 0.1, 0.25)
            yl = y + 33
            xs = (1 - eout(kin)) * -30
            nmw = tw(d, nm, f_nm)
            d.text((LX + xs, yl), nm, font=f_nm, fill=fade(TEXT, a * kin), anchor="rm")
            d.text((LX - nmw - 14 + xs, yl), lv, font=f_lv, fill=fade(TOAD if not hot else (190, 255, 140), a * kin),
                   anchor="rm")
            # bars
            wo, wr = ours * SCALE * k, rec * SCALE * k
            d.rectangle((BX, y + 9, BX + max(2, wo), y + 31), fill=fade(TOAD, a))
            d.rectangle((BX, y + 35, BX + max(2, wr), y + 57), fill=fade(GOLD, a))
            d.text((BX + wo + 12, y + 20), f"{ours * k:.1f}", font=f_val, fill=fade(TEXT, a), anchor="lm")
            d.text((BX + wr + 12, y + 46), f"{rec * k:.1f}", font=f_val, fill=fade(mix(GOLD, TEXT, 0.4), a), anchor="lm")
            delta = rec - ours
            if hot:
                th = TOP[i]
                kh = prog(t, th, 0.35)
                if kh > 0:
                    x0 = BX + rec * SCALE
                    x1 = x0 + (ours - rec) * SCALE * eout(kh)
                    d.rectangle((x0, y + 9, x1, y + 31), fill=RED)
                    g.rectangle((x0, y + 9, x1, y + 31), fill=glowc(RED, 0.9 * (1 - 0.5 * kh)))
                    if kh < 1:
                        g.rectangle((x1 - 6, y + 4, x1 + 2, y + 36), fill=WHITE)
                    # dimension bracket over the lost stretch
                    kb2 = prog(t, th + 0.2, 0.3)
                    if kb2 > 0:
                        cbr = fade(RED_HI, kb2)
                        d.line((x0, y + 3, x0 + (ours - rec) * SCALE, y + 3), fill=cbr, width=2)
                        d.line((x0, y - 2, x0, y + 8), fill=cbr, width=2)
                        d.line((x0 + (ours - rec) * SCALE, y - 2, x0 + (ours - rec) * SCALE, y + 8), fill=cbr, width=2)
                kc = prog(t, th + 0.35, 0.4)
                if kc > 0:
                    sc = 1.7 - 0.7 * eback(kc, 2.2)
                    txt = f"−{ours - rec:.1f} s"
                    fch = mono(int(30 * sc), True)
                    wch, hch = tw(d, txt, fch) + 24, 30 * sc * 1.3
                    cx, cy = DCX + 30 + (1 - eout(kc)) * 140, yl
                    d.rectangle((cx - wch / 2, cy - hch / 2, cx + wch / 2, cy + hch / 2), fill=fade(RED, min(1, kc * 3)))
                    d.text((cx, cy + 1), txt, font=fch, fill=WHITE, anchor="mm")
                sparks(g, t, th + 0.35, DCX + 30, yl, n=26, seed=i * 13, cols=(RED_HI, WHITE, ORANGE), spd=650,
                       life=0.6)
            else:
                kd = prog(t, 3.1 + i * 0.03, 0.3)
                if kd > 0:
                    txt = (f"+{delta:.1f} s" if delta > 0 else f"−{-delta:.1f} s")
                    col = TOAD if delta > 0 else TEXT
                    d.text((DCX + 30, yl), txt, font=f_dl, fill=fade(col, kd * a), anchor="mm")
        # column header for deltas
        kh = prog(t, 3.0, 0.3)
        if kh > 0:
            d.text((DCX + 30, 222), "vs RECORD", font=mono(22, True), fill=fade(DIM, kh), anchor="ms")
        base = add_glow(base, G)
        kc = prog(t, T_CAP, 0.4)
        if kc > 0:
            dd = ImageDraw.Draw(base)
            f1 = mono(int(34 * (1.5 - 0.5 * eback(kc, 2))), True)
            s1, s2 = "3 LEVELS = ", "94% OF THE 5:35 GAP"
            w1, w2 = tw(dd, s1, f1), tw(dd, s2, f1)
            x0 = 960 - (w1 + w2) / 2
            dd.text((x0, 975), s1, font=f1, fill=fade(WHITE, kc), anchor="ls")
            dd.text((x0 + w1, 975), s2, font=f1, fill=fade(RED_HI, kc), anchor="ls")
        return post(base, t)

    cues = [(0.0, "whoosh")] + [(0.6 + i * 0.16, "tick") for i in range(10)] + [(T_DIM, "whoosh")]
    for i, th in TOP.items():
        cues += [(th, "riser" if i == 1 else "blip"), (th + 0.35, "slam")]
    cues += [(T_CAP, "ding")]
    return render(out_path, dur, frame, cues)


# ================================================================ 3. numbers
def _marks():
    rows = []
    for line in (LOGS / "token_marks.jsonl").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows


def numbers(out_path, dur=12.0):
    last = _marks()[-1]
    TOTAL, REPL, OUT_, CR, COST = last["total"], last["replies"], last["out"], last["cr"], last["cost"]
    NEW = TOTAL - OUT_ - CR
    days = 12
    T1, T2, T3, T3L, T4, T5, T6 = 0.7, 1.8, 3.1, 6.0, 6.8, 8.0, 9.6
    lg_title = small_logo("CLAUDE, BY THE NUMBERS", 66)
    hero = f"{TOTAL:,}"
    HS = 168
    f_hero = mono(HS, True)
    cw = int(f_hero.getlength("0"))
    f_val = mono(92, True)
    f_lab = mono(28, True)
    post = Post(dur, impacts=[(T1, 12), (T2, 12), (T3L, 26, 0.55), (T4, 12), (T6, 10)])
    cards = [(120, T1), (700, T2), (1280, T4)]

    def card(base, d, g, t, x, t0, val, lab, sub, col):
        k = prog(t, t0, 0.45)
        if k <= 0:
            return
        s = eback(k, 2.0)
        cx, cy, w, h = x + 260, 330, 520, 190
        w2, h2 = w * (0.85 + 0.15 * s) / 2, h * (0.85 + 0.15 * s) / 2
        d.rectangle((cx - w2, cy - h2, cx + w2, cy + h2), fill=fade(PANEL, min(1, k * 3)), outline=fade((40, 62, 48), k),
                    width=2)
        g.line((cx - w2, cy - h2, cx - w2 + 70 * s, cy - h2), fill=glowc(col, k), width=4)
        g.line((cx - w2, cy - h2, cx - w2, cy - h2 + 40 * s), fill=glowc(col, k), width=4)
        g.text((cx, cy - 22), val, font=f_val, fill=glowc(col, min(1, k * 2)), anchor="mm")
        d.text((cx, cy + 50), lab, font=f_lab, fill=fade(TEXT, k), anchor="mm")
        if sub:
            d.text((cx, cy + 80), sub, font=mono(20), fill=fade(DIM, k), anchor="mm")

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "DATA // logs/token_marks.jsonl, 475 marks")
        title_pop(base, lg_title, t, 0.0, 960, 136)
        n1 = int(round(days * eout(prog(t, T1, 0.6))))
        card(base, d, g, t, 120, T1, f"{n1}", "DAYS", "DAY 1 → DAY 12", TOAD)
        n2 = int(round(REPL * eout(prog(t, T2, 0.8))))
        card(base, d, g, t, 700, T2, f"{n2:,}", "AI REPLIES", "messages Claude sent", TOAD)
        n4 = int(round(COST * eout(prog(t, T4, 0.7))))
        card(base, d, g, t, 1280, T4, f"~${n4:,}", "AT API LIST PRICES", "cost if billed per token", GOLD)
        # hero odometer
        kh = prog(t, T3, 0.35)
        if kh > 0:
            kspin = prog(t, T3, T3L - T3)
            N = TOTAL * (1 - (1 - kspin) ** 2.6)
            if t >= T3L:
                N = TOTAL
            ndig = len(str(TOTAL))
            pos = odometer(N, ndig)
            prev = odometer(TOTAL * (1 - (1 - prog(t - 1 / NES_FPS, T3, T3L - T3)) ** 2.6), ndig)
            landed = t >= T3L
            col = GOLD if landed else (255, 225, 120)
            strip, scw, sch = digit_strip(HS, col)
            bstrip, _, _ = digit_strip(HS, col, blur=True)
            total_w = len(hero) * cw
            x = 960 - total_w / 2
            cy = 548
            di = 0
            sc = 0.8 + 0.2 * eback(kh)
            for ch in hero:
                if ch == ",":
                    g.text((x + cw / 2, cy + 8), ",", font=f_hero, fill=glowc(col, kh), anchor="mm")
                else:
                    p = pos[di] % 10
                    speed = abs(pos[di] - prev[di])
                    st = bstrip if speed > 0.35 and not landed else strip
                    oy = int(p * sch)
                    cell = st.crop((0, oy, scw, oy + sch))
                    if kh < 1:
                        cell = ImageEnhance.Brightness(cell).enhance(kh)
                    G.paste(cell, (int(x), int(cy - sch / 2)))
                    di += 1
                x += cw
            # mask edges of the drum: dark bands above/below
            # label
            kl = prog(t, T3 + 0.15, 0.4)
            d.text((960, 668), "TOKENS", font=mono(40, True), fill=fade(TEXT, kl), anchor="mm")
            if not landed:
                # drum window lines
                d.line((960 - total_w / 2 - 20, cy - sch / 2 - 6, 960 + total_w / 2 + 20, cy - sch / 2 - 6),
                       fill=fade((50, 72, 58), kh), width=2)
                d.line((960 - total_w / 2 - 20, cy + sch / 2 + 6, 960 + total_w / 2 + 20, cy + sch / 2 + 6),
                       fill=fade((50, 72, 58), kh), width=2)
            for side in (-1, 1):
                ex = 960 + side * (total_w / 2 + 16)
                spr = (-0.9, 0.9) if side > 0 else (math.pi - 0.9, math.pi + 0.9)
                sparks(g, t, T3L, ex, cy, n=34, seed=5 + side, cols=(GOLD, WHITE, ORANGE), spd=1300, life=0.8,
                       width=4, spread=spr)
            ring(g, t, T3L, 960, cy, r1=900, life=0.6, col=(255, 220, 120), width=14, squash=0.45)
        # split bar
        kb = prog(t, T5, 0.9)
        if kb > 0:
            BX0, BX1, BY0, BY1 = 120, 1800, 790, 846
            L = BX1 - BX0
            wo = max(7, L * OUT_ / TOTAL)
            wn = max(10, L * NEW / TOTAL)
            xe = BX0 + L * eout(kb)
            d.rectangle((BX0, BY0, BX1, BY1), outline=fade((40, 62, 48), min(1, kb * 3)), width=2)
            # segments: written | new context | re-read
            g.rectangle((BX0, BY0, min(xe, BX0 + wo), BY1), fill=TOAD)
            if xe > BX0 + wo:
                d.rectangle((BX0 + wo, BY0, min(xe, BX0 + wo + wn), BY1), fill=TEAL)
            if xe > BX0 + wo + wn:
                d.rectangle((BX0 + wo + wn + 1, BY0, xe, BY1), fill=mix(GOLD, BG, 0.15))
                # sheen sweep across the gold
                sx = BX0 + (BX1 - BX0) * prog(t, T5 + 0.9, 0.9)
                if T5 + 0.9 < t < T5 + 1.8:
                    g.polygon([(sx - 60, BY0), (sx, BY0), (sx - 30, BY1), (sx - 90, BY1)], fill=(120, 100, 40))
            k1 = prog(t, T5 + 0.9, 0.35)
            if k1 > 0:
                yy = BY0 - 22 - (1 - eout(k1)) * 10
                d.line((BX0 + 3, BY0 - 4, BX0 + 3, yy + 6), fill=fade(TOAD, k1), width=3)
                d.text((BX0, yy), f"{OUT_ / 1e6:.1f} M WRITTEN", font=mono(30, True), fill=fade(TOAD, k1), anchor="ls")
                d.text((BX0 + tw(d, f"{OUT_ / 1e6:.1f} M WRITTEN  ", mono(30, True)), yy),
                       f"({100 * OUT_ / TOTAL:.1f}%)", font=mono(24), fill=fade(DIM, k1), anchor="ls")
            k2 = prog(t, T5 + 1.1, 0.35)
            if k2 > 0:
                yy = BY0 - 22 - (1 - eout(k2)) * 10
                d.text((BX1, yy), f"{CR / 1e9:.1f} B RE-READ", font=mono(30, True), fill=fade(GOLD, k2), anchor="rs")
                d.text((BX1 - tw(d, f"{CR / 1e9:.1f} B RE-READ  ", mono(30, True)), yy),
                       f"({100 * CR / TOTAL:.0f}%)", font=mono(24), fill=fade(DIM, k2), anchor="rs")
        base = add_glow(base, G)
        kc = prog(t, T6, 0.4)
        if kc > 0:
            dd = ImageDraw.Draw(base)
            sc = 1.5 - 0.5 * eback(kc, 2)
            f1 = mono(int(42 * sc), True)
            s1, s2 = "99%", " OF THE TOKENS WERE RE-READING"
            w1, w2 = tw(dd, s1, f1), tw(dd, s2, f1)
            x0 = 960 - (w1 + w2) / 2
            dd.text((x0, 922), s1, font=f1, fill=fade(GOLD, kc), anchor="ls")
            dd.text((x0 + w1, 922), s2, font=f1, fill=fade(WHITE, kc), anchor="ls")
            k2 = prog(t, T6 + 0.4, 0.4)
            if k2 > 0:
                dd.text((960, 968), "every reply re-reads the whole conversation so far", font=mono(26),
                        fill=fade(DIM, k2), anchor="ms")
        return post(base, t)

    cues = [(0.0, "whoosh"), (T1, "slam"), (T2, "slam"), (T3, "riser"), (T3L, "slam"), (T4, "slam"), (T5, "whoosh"),
            (T5 + 0.9, "blip"), (T5 + 1.1, "blip"), (T6, "ding")]
    cues += [(T1 + 0.05 * i, "tick") for i in range(1, 12, 2)]
    return render(out_path, dur, frame, cues)


# ================================================================ 4. token_phases
MILESTONES = [  # (mark text prefix, label, sub, label anchor x offset, label y, side)
    ("first boot recorded", "FIRST BOOT", None),
    ("Level 1 solved", "LEVEL 1 SOLVED", None),
    ("Turbo Tunnel cleared by the reactive policy", "TURBO TUNNEL CLEARED", None),
    ("LEVEL 4 COMPLETE", "LEVEL 4 WARP", None),
    ("GAME BEATEN", "GAME BEATEN · 18:04", None),
    ("WR comparison + tunnel skip found", "TUNNEL SKIP FOUND", None),
    ("route up5 verified", "UNDER 13:00 · 12:58.87", None),
    ("up13 = 12:28.60 verified", "RECORD BEATEN · 12:28.60", None),
    ("up14 = 12:23.39 verified", "12:23.39", None),
]


def _ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def token_phases(out_path, dur=12.0):
    rows = _marks()
    t0d = datetime(2026, 9, 26, tzinfo=timezone.utc)
    DAYS = 12.0
    PX0, PX1, PY0, PY1 = 230, 1760, 272, 900
    VMAX = 3.5e9

    def xd(day):
        return PX0 + (PX1 - PX0) * day / DAYS

    def yv(v):
        return PY1 - (PY1 - PY0) * v / VMAX

    start = _ts(rows[0]["since"])
    data = [((start - t0d).total_seconds() / 86400, 0.0)]
    for r in rows:
        data.append(((_ts(r["ts"]) - t0d).total_seconds() / 86400, float(r["total"])))
    data.sort()
    D0, D1 = data[0][0], data[-1][0]
    ms = []
    for key, lab, _ in MILESTONES:
        r = next(r for r in rows if r["mark"].startswith(key))
        dd = (_ts(r["ts"]) - t0d).total_seconds() / 86400
        ms.append((dd, r["total"], lab, r["ts"]))
    beat_day = ms[4][0]
    # label placement: (dx of the label anchor from the point, label y, anchor 'l' or 'r', leader up/down)
    place = [(10, 330, "l"), (10, 398, "l"), (10, 466, "l"), (10, 534, "l"),
             (10, 452, "l"), (10, 724, "l"), (10, 356, "l"), (-12, 510, "r"), (-14, 300, "r")]
    TR0, TR1 = 0.9, 8.4

    def head_day(t):
        return D0 + (D1 - D0) * ease(prog(t, TR0, TR1 - TR0)) if t < TR1 else D1

    def val_at(day):
        for (a, va), (b, vb) in zip(data, data[1:]):
            if a <= day <= b:
                return va + (vb - va) * ((day - a) / (b - a) if b > a else 1)
        return data[-1][1] if day >= D1 else 0.0

    def t_of_day(day):
        # invert head_day numerically
        lo, hi = TR0, TR1
        for _ in range(40):
            mid = (lo + hi) / 2
            if head_day(mid) < day:
                lo = mid
            else:
                hi = mid
        return hi

    T_MS = [t_of_day(m[0]) for m in ms]
    T_MS[-1] = max(T_MS[-1], TR1) + 0.25
    lg_title = small_logo("WHERE THE TOKENS WENT", 64)
    f_ax = mono(22)
    f_ml = mono(25, True)
    f_ms = mono(19)
    post = Post(dur, impacts=[(T_MS[4], 10), (T_MS[7], 12, 0.25, (255, 230, 150)), (T_MS[8], 18, 0.35)])
    area_col = Image.new("RGB", (W, H), (36, 92, 30))
    p1tot = ms[4][1]

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "DATA // logs/token_marks.jsonl, cumulative tokens")
        title_pop(base, lg_title, t, 0.0, 960, 132)
        ka = eout(prog(t, 0.2, 0.6))
        # phase bands
        kp = prog(t, 0.5, 0.5)
        if kp > 0:
            xb = xd(beat_day)
            d.rectangle((PX0, PY0, xb, PY1), fill=fade((14, 24, 17), kp))
            d.rectangle((xb, PY0, PX1, PY1), fill=fade((22, 22, 13), kp))
            d.line((xb, PY0 - 30, xb, PY1), fill=fade((60, 70, 50), kp), width=2)
            f_ph = mono(23, True)
            d.text(((PX0 + xb) / 2, 238), "PHASE 1 · BEAT THE GAME", font=f_ph, fill=fade(TOAD, kp), anchor="ms")
            d.text(((xb + PX1) / 2, 238), "PHASE 2 · BEAT THE RECORD", font=f_ph, fill=fade(GOLD, kp), anchor="ms")
            kq = prog(t, T_MS[4], 0.4)
            if kq > 0:
                d.text(((PX0 + xb) / 2, 262), f"{p1tot / 1e9:.2f} B tokens · 4.3 days", font=f_ms,
                       fill=fade(DIM, kq), anchor="ms")
            kq = prog(t, T_MS[8], 0.4)
            if kq > 0:
                d.text(((xb + PX1) / 2, 262), f"{(rows[-1]['total'] - p1tot) / 1e9:.2f} B tokens · 7.1 days",
                       font=f_ms, fill=fade(DIM, kq), anchor="ms")
        # axes
        if ka > 0:
            for b in range(0, 4):
                y = yv(b * 1e9)
                d.line((PX0, y, PX0 + (PX1 - PX0) * ka, y), fill=(30, 44, 35) if b else (70, 96, 78), width=2 if b else 3)
                d.text((PX0 - 16, y), "0" if b == 0 else f"{b} B", font=f_ax, fill=fade(DIM, ka), anchor="rm")
            for day in range(13):
                x = xd(day)
                d.line((x, PY1, x, PY1 + 8), fill=fade((70, 96, 78), ka), width=2)
                if day < 12:
                    lab = f"DAY {day + 1}" if day == 0 else str(day + 1)
                    d.text((x + (xd(1) - xd(0)) / 2, PY1 + 34), lab, font=f_ax, fill=fade(DIM, ka), anchor="ms")
        # the area up to the reveal head
        hd = head_day(t)
        if t > TR0:
            poly = [(xd(D0), PY1)]
            for day, v in data:
                if day > hd:
                    break
                poly.append((xd(day), yv(v)))
            hv = val_at(hd)
            poly.append((xd(hd), yv(hv)))
            poly.append((xd(hd), PY1))
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).polygon(poly, fill=120)
            # brighter toward the top edge: second pass
            base.paste(area_col, (0, 0), mask)
            line = poly[1:-1]
            if len(line) > 1:
                g.line(line, fill=TOAD, width=4, joint="curve")
            # head
            hx, hy = xd(hd), yv(hv)
            if t < TR1 + 0.6:
                kf = 1 - prog(t, TR1, 0.6)
                g.ellipse((hx - 8, hy - 8, hx + 8, hy + 8), fill=glowc(WHITE, kf))
                g.line((hx, hy + 12, hx, PY1), fill=glowc((90, 160, 70), kf * 0.6), width=2)
                d.text((hx + 16, hy - 16), f"{hv / 1e9:.2f} B", font=mono(26, True), fill=fade(WHITE, kf),
                       anchor="ls") if hx < 1500 else None
        # milestones
        for i, (day, v, lab, ts) in enumerate(ms):
            k = prog(t, T_MS[i], 0.35)
            if k <= 0:
                continue
            x, y = xd(day), yv(v)
            dx, ly, side = place[i]
            last = i == len(ms) - 1
            col = GOLD if i >= 7 else (WHITE if i != 4 else (190, 255, 140))
            s = eback(k, 2.4)
            r = (9 if last else 7) * s
            g.ellipse((x - r, y - r, x + r, y + r), fill=GOLD if i >= 7 else WHITE)
            if k < 1:
                rr = 8 + 30 * eout(k)
                g.ellipse((x - rr, y - rr, x + rr, y + rr), outline=glowc(col, 1 - k), width=3)
            kl = eout(prog(t, T_MS[i] + 0.05, 0.3))
            if kl <= 0:
                continue
            # leader
            top = ly - 26 if ly < y else ly - 26
            if ly < y:
                y_lead_end = ly + 8
            else:
                y_lead_end = ly - 30
            ye = y + (y_lead_end - y) * kl
            d.line((x, y + (-10 if ly < y else 10), x, ye), fill=fade((120, 140, 125), kl), width=2)
            when = f"DAY {(_ts(ts) - datetime(2026, 9, 26, tzinfo=timezone.utc)).days + 1}"
            sub = f"{when} · {v / 1e9:.2f} B" if v >= 1e8 else f"{when} · {v / 1e6:.0f} M"
            fl = mono(48, True) if last else f_ml
            lab_w = max(tw(d, lab, fl), tw(d, sub, f_ms))
            xa = x + dx
            xl = xa if side == "l" else xa - lab_w
            # dark pill behind labels that sit over the area
            if i in (5, 7):
                d.rectangle((xl - 10, ly - 30, xl + lab_w + 10, ly + 30), fill=fade((10, 20, 12), kl))
            off = (1 - kl) * 10
            d.text((xl, ly + off), lab, font=fl, fill=fade(col, kl), anchor="ls")
            d.text((xl, ly + 24 + off), sub, font=f_ms, fill=fade(DIM if not last else TEXT, kl), anchor="ls")
        sparks(g, t, T_MS[7], xd(ms[7][0]), yv(ms[7][1]), n=30, seed=4, cols=(GOLD, WHITE), spd=650)
        sparks(g, t, T_MS[8], xd(ms[8][0]), yv(ms[8][1]), n=46, seed=9, cols=(GOLD, WHITE, ORANGE), spd=900)
        ring(g, t, T_MS[8], xd(ms[8][0]), yv(ms[8][1]), r1=260, life=0.5, col=GOLD, width=8)
        base = add_glow(base, G)
        return post(base, t)

    cues = [(0.0, "whoosh"), (TR0, "riser")] + [(tm, "blip") for tm in T_MS[:4]] + \
           [(T_MS[4], "slam"), (T_MS[5], "blip"), (T_MS[6], "blip"), (T_MS[7], "slam"), (T_MS[8], "ding")]
    return render(out_path, dur, frame, cues)


# ================================================================ 5. rules
RULES = [("ok", "Hidden warps in levels 1, 4 and 6", "ALLOWED"),
         ("ok", "Level-end tricks: the Turbo Tunnel bike skip, the rat boot", "ALLOWED"),
         ("ok", "Out of bounds, damage boosts, any route you like", "ALLOWED"),
         ("no", "Credits warp (corrupts memory, jumps to the ending)", "BANNED"),
         ("no", "Left+Right or Up+Down at the same time", "BANNED"),
         ("no", "Turbo controllers", "BANNED"),
         ("clock", "Timer starts when you get control of the toad in level 1", "TIMING"),
         ("clock", "Timer stops when control is lost after the Dark Queen", "TIMING")]


def icon(d, g, kind, cx, cy, r, k):
    col = {"ok": TOAD, "no": RED, "clock": CYAN}[kind]
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fade(mix(col, BG, 0.75), k), outline=fade(col, k), width=3)
    w = max(3, int(r * 0.2))
    if kind == "ok":
        pts = [(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.38)]
        g.line(pts, fill=glowc(col, k), width=w, joint="curve")
        d.line(pts, fill=fade(WHITE, k), width=max(2, w - 3), joint="curve")
    elif kind == "no":
        a = r * 0.38
        for p in ((cx - a, cy - a, cx + a, cy + a), (cx - a, cy + a, cx + a, cy - a)):
            g.line(p, fill=glowc(col, k), width=w)
            d.line(p, fill=fade(WHITE, k), width=max(2, w - 3))
    else:
        rr = r * 0.55
        d.ellipse((cx - rr, cy - rr + 3, cx + rr, cy + rr + 3), outline=fade(WHITE, k), width=3)
        d.rectangle((cx - 4, cy - rr - 6, cx + 4, cy - rr + 1), fill=fade(WHITE, k))
        d.line((cx, cy + 3, cx, cy - rr * 0.6 + 3), fill=fade(WHITE, k), width=3)
        d.line((cx, cy + 3, cx + rr * 0.5, cy + 3), fill=fade(WHITE, k), width=3)
        g.ellipse((cx - rr, cy - rr + 3, cx + rr, cy + rr + 3), outline=glowc(col, k), width=4)


def rules(out_path, dur=11.0):
    lg_title = small_logo("THE RULES", 100)
    TI = [0.85 + i * 0.6 for i in range(len(RULES))]
    TG = [TI[-1] + 0.9, TI[-1] + 1.55]
    goals = [("GOAL 1", small_logo("BEAT THE GAME", 60, GREEN_LOGO), TOAD, 140),
             ("GOAL 2", small_logo("BEAT 12:29.25", 60), GOLD, 1000)]
    f_it = mono(31, True)
    f_tag = mono(22, True)
    post = Post(dur, impacts=[(tt + 0.12, 9) for tt in TI] + [(TG[0] + 0.3, 14), (TG[1] + 0.3, 18)])

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "SOURCE // speedrun.com/battletoads, Any% (No Credits Warp)")
        title_pop(base, lg_title, t, 0.0, 960, 146)
        ks = prog(t, 0.35, 0.4)
        if ks > 0:
            d.text((960, 250), "SPEEDRUN.COM · BATTLETOADS (NES) · ANY% (NO CREDITS WARP)", font=mono(26, True),
                   fill=fade(DIM, ks), anchor="ms")
        for i, (kind, txt, tag) in enumerate(RULES):
            k = prog(t, TI[i], 0.4)
            if k <= 0:
                continue
            y = 300 + i * 54
            xo = (1 - eback(k, 1.8)) * -260
            a = min(1, k * 2.5)
            col = {"ok": TOAD, "no": RED, "clock": CYAN}[kind]
            # row panel
            d.rectangle((150 + xo, y - 24, 1770 + xo, y + 24), fill=fade(PANEL, a))
            d.rectangle((150 + xo, y - 24, 156 + xo, y + 24), fill=fade(col, a))
            ki = eback(prog(t, TI[i] + 0.08, 0.35), 2.6)
            if ki > 0:
                icon(d, g, kind, 212 + xo, y, 19 * ki, a)
            d.text((268 + xo, y + 2), txt, font=f_it, fill=fade(TEXT if kind != "no" else (235, 215, 210), a),
                   anchor="lm")
            kt = prog(t, TI[i] + 0.15, 0.3)
            if kt > 0:
                wtag = tw(d, tag, f_tag) + 24
                x1 = 1748 + xo
                d.rectangle((x1 - wtag, y - 16, x1, y + 16), outline=fade(col, kt), width=2)
                d.text((x1 - wtag / 2, y + 1), tag, font=f_tag, fill=fade(col, kt), anchor="mm")
            if k < 1:
                g.rectangle((150 + xo, y - 24, 1770 + xo, y + 24), outline=glowc(col, 1 - k), width=3)
        for j, (cap, lg, col, x) in enumerate(goals):
            k = prog(t, TG[j], 0.5)
            if k <= 0:
                continue
            xo = (1 - eback(k, 1.4)) * (-900 if j == 0 else 900)
            a = min(1, k * 2)
            x0, y0, x1, y1 = x + xo, 760, x + 780 + xo, 970
            d.rectangle((x0, y0, x1, y1), fill=fade((10, 16, 12), a), outline=fade(mix(col, BG, 0.4), a), width=2)
            g.rectangle((x0, y0, x1, y1), outline=glowc(col, a * (0.5 + 0.5 * (1 - prog(t, TG[j] + 0.4, 0.6)))),
                        width=4)
            d.rectangle((x0, y0, x0 + 150, y0 + 40), fill=fade(col, a))
            d.text((x0 + 75, y0 + 21), cap, font=mono(26, True), fill=(10, 10, 6), anchor="mm")
        base = add_glow(base, G)
        for j, (cap, lg, col, x) in enumerate(goals):
            k = prog(t, TG[j], 0.5)
            if k <= 0:
                continue
            xo = (1 - eback(k, 1.4)) * (-900 if j == 0 else 900)
            kl = prog(t, TG[j] + 0.3, 0.25)
            sc = 1.5 - 0.5 * ease(kl) if kl > 0 else 0
            put_logo(base, lg, x + 390 + xo, 883, scale=sc, alpha=min(1, kl * 2),
                     glow=(60, 110, 20) if j == 0 else (110, 70, 0), glow_k=0.6)
        return post(base, t)

    cues = [(0.0, "whoosh")] + [(tt + 0.12, "slam") for tt in TI] + [(TG[0], "whoosh"), (TG[0] + 0.3, "slam"),
                                                                    (TG[1], "whoosh"), (TG[1] + 0.3, "slam")]
    return render(out_path, dur, frame, cues)


# ================================================================ 6. tas
def tas(out_path, dur=9.0):
    lg_title = small_logo("WHAT'S A TAS?", 96)
    lg_vs = small_logo("VS", 56, WHITE_LOGO)
    DEF = "built on an emulator with save states, played back as a file of button presses"
    T_DEF, T_TYPE0, T_TYPE1 = 0.55, 0.95, 2.55
    T_COLS = (3.0, 3.25)
    ROWS = [("BUILT BY", "people, frame by frame", "an AI writing its own search tools"),
            ("TIME", "months of work", "12 days"),
            ("INPUTS", "any input, e.g. Left+Right", "held to the human rules")]
    TR = [3.85, 4.75, 5.65]
    T_HI = 6.6
    post = Post(dur, impacts=[(T_COLS[1] + 0.25, 12)] + [(tr + 0.3, 7) for tr in TR] + [(T_HI, 10, 0.18, (200, 255, 160))])
    f_cap = mono(21, True)
    f_val = mono(30, True)
    cols = [(130, "TYPICAL TAS", CYAN), (1030, "THIS RUN", TOAD)]

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "TAS = tool-assisted speedrun")
        title_pop(base, lg_title, t, 0.0, 960, 140)
        k = prog(t, T_DEF, 0.4)
        if k > 0:
            y0 = 236
            d.rectangle((130, y0, 1790, y0 + 130), fill=fade(PANEL, k), outline=fade((40, 62, 48), k), width=2)
            d.rectangle((130, y0, 138, y0 + 130), fill=fade(CYAN, k))
            g.text((170, y0 + 46), "TOOL-ASSISTED SPEEDRUN", font=mono(38, True), fill=glowc(CYAN, k), anchor="lm")
            n = int(len(DEF) * prog(t, T_TYPE0, T_TYPE1 - T_TYPE0))
            shown = DEF[:n]
            ft = mono(30)
            d.text((170, y0 + 96), shown, font=ft, fill=TEXT, anchor="lm")
            if t < T_TYPE1 + 0.8 and int(t * 4) % 2 == 0:
                cx = 170 + tw(d, shown, ft) + 4
                d.rectangle((cx, y0 + 80, cx + 14, y0 + 112), fill=CYAN)
        for j, (x, head, col) in enumerate(cols):
            k = prog(t, T_COLS[j], 0.45)
            if k <= 0:
                continue
            yo = (1 - eback(k, 1.6)) * 120
            a = min(1, k * 2.5)
            x0, y0, x1, y1 = x, 412 + yo, x + 760, 950 + yo
            hi = j == 1 and t > T_HI
            d.rectangle((x0, y0, x1, y1), fill=fade((11, 17, 13), a), outline=fade(mix(col, BG, 0.45), a), width=2)
            d.rectangle((x0, y0, x1, y0 + 72), fill=fade(mix(col, BG, 0.78), a))
            g.text((x0 + 36, y0 + 37), head, font=mono(40, True), fill=glowc(col, a), anchor="lm")
            if hi:
                kh = prog(t, T_HI, 0.5)
                g.rectangle((x0, y0, x1, y1), outline=glowc(TOAD, 0.4 + 0.6 * (1 - kh) + 0.15 * math.sin(t * 4)),
                            width=4)
            for r, (cap, lv, rv) in enumerate(ROWS):
                tr = TR[r] + (0.3 if j else 0)
                kr = prog(t, tr, 0.35)
                if kr <= 0:
                    continue
                yy = y0 + 122 + r * 146
                xs = (1 - eout(kr)) * 40
                d.text((x0 + 36 + xs, yy), cap, font=f_cap, fill=fade(DIM, kr), anchor="ls")
                txt = rv if j else lv
                d.text((x0 + 36 + xs, yy + 50), txt, font=f_val, fill=fade(WHITE if j else TEXT, kr), anchor="ls")
                if r < 2:
                    d.line((x0 + 36, yy + 88, x1 - 36, yy + 88), fill=fade((28, 42, 33), kr), width=2)
                # marker dot
                g.ellipse((x0 + 14, yy + 32, x0 + 24, yy + 42), fill=glowc(col, kr))
        base = add_glow(base, G)
        kv = prog(t, T_COLS[1] + 0.25, 0.3)
        if kv > 0:
            put_logo(base, lg_vs, 960, 681, scale=2.2 - 1.2 * ease(kv), alpha=min(1, kv * 2), glow=(70, 80, 70),
                     glow_k=0.5)
        return post(base, t)

    cues = [(0.0, "whoosh"), (T_DEF, "blip")] + [(T_TYPE0 + 0.12 * i, "tick") for i in range(13)] + \
           [(T_COLS[0], "whoosh"), (T_COLS[1], "whoosh"), (T_COLS[1] + 0.25, "slam")] + \
           [(tr, "blip") for tr in TR] + [(tr + 0.3, "blip") for tr in TR] + [(T_HI, "ding")]
    return render(out_path, dur, frame, cues)


# ================================================================ 7. record_card
def record_card(out_path, dur=5.0):
    lg = fx.logo("12:29.25", 250)
    T_FRAME, T_TOP, T_BIG, T_SUB, T_SHINE = 0.0, 0.3, 0.6, 1.15, 1.9
    LAND = T_BIG + 0.18
    post = Post(dur, impacts=[(LAND, 26, 0.6)], z=(1.0, 1.03))
    CX, CY = 960, 548
    lw, lh = lg.size
    shine_mask = lg.getchannel("A")

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "SOURCE // speedrun.com/battletoads leaderboard")
        k = eout(prog(t, T_FRAME, 0.5))
        if k > 0:
            hw, hh = 760 * k, 300 * (0.3 + 0.7 * k)
            d.rectangle((CX - hw, CY - hh, CX + hw, CY + hh), fill=fade((11, 15, 10), k))
            g.rectangle((CX - hw, CY - hh, CX + hw, CY + hh), outline=glowc(mix(GOLD, BG, 0.35), k), width=3)
            # corner ticks
            for sx in (-1, 1):
                for sy in (-1, 1):
                    x, y = CX + sx * (hw + 14), CY + sy * (hh + 14)
                    g.line((x, y, x - sx * 46, y), fill=glowc(GOLD, k), width=4)
                    g.line((x, y, x, y - sy * 46), fill=glowc(GOLD, k), width=4)
        kt = prog(t, T_TOP, 0.4)
        if kt > 0:
            txt = "W O R L D   R E C O R D"
            g.text((CX, 330 - (1 - eout(kt)) * 16), txt, font=mono(40, True), fill=glowc(GOLD, kt), anchor="mm")
            wl = 620 * eout(kt)
            d.line((CX - wl / 2, 370, CX + wl / 2, 370), fill=fade((90, 80, 40), kt), width=2)
        ks = prog(t, T_SUB, 0.45)
        if ks > 0:
            f = mono(34, True)
            parts = [("jay_cee", WHITE), ("  ·  ", DIM), ("speedrun.com", TEXT), ("  ·  ", DIM),
                     ("Any% (No Credits Warp)", TEXT)]
            wsum = sum(tw(d, p, f) for p, _ in parts)
            x = CX - wsum / 2
            yy = 742 + (1 - eout(ks)) * 18
            for p, c in parts:
                d.text((x, yy), p, font=f, fill=fade(c, ks), anchor="ls")
                x += tw(d, p, f)
        sparks(g, t, LAND, CX, CY, n=64, seed=12, cols=(GOLD, WHITE, ORANGE), spd=1300, life=0.9)
        ring(g, t, LAND, CX, CY, r1=1000, life=0.6, col=(255, 220, 120), width=16, squash=0.5)
        base = add_glow(base, G)
        kb = prog(t, T_BIG, 0.18)
        if kb > 0:
            sc = 3.0 - 2.0 * ease(kb)
            put_logo(base, lg, CX, CY, scale=sc, alpha=min(1, kb * 2), glow=(130, 85, 0), glow_k=0.9)
            # shine sweep
            kk = prog(t, T_SHINE, 0.7)
            if 0 < kk < 1:
                band = Image.new("L", (lw, lh), 0)
                bx = -200 + (lw + 400) * kk
                ImageDraw.Draw(band).polygon([(bx, 0), (bx + 90, 0), (bx + 30, lh), (bx - 60, lh)], fill=150)
                band = ImageChops.multiply(band, shine_mask)
                spr = Image.merge("RGB", (band, band, band.point(lambda p: p * 3 // 4)))
                add_at(base, spr, CX - lw / 2, CY - lh / 2)
        return post(base, t)

    cues = [(0.0, "whoosh"), (T_TOP, "blip"), (T_BIG, "whoosh"), (LAND, "slam"), (T_SUB, "blip"), (T_SHINE, "ding")]
    return render(out_path, dur, frame, cues)


# ================================================================ 8. title_card
def title_card(out_path, dur=3.0):
    lg_ai = fx.logo("AI", 126, top=GREEN_LOGO[0], bottom=GREEN_LOGO[1], extrude=GREEN_LOGO[2])
    lg_vs = small_logo("vs", 72, WHITE_LOGO)
    lg_bt = fx.logo("BATTLETOADS", 126)
    T0 = 0.12
    LAND = T0 + 0.18
    T_SUB = 0.85
    post = Post(dur, impacts=[(LAND, 30, 0.75)], z=(1.0, 1.03))
    gap = 22
    total = lg_ai.width + gap + lg_vs.width + gap + lg_bt.width
    xs = 960 - total / 2
    CY = 470
    cx_ai = xs + lg_ai.width / 2
    cx_vs = xs + lg_ai.width + gap + lg_vs.width / 2
    cx_bt = xs + lg_ai.width + gap + lg_vs.width + gap + lg_bt.width / 2
    SUB = "can an AI beat one of the hardest NES games ever made?"

    def frame(t):
        base = background(t)
        d = ImageDraw.Draw(base)
        G = Image.new("RGB", (W, H), (0, 0, 0))
        g = ImageDraw.Draw(G)
        hud(d, t, "CLAUDE (CLAUDE CODE) x NES BATTLETOADS (1991)")
        ring(g, t, LAND, 960, CY, r1=1250, life=0.7, col=(255, 230, 150), width=22, squash=0.55)
        ring(g, t, LAND + 0.08, 960, CY, r1=800, life=0.6, col=(160, 255, 110), width=10, squash=0.55)
        debris(g, t, LAND, 960, CY, n=56, seed=8, spd=1300, life=1.7,
               box=(xs, CY - 70, xs + total, CY + 70))
        sparks(g, t, LAND, 960, CY, n=70, seed=2, cols=(GOLD, WHITE, ORANGE), spd=1600, life=0.8)
        ks = prog(t, T_SUB, 0.45)
        if ks > 0:
            f = mono(40, True)
            yy = 640 + (1 - eout(ks)) * 22
            d.text((960, yy), SUB, font=f, fill=fade(WHITE, ks), anchor="mm")
            wl = (tw(d, SUB, f) + 40) * eout(ks)
            g.line((960 - wl / 2, 690, 960 + wl / 2, 690), fill=glowc(TOAD, ks), width=3)
        base = add_glow(base, G)
        k = prog(t, T0, 0.18)
        if k > 0:
            sc = 3.2 - 2.2 * ease(k)
            a = min(1, k * 2)
            # everything scales about the centre of the whole title
            for lg, cx, glow in ((lg_ai, cx_ai, (40, 110, 20)), (lg_vs, cx_vs, None), (lg_bt, cx_bt, (120, 70, 0))):
                put_logo(base, lg, 960 + (cx - 960) * sc, CY, scale=sc, alpha=a, glow=glow, glow_k=0.85)
        return post(base, t)

    cues = [(0.0, "riser"), (T0, "whoosh"), (LAND, "slam"), (T_SUB, "blip")]
    return render(out_path, dur, frame, cues)


ALL = {"progression": progression, "level_losses": level_losses, "numbers": numbers, "token_phases": token_phases,
       "rules": rules, "tas": tas, "record_card": record_card, "title_card": title_card}

if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--stills":      # --stills OUTDIR name t1,t2,...
        STILLS = (args[1], [float(x) for x in args[3].split(",")])
        ALL[args[2]](CLIPS / f"{args[2]}.mp4")
        sys.exit(0)
    names = args or list(ALL)
    for nm in names:
        ALL[nm](CLIPS / f"{nm}.mp4")
