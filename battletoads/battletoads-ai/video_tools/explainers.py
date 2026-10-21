"""Animated technical explainers for the Battletoads video (1920x1080 at the NES frame rate).

    ramvision     14 s  READING THE GAME'S MIND: Level 1 footage + the 2 KB of RAM as a live 32x64 grid, key bytes found
    bike_skip     20 s  THE TURBO TUNNEL SKIP: footage + a zero-page / page-3 hex view driven by the real $B7/$B8 pointer
    rng_chaos     10 s  CHAOS: RNG bytes $25-$28 flickering; first run vs final run at the same moment of Level 8
    integrity      8 s  terminal: two replays, same RAM sha1, MATCH; the banned Up+Down found and removed
    architecture  12 s  how it works: Claude -> search programs -> 1/4/16 emulators -> best inputs -> input file -> playback

Every clip is `def name(out_path, dur=..., stills=None)`; `stills` (frame indices) writes PNGs instead of a video.
A cue list for the sound designer goes next to each clip as <name>.sfx.json.

Facts used (verified from logs/cap14.ram, row r = RAM after input line r+1; video frame = lead + r - 1, see shots.py):
  bike skip   r 4222 the toad's height goes negative in the gap (dies), $E5/$E6 = $0000 the whole time
              r 4315 respawn, lives 3 -> 2, reader $B7/$B8 = $000B (was $EE04, level data in ROM)
              r 4319 timer $0B restarts at $00; r 4574 $0B = $FF, $0C/$0D = $7F $03 -> r 4575 reader in page 3 ($038A)
              r 4575-4597 reader walks 11 bytes/frame ($038A ... $0403), spawning junk objects $12 (r 4577) and $19 (r 4583)
              r 4597-4602 $0403 (slot 6 x) counts $52 $5B $64 $6D $76 $7F; at r 4602 it is $7F with trigger $0000
              r 4603 object $7F in slot 7 (input 4,604); r 4731 level byte -> $FE (128 frames later); Level 4 at r 4752
  RNG         Level 8 starts at cap14 r 12457 / capwip r 29634; with a 6-frame offset the toad path is identical for
              2,631 frames while the RNG bytes match on 0.6 % of frames; at +1460..+1570 a yellow object ($51) heads
              right in the final run and left in the first run.
  integrity   input 4,731 of up14 = input 594 of segment L3skipu, originally 'Down+Up', now empty.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageChops  # noqa: E402

from fx import *  # noqa: F401,F403,E402

STILLS = Path(r"stills"
              r"\scratchpad\explainers")
LEAD = {"cap14": 6, "capwip": 9}              # capture frames before input 1 (lead_in(): 6 and 9)
SRC = {"cap14": VIDEO / "up14.mkv", "capwip": VIDEO / "fullrun_wip.mkv"}
_CAPS = {}


def cap(name):
    if name not in _CAPS:
        _CAPS[name] = Cap(name)
    return _CAPS[name]


def vframe(name, row):
    """capture frame that shows RAM/OAM row `row` (shots.py DATA_SHIFT = 1)"""
    return LEAD[name] + row - 1


class Footage:
    """sequential reader: get(row) for non-decreasing rows"""

    def __init__(self, name, r0, r1):
        self.gen = nes_frames(SRC[name], vframe(name, r0), r1 - r0 + 1)
        self.cur, self.im = r0 - 1, None

    def get(self, r):
        while self.cur < r:
            try:
                self.im = next(self.gen)
            except StopIteration:
                break
            self.cur += 1
        return self.im


class Sink:
    """video writer, or (stills mode) PNGs of chosen frame indices"""

    def __init__(self, path, stills=None):
        self.path = Path(path)
        self.stills = sorted(stills) if stills else None
        self.w = None if self.stills else Writer(self.path)

    def want(self, i):
        return self.stills is None or i in self.stills

    def stop(self, i):
        return self.stills is not None and i > self.stills[-1]

    def put(self, i, im):
        if self.w:
            self.w.put(im)
        elif i in self.stills:
            STILLS.mkdir(parents=True, exist_ok=True)
            im.save(STILLS / f"{self.path.stem}_{i:04d}.png")

    def close(self):
        if self.w:
            self.w.close()


def write_cues(out_path, cues):
    p = Path(out_path).with_suffix(".sfx.json")
    cues = sorted(({"t": round(float(t), 3), "sfx": s} for t, s in cues), key=lambda c: c["t"])
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(cues, indent=1), encoding="utf-8")
    tmp.replace(p)


# ------------------------------------------------------------------------------------------------ drawing helpers
_FC = {}


def F(size, kind="mono"):
    size = max(6, int(size))
    key = (size, kind)
    if key not in _FC:
        _FC[key] = {"mono": lambda: mono(size), "monob": lambda: mono(size, True),
                    "ui": lambda: font("arialbd.ttf", size), "uil": lambda: font("arial.ttf", size)}[kind]()
    return _FC[key]


def txt(d, xy, s, size=24, kind="mono", fill=TEXT, anchor="la", shadow=2):
    f = F(size, kind)
    if shadow:
        sc = (0, 0, 0, fill[3]) if len(fill) == 4 else (0, 0, 0)
        d.text((xy[0] + shadow, xy[1] + shadow), s, font=f, fill=sc, anchor=anchor)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def tw(s, size, kind="mono"):
    l, t, r, b = F(size, kind).getbbox(s)
    return r - l


def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def A(col, a):
    return tuple(col[:3]) + (int(max(0, min(255, a))),)


def clamp01(x):
    return max(0.0, min(1.0, x))


_BG = {}


def background(t):
    """near-black green with a faint drifting grid"""
    if "g" not in _BG:
        g = Image.new("RGB", (W + 120, H + 120), BG)
        d = ImageDraw.Draw(g)
        for x in range(0, W + 120, 60):
            d.line((x, 0, x, H + 120), fill=(15, 23, 18))
        for y in range(0, H + 120, 60):
            d.line((0, y, W + 120, y), fill=(15, 23, 18))
        for x in range(0, W + 120, 60):
            for y in range(0, H + 120, 60):
                d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=(30, 46, 36))
        _BG["g"] = g
    o = int(t * 12) % 60
    return _BG["g"].crop((o, o, o + W, o + H))


def add_glow(base, layer, radius=10, gain=1.4):
    """additive bloom of an RGBA layer, then the layer itself on top"""
    small = layer.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(max(1.0, radius / 4)))
    a = np.asarray(small, dtype=np.float32)
    rgb = a[..., :3] * (a[..., 3:4] / 255.0) * gain
    g = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    out = ImageChops.add(base, g)
    out.paste(layer, (0, 0), layer)
    return out


def compose(base, gl, ov, vig=0.32):
    """plain overlay first, the glowing layer on top"""
    base = base.copy()
    base.paste(ov, (0, 0), ov)
    return vignette(add_glow(base, gl), vig)


def layers():
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return gl, ImageDraw.Draw(gl), ov, ImageDraw.Draw(ov)


def header(im, text, t, t0=1.35, size=60, y=62):
    """small logo header that slides in from the left after the intro slam"""
    if t < t0:
        return
    lg = logo(text, size)
    k = ease_out_back(clamp01((t - t0) / 0.5))
    x = int(80 - (1 - k) * (lg.width + 160))
    im.paste(lg, (x, y), lg)


def intro(im, text, t, dur=1.4, sub=None, size=140):
    if t >= dur:
        return im
    return slam(darken(im, 0.45), text, t, dur, sub=sub, size=size)


def polyline_partial(d, pts, p, fill, width):
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(math.dist(a, b) for a, b in segs)
    rem = L * clamp01(p)
    out = [pts[0]]
    for a, b in segs:
        l = math.dist(a, b)
        if rem <= 0:
            break
        if rem >= l:
            out.append(b); rem -= l
        else:
            k = rem / l
            out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)); rem = 0
    if len(out) > 1:
        d.line(out, fill=fill, width=width, joint="curve")
    return out[-1]


def point_on(pts, s):
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    L = sum(math.dist(a, b) for a, b in segs)
    rem = L * (s % 1.0)
    for a, b in segs:
        l = math.dist(a, b)
        if rem <= l:
            k = rem / max(l, 1e-6)
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        rem -= l
    return pts[-1]


def arrowhead(d, p_from, p_to, col, size=16):
    ang = math.atan2(p_to[1] - p_from[1], p_to[0] - p_from[0])
    x, y = p_to
    pts = [(x, y), (x - size * math.cos(ang - 0.45), y - size * math.sin(ang - 0.45)),
           (x - size * math.cos(ang + 0.45), y - size * math.sin(ang + 0.45))]
    d.polygon(pts, fill=col)


def flow(d, pts, t, col, n=3, speed=0.6, r=5):
    for j in range(n):
        x, y = point_on(pts, t * speed + j / n)
        d.ellipse((x - r, y - r, x + r, y + r), fill=col)


def check(d, x, y, size, col, width=5):
    """a drawn check mark (Consolas has no U+2713); (x, y) = left end, vertically centred"""
    d.line([(x, y), (x + size * 0.38, y + size * 0.36), (x + size, y - size * 0.45)], fill=col, width=width, joint="curve")


def panel(d, box, outline=TOAD, fill=(12, 20, 15, 235), width=3, radius=14):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pop_scale(t, t0, d=0.45):
    return ease_out_back(clamp01((t - t0) / d)) if t >= t0 else 0.0


def scaled_box(box, s):
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    w, h = (box[2] - box[0]) * s / 2, (box[3] - box[1]) * s / 2
    return cx - w, cy - h, cx + w, cy + h


def nes_panel(im, nes, x, y, scale, border=TOAD, d=None):
    w, h = int(256 * scale), int(224 * scale)
    im.paste(scanlines_small(nes.resize((w, h), Image.NEAREST)), (int(x), int(y)))
    if d is not None:
        d.rectangle((x - 4, y - 4, x + w + 3, y + h + 3), outline=border, width=3)


def scanlines_small(im, alpha=0.12):
    a = np.asarray(im, dtype=np.uint8).copy()
    a[::4] = (a[::4].astype(np.float32) * (1 - alpha)).astype(np.uint8)
    return Image.fromarray(a)


# ================================================================================================ 1. RAM VISION
def ramvision(out_path, dur=14.0, stills=None):
    c = cap("cap14")
    N = nframes(dur)
    R0, R1 = 1925, 2288                          # Level 1: the drop-in -> both pigs -> into the warp portal
    rows = [R0 + int(round(i * (R1 - R0) / (N - 1))) for i in range(N)]
    speed = (R1 - R0) / (N - 1)
    foot = Footage("cap14", R0, R1)
    FX, FY, FS = 80, 250, 3
    GX, GY, P, CS = 1010, 262, 11, 9             # grid: 32 columns x 64 rows, 11 px pitch
    CX, CW, CH, CP = 1440, 400, 86, 101          # cards
    sgn = lambda v: v - 256 if v > 127 else v
    items = [
        ("FRAME COUNTER", [0x0B], CYAN, lambda r: c.r(r, 0x0B), "counts up once per frame"),
        ("LEVEL", [0x10], GOLD, lambda r: c.r(r, 0x10), "changes only between levels"),
        ("LIVES", [0x11], ORANGE, lambda r: c.r(r, 0x11), "drops by one on every death"),
        ("CAMERA X", [0x87, 0x88], CYAN, lambda r: c.r(r, 0x87) + 256 * c.r(r, 0x88), "moves when the screen scrolls"),
        ("TOAD X", [0x3FD, 0x3EE], TOAD, lambda r: c.r(r, 0x3FD) + 256 * sgn(c.r(r, 0x3EE)), "follows the toad left / right"),
        ("HEIGHT", [0x439, 0x42A], TOAD, lambda r: c.r(r, 0x439) + 256 * sgn(c.r(r, 0x42A)), "falls as the toad drops in"),
        ("HEALTH", [0x51A], RED, lambda r: c.r(r, 0x51A), "drops when the toad is hit"),
    ]
    T0, DT, SCAN = 2.0, 1.35, 0.7
    tk = [T0 + DT * k for k in range(len(items))]
    cues = [(0.0, "whoosh"), (0.18, "slam")]
    for k in range(len(items)):
        cues += [(tk[k] - SCAN, "tick"), (tk[k] - SCAN / 2, "tick"), (tk[k], "ding"), (tk[k] + 0.18, "blip")]
    write_cues(out_path, cues)

    def cell(a):
        rr, cc = divmod(a, 32)
        return GX + cc * P, GY + rr * P, GX + cc * P + CS, GY + rr * P + CS

    lo, hi, zero = np.array([26, 58, 38], np.float32), np.array([150, 240, 95], np.float32), np.array([17, 27, 21], np.float32)
    flashc = np.array([255, 238, 160], np.float32)
    gapc = np.array([9, 14, 11], np.uint8)
    gy_mask = (np.arange(64 * P) % P) >= CS
    gx_mask = (np.arange(32 * P) % P) >= CS
    heat = np.zeros((64, 32), np.float32)
    vheat = [0.0] * len(items)
    lastv = [None] * len(items)
    prev_r, nchanged = None, 0
    sink = Sink(out_path, stills)
    for i in range(N):
        if sink.stop(i):
            break
        t = i / NES_FPS
        r = rows[i]
        if prev_r is not None and r != prev_r:
            ch = np.asarray(c.ram[r]) != np.asarray(c.ram[prev_r])
            heat[ch.reshape(64, 32)] = 1.0
            nchanged = int(ch.sum())
        prev_r = r
        for k, it in enumerate(items):
            v = it[3](r)
            if lastv[k] is not None and v != lastv[k]:
                vheat[k] = 1.0
            lastv[k] = v
        if not sink.want(i):
            heat *= 0.78
            vheat = [h * 0.8 for h in vheat]
            continue
        im = background(t)
        gl, dg, ov, do = layers()
        # ---- footage
        nes = foot.get(r)
        nes_panel(im, nes, FX, FY, FS, d=dg)
        txt(do, (FX, 192), "THE GAME", 24, "ui", DIM)
        # toad marker once TOAD X has been found
        if t >= tk[4] + 0.2:
            tb = toad_box(c, r)
            if tb:
                bx = (FX + tb[0] * FS - 6, FY + tb[1] * FS - 6, FX + tb[2] * FS + 6, FY + tb[3] * FS + 6)
                g = (1 - pop_scale(t, tk[4] + 0.2, 0.4)) * 40
                brackets(dg, bx, TOAD, 4, grow=g)
                lab = f"X {items[4][3](r)}" + (f"  H {items[5][3](r)}" if t >= tk[5] + 0.2 else "")
                chip(do, bx[0], bx[1] - 6, lab, TOAD, 22)
        cy = FY + 224 * FS + 18
        x1 = chip(do, FX, cy, f"FRAME {r + 1:,}", (24, 34, 28), 22, fg=TEXT, anchor="lt")[2]
        x2 = chip(do, x1 + 12, cy, f"\u00d7{speed:.2f} SPEED", (24, 34, 28), 22, fg=DIM, anchor="lt")[2]
        chip(do, x2 + 12, cy, f"{nchanged} BYTES CHANGED", GOLD if nchanged > 120 else (60, 52, 20), 22,
             fg=(10, 10, 10) if nchanged > 120 else GOLD, anchor="lt")
        # ---- the grid
        v = np.asarray(c.ram[r]).reshape(64, 32).astype(np.float32) / 255.0
        col = np.where((v > 0)[..., None], lo + (hi - lo) * np.sqrt(v)[..., None], zero)
        h = heat[..., None]
        col = col * (1 - h) + flashc * h
        big = np.repeat(np.repeat(col.astype(np.uint8), P, 0), P, 1)
        big[gy_mask] = gapc
        big[:, gx_mask] = gapc
        im.paste(Image.fromarray(big), (GX, GY))
        dg.rectangle((GX - 5, GY - 5, GX + 32 * P + 3, GY + 64 * P + 3), outline=A(TOAD, 120), width=2)
        txt(do, (GX - 70, 192), "ITS MEMORY: 2,048 BYTES, 1 CELL = 1 BYTE", 24, "ui", DIM)
        for pg in range(8):
            txt(do, (GX - 14, GY + pg * 8 * P + 2), f"${pg:01X}00", 18, "mono", DIM, anchor="ra")
        # ---- discoveries
        for k, (name, addrs, colr, fn, query) in enumerate(items):
            tl = tk[k]
            row0 = addrs[0] // 32
            if tl - SCAN <= t < tl:                         # scanning cursor converging on the byte
                p = (t - (tl - SCAN)) / SCAN
                rng = random.Random(i * 31 + k)
                spread = (1 - p) ** 1.4
                rr = int(min(63, max(0, row0 + rng.randint(-int(30 * spread), int(30 * spread)))))
                cc = int(min(31, max(0, addrs[0] % 32 + rng.randint(-int(16 * spread), int(16 * spread)))))
                bx = cell(rr * 32 + cc)
                dg.line((GX, (bx[1] + bx[3]) / 2, GX + 32 * P - 2, (bx[1] + bx[3]) / 2), fill=A(GOLD, 70), width=1)
                dg.line(((bx[0] + bx[2]) / 2, GY, (bx[0] + bx[2]) / 2, GY + 64 * P - 2), fill=A(GOLD, 70), width=1)
                dg.rectangle((bx[0] - 3, bx[1] - 3, bx[2] + 2, bx[3] + 2), outline=GOLD, width=2)
            if tl - SCAN <= t < tl + 0.6:
                a = 255 * min(1, (t - (tl - SCAN)) / 0.15, (tl + 0.6 - t) / 0.15)
                txt(do, (GX - 70, GY + 64 * P + 12), f"LOOKING FOR A BYTE THAT {query.upper()}", 20, "monob",
                    A(colr, a), shadow=0)
            if t < tl:
                continue
            # lock-on rings
            s = 1 + 2.2 * (1 - pop_scale(t, tl, 0.35))
            pulse = 0.5 + 0.5 * math.sin(t * 6 + k)
            for a in addrs:
                bx = scaled_box(cell(a), s)
                dg.rectangle((bx[0] - 3, bx[1] - 3, bx[2] + 2, bx[3] + 2), outline=A(colr, 200 + 55 * pulse), width=3)
            # leader line
            cyk = GY + k * CP + CH / 2 + 2
            ex = GX + 32 * P + 16 + 7 * k
            pa = addrs[0]
            b0 = cell(pa)
            if row0 == 0:
                yy = GY - 12 - 7 * k
                pts = [((b0[0] + b0[2]) / 2, b0[1] - 4), ((b0[0] + b0[2]) / 2, yy), (ex, yy), (ex, cyk), (CX, cyk)]
            else:
                ym = (b0[1] + b0[3]) / 2
                pts = [(b0[2] + 4, ym), (ex, ym), (ex, cyk), (CX, cyk)]
            pl = clamp01((t - tl) / 0.35)
            polyline_partial(dg, pts, pl, A(colr, 230), 3)
            if len(addrs) > 1 and row0 != 0:              # second byte joins the same line
                b1 = cell(addrs[1])
                ym = (b1[1] + b1[3]) / 2
                polyline_partial(dg, [(b1[2] + 4, ym), (ex, ym)], pl, A(colr, 150), 2)
            if pl >= 1:
                flow(dg, pts, t, A(WHITE, 200), n=2, speed=0.9, r=3)
            # card
            kc = pop_scale(t, tl + 0.18, 0.5)
            if kc <= 0:
                continue
            x0 = CX + (1 - kc) * 520
            y0 = GY + k * CP
            vh = vheat[k]
            panel(do, (x0, y0, x0 + CW, y0 + CH), outline=mix(colr, WHITE, vh * 0.6), fill=(12, 20, 15, 238), width=3,
                  radius=10)
            do.rectangle((x0 + 3, y0 + 10, x0 + 9, y0 + CH - 10), fill=colr)
            txt(do, (x0 + 24, y0 + 12), name, 27, "ui", colr)
            addr_s = "  ".join(f"${a:04X}" for a in addrs)
            txt(do, (x0 + 24, y0 + 52), addr_s, 20, "mono", DIM)
            val = lastv[k]
            txt(dg, (x0 + CW - 22, y0 + CH / 2 + 2), f"{val:,}", 46, "monob", mix(WHITE, colr, 0.35 + 0.65 * (1 - vh)),
                anchor="rm", shadow=0)
        heat *= 0.78
        vheat = [hh * 0.8 for hh in vheat]
        header(im, "READING THE GAME'S MIND", t)
        out = compose(im, gl, ov)
        out = intro(out, "READING THE GAME'S MIND", t, sub="every byte of memory, every frame", size=110)
        sink.put(i, out)
    sink.close()
    return out_path


# ================================================================================================ 2. BIKE SKIP
def bike_skip(out_path, dur=20.0, stills=None):
    c = cap("cap14")
    N = nframes(dur)
    ptr = lambda r: c.r(r, 0xB7) | (c.r(r, 0xB8) << 8)
    cam = lambda r: c.cam(r)[0]
    # (row_a, row_b, output frames per row; < 1 = rows skipped per frame)
    segs = [(4000, 4195, 1), (4195, 4235, 2), (4235, 4315, 0.5), (4315, 4566, 1), (4566, 4578, 10), (4578, 4596, 4),
            (4596, 4606, 12), (4606, 4762, 1)]
    sched = []
    for a, b, rep in segs:
        if rep >= 1:
            for r in range(a, b):
                for j in range(rep):
                    sched.append((r, j / rep, rep))
        else:
            for r in range(a, b, int(round(1 / rep))):
                sched.append((r, 0.0, rep))
    while len(sched) < N:
        sched.append((4761, 0.0, 0))                 # hold on the Level 4 card (shown for 2 frames only)
    sched = sched[:N]
    first = {}
    for i, (r, fr, rep) in enumerate(sched):
        first.setdefault(r, i)

    def first_at(row):
        return min(i for i, s in enumerate(sched) if s[0] >= row)

    R_DIE, R_RESP, R_JUMP, R_7F, R_END = 4222, 4315, 4574, 4602, 4731
    caps = [(max(first_at(4040), nframes(1.5)), "1. crash before the first checkpoint", TEXT),
            (first_at(R_RESP), "2. respawn: saved list pointer = $0000", TEXT),
            (first_at(4400), "3. the game reads its own variables as level data", TEXT),
            (first_at(R_7F), "4. finds $7F \u2192 level over", TEXT),
            (first_at(R_END), "2.3 minutes of bike course: skipped", GOLD)]
    i7f, iend, ijump = first_at(R_7F), first_at(R_END), first_at(R_JUMP)
    tt = lambda i: i / NES_FPS
    cues = [(0.0, "whoosh"), (0.18, "slam"), (tt(first_at(R_DIE)), "glitch"), (tt(first_at(R_RESP)), "blip"),
            (tt(ijump), "glitch"), (tt(ijump) + 0.5, "whoosh"), (tt(first_at(4596)), "riser"), (tt(i7f), "slam"),
            (tt(iend), "ding"), (tt(iend) + 0.05, "slam")]
    for ci, _, _ in caps:
        cues.append((tt(ci), "tick"))
    for r in range(4576, 4598):
        if ptr(r) != ptr(r - 1):
            cues.append((tt(first[r]), "blip"))
    write_cues(out_path, cues)

    foot = Footage("cap14", 4000, 4761)
    FX, FY, FS = 80, 200, 3
    HX, BX, BP = 930, 1024, 50
    ZY = [222, 254]
    PY0, RP = 318, 32
    PROWS = list(range(0x370, 0x420, 0x10))

    def bxy(a):
        base = a & ~15
        if base in (0x000, 0x010):
            y = ZY[base >> 4]
        elif 0x370 <= base <= 0x410:
            y = PY0 + ((base - 0x370) >> 4) * RP
        else:
            return None
        return BX + (a & 15) * BP, y

    fields = ["ID", "TRIG\nHI", "TRIG\nLO", "", "X\nLO", "X\nHI", "Y", "", "H", "", "FLAGS"]
    spawned = []                                      # (row, id)
    for r in range(4575, 4606):                      # objects the loader itself spawned (entry id == new object)
        for s in range(2, 15):
            nid = c.a(r, "id", s)
            if nid and not c.a(r - 1, "id", s) and ptr(r) != ptr(r - 1) and c.r(r - 1, ptr(r - 1)) == nid:
                spawned.append((r, nid))
    prev_disp = None
    bheat = {}
    sink = Sink(out_path, stills)
    for i in range(N):
        if sink.stop(i):
            break
        t = tt(i)
        r, frac, rep = sched[i]
        rf = r                                        # footage row
        r = min(r, 4603)                              # the diagram freezes once the level-end object exists
        ram = c.ram[r]
        if prev_disp is not None and r != prev_disp:
            pr = c.ram[prev_disp]
            for a in list(range(0, 0x20)) + list(range(0x370, 0x420)):
                if ram[a] != pr[a]:
                    bheat[a] = 1.0
        prev_disp = r
        if not sink.want(i):
            for a in list(bheat):
                bheat[a] *= 0.8
            continue
        im = background(t)
        gl, dg, ov, do = layers()
        # ---------------- footage
        nes = foot.get(rf)
        if rep == 0:
            nes = darken(nes, 0.5)
        shake_k = clamp01((t - tt(i7f)) / 0.5) if i >= i7f else 1.0
        dx = dy = 0
        if shake_k < 1:
            rg = random.Random(i)
            a_ = 16 * (1 - shake_k) ** 2
            dx, dy = int(rg.uniform(-a_, a_)), int(rg.uniform(-a_, a_))
        nes_panel(im, nes, FX + dx, FY + dy, FS, d=dg)
        cy = FY + 224 * FS + 16
        x1 = chip(do, FX, cy, f"INPUT FRAME {rf + 1:,}", (24, 34, 28), 22, fg=TEXT, anchor="lt")[2]
        if rep > 1:
            chip(do, x1 + 12, cy, f"SLOW MOTION \u00d71/{rep}", GOLD, 22, anchor="lt")
        elif rep and rep < 1:
            chip(do, x1 + 12, cy, f"\u00d7{int(round(1 / rep))} SPEED", (60, 52, 20), 22, fg=GOLD, anchor="lt")
        elif rep == 0:
            chip(do, x1 + 12, cy, "LEVEL 4 NEXT", TOAD, 22, anchor="lt")
        lv = c.r(r, 0x11)
        txt(do, (FX + 768, cy + 4), f"LIVES {lv}", 24, "monob", RED if r >= R_RESP else DIM, anchor="ra")
        # ---------------- hex view
        txt(do, (HX, 168), "ZERO PAGE  \u00b7  the game's own variables", 21, "ui", DIM)
        txt(do, (HX, 286), "PAGES 3-4  \u00b7  the object tables (15 slots \u00d7 35 attributes)", 21, "ui", DIM)
        for j in range(16):
            txt(do, (BX + j * BP + 13, ZY[0] - 22), f"{j:X}", 15, "mono", (70, 90, 78), anchor="ma", shadow=0)
        # window position
        win = None
        p_now = ptr(r)
        if R_RESP <= r <= R_7F and p_now < 0x800:
            if r == R_JUMP:
                win = 0x00B if frac < 0.55 else 0x37F
            else:
                prev_p = 0x37F if r == R_JUMP + 1 else ptr(r - 1)
                if rep >= 4 and prev_p != p_now and frac < 0.45 and prev_p < 0x800 and r > R_RESP:
                    k = ease(frac / 0.45)
                    win = int(round(prev_p + (p_now - prev_p) * k))
                else:
                    win = p_now
        wset = set(range(win, win + 11)) if win is not None else set()
        pop = pop_scale(t, tt(first_at(R_RESP)), 0.4) if r >= R_RESP else 0
        for base in [0x000, 0x010] + PROWS:
            y = bxy(base)[1]
            txt(do, (HX, y + 2), f"${base:04X}", 22, "mono", DIM)
            runs = []
            for j in range(16):
                a = base + j
                x = BX + j * BP
                v = int(ram[a])
                hh = bheat.get(a, 0)
                colr = (175, 196, 182) if v else (68, 84, 74)
                if a == 0x0B:
                    colr = CYAN
                if a in wset:
                    off = a - win
                    if off == 0:
                        fillc, colr = (GOLD if not (r >= R_7F and win == 0x403) else RED), (12, 12, 12)
                    elif off in (1, 2):
                        fillc, colr = (150, 85, 20), WHITE
                    else:
                        fillc, colr = (58, 52, 18), (250, 225, 140)
                    bx = scaled_box((x - 5, y - 3, x + 35, y + 29), 1 + 0.6 * (1 - pop) if r < R_RESP + 6 else 1)
                    do.rounded_rectangle(bx, radius=5, fill=fillc)
                    if runs and runs[-1][1] == j - 1:
                        runs[-1][1] = j
                    else:
                        runs.append([j, j])
                if a not in wset:
                    colr = mix(colr, WHITE, hh * 0.8)
                txt(do, (x + 15, y + 1), f"{v:02X}", 26, "monob", colr, anchor="ma", shadow=0)
            for j0, j1 in runs:
                dg.rounded_rectangle((BX + j0 * BP - 9, y - 7, BX + j1 * BP + 39, y + 33), radius=8, outline=GOLD, width=3)
        # the timer tag and its outline
        x0b, y0b = bxy(0x0B)
        dg.rounded_rectangle((x0b - 8, y0b - 6, x0b + 38, y0b + 32), radius=6, outline=A(CYAN, 220), width=2)
        txt(do, (x0b + 15, ZY[0] - 44), "TIMER", 16, "monob", CYAN, anchor="ma", shadow=0)
        # separator between zero page and page 3
        do.line((HX, 280, BX + 16 * BP, 280), fill=(30, 44, 36), width=2)
        # jump arrow
        if ijump <= i < ijump + 40:
            k = clamp01((i - ijump) / 6)
            sx, sy = bxy(0x0C)
            ex_, ey_ = bxy(0x37F)
            fade = 1 - clamp01((i - ijump - 26) / 14)
            for a in (0x0C, 0x0D):                    # the two bytes that hold the jump target
                xa, ya = bxy(a)
                dg.rounded_rectangle((xa - 8, ya - 6, xa + 38, ya + 32), radius=6, outline=A(CYAN, 255 * fade), width=3)
            p0, p3 = (sx + 40, sy + 34), (ex_ + 15, ey_ - 8)
            c1, c2 = (p0[0] + 10, p0[1] + 45), (p3[0] - 70, p3[1] - 4)
            pts = []
            for q in range(31):
                u = q / 30
                pts.append(tuple((1 - u) ** 3 * p0[z] + 3 * (1 - u) ** 2 * u * c1[z] + 3 * (1 - u) * u * u * c2[z]
                                 + u ** 3 * p3[z] for z in (0, 1)))
            polyline_partial(dg, pts, k, A(CYAN, 255 * fade), 5)
            if k > 0.97:
                arrowhead(dg, pts[-4], pts[-1], A(CYAN, 255 * fade), 20)
                dg.rounded_rectangle((ex_ - 8, ey_ - 6, ex_ + 38, ey_ + 32), radius=6, outline=A(CYAN, 255 * fade), width=3)
        # the $7F ring
        if r == R_7F:
            x7, y7 = bxy(0x403)
            pulse = 0.5 + 0.5 * math.sin(t * 9)
            g = 18 * (1 - pop_scale(t, tt(i7f), 0.35))
            dg.rounded_rectangle((x7 - 10 - g, y7 - 8 - g, x7 + 40 + g, y7 + 34 + g), radius=8, outline=A(RED, 170 + 85 * pulse),
                                 width=4)
        if r >= R_7F + 1:
            x8, y8 = bxy(0x3C8)
            pulse = 0.5 + 0.5 * math.sin(t * 9)
            g = 18 * (1 - pop_scale(t, tt(first[R_7F + 1]), 0.35))
            dg.rounded_rectangle((x8 - 10 - g, y8 - 8 - g, x8 + 40 + g, y8 + 34 + g), radius=8,
                                 outline=A(RED, 170 + 85 * pulse), width=4)
        # ---------------- decode panel
        DY = 680
        if r < R_RESP:
            txt(do, (HX, DY), f"READER  $B7/$B8 = ${p_now:04X}", 28, "monob", GOLD)
            txt(do, (HX + 470, DY + 4), "(the level's list, in ROM)", 22, "ui", DIM)
        else:
            flashk = 1 - clamp01((i - first_at(R_RESP)) / 30)
            txt(dg, (HX, DY), f"READER  $B7/$B8 = ${p_now:04X}", 28, "monob", mix(GOLD, WHITE, flashk))
            txt(do, (HX + 470, DY + 4), "\u2190 from the empty save ($0000)", 22, "ui", mix(DIM, RED, flashk))
        e5 = c.r(r, 0xE5) | (c.r(r, 0xE6) << 8)
        txt(do, (BX + 16 * BP, DY + 46), f"CHECKPOINT SAVE $E5/$E6 = ${e5:04X}", 20, "mono", RED if r < R_RESP else DIM,
            anchor="ra")
        SY = 758
        wbytes = [int(c.ram[r, win + j]) for j in range(11)] if win is not None else [None] * 11
        for j in range(11):
            x = BX + j * 74
            v = wbytes[j]
            on = v is not None
            fc = (GOLD if j == 0 else (150, 85, 20) if j in (1, 2) else (40, 40, 22)) if on else (22, 30, 25)
            if on and j == 0 and win == 0x403 and r >= R_7F:
                fc = RED
            do.rounded_rectangle((x, SY, x + 66, SY + 42), radius=6, fill=fc, outline=(0, 0, 0), width=2)
            if on:
                txt(do, (x + 33, SY + 7), f"{v:02X}", 26, "monob", (12, 12, 12) if j == 0 else WHITE, anchor="ma", shadow=0)
            if fields[j]:
                txt(do, (x + 33, SY + 46), fields[j].replace("\n", " "), 14, "mono", DIM, anchor="ma", shadow=0)
        txt(do, (BX - 14, SY + 8), "ENTRY", 18, "monob", DIM, anchor="ra", shadow=0)
        # verdict
        VY = 828
        if r < R_RESP:
            verdict, vc = ("toad dies in the gap: no checkpoint saved yet" if r >= R_DIE else "mounting the bike, rolling back"), (RED if r >= R_DIE else DIM)
        else:
            b = wbytes if wbytes[0] is not None else [0] * 11
            trig = b[1] * 256 + b[2]
            cx = cam(r)
            nxt = ptr(r + 1)
            if r == R_JUMP:
                verdict, vc = "ID $FF = JUMP \u2192 next two bytes $7F $03 = address $037F", CYAN
            elif win == 0x403 and r == R_7F:
                verdict, vc = "ID $7F, TRIGGER $0000 \u2264 CAMERA \u2192 SPAWN OBJECT $7F", RED
            elif r > R_7F:
                verdict, vc = "slot 7's id ($03C8) = $7F: the level-end fireworks", RED
            elif win != p_now:
                verdict, vc = "next entry, 11 bytes on", GOLD
            elif nxt != p_now:
                if b[0]:
                    verdict, vc = f"CAMERA ${cx:04X} \u2265 TRIGGER ${trig:04X} \u2192 SPAWN ${b[0]:02X}", TOAD
                else:
                    verdict, vc = f"CAMERA ${cx:04X} \u2265 TRIGGER ${trig:04X} \u2192 ID $00, next", TOAD
            else:
                verdict, vc = f"TRIGGER ${trig:04X} > CAMERA ${cx:04X} \u2192 WAIT", DIM
                if win == 0x00B:
                    verdict = f"ID = TIMER ${b[0]:02X}   TRIGGER ${trig:04X} > CAMERA ${cx:04X} \u2192 WAIT"
        txt(do, (HX, VY), verdict, 22, "monob", vc)
        sp = [s_ for s_ in spawned if s_[0] <= r]
        if sp:
            xx = HX + tw("SPAWNED ", 18, "mono") + 4
            txt(do, (HX, DY + 46), "SPAWNED", 18, "mono", DIM, shadow=0)
            for (sr, sid) in sp:
                lab = f"${sid:02X}"
                kk = pop_scale(t, tt(first[sr]), 0.3)
                bx = chip(do, xx, DY + 40 + (1 - kk) * 20, lab, RED if sid == 0x7F else (60, 52, 20), 18,
                          fg=WHITE if sid == 0x7F else GOLD, anchor="lt")
                xx = bx[2] + 8
        # ---------------- captions
        for k, (ci, line, colr) in enumerate(caps):
            if i < ci:
                continue
            kk = pop_scale(t, tt(ci), 0.45)
            y = 870 + k * 26
            active = (k == len([1 for cc in caps if i >= cc[0]]) - 1)
            last = (k == 4)
            size = 25 if last else 22
            cc = colr if (active or last) else (150, 165, 155)
            x = HX + (1 - kk) * 300
            if active and not last:
                do.polygon([(x - 18, y + 4), (x - 18, y + 20), (x - 6, y + 12)], fill=GOLD)
            txt(dg if (active or last) else do, (x, y), line, size, "ui", A(cc, 255 * min(1, kk * 1.5)))
        # ---------------- big callouts on the footage
        if i >= i7f and t < tt(i7f) + 2.8:
            u = t - tt(i7f)
            lg = logo("$7F = LEVEL END", 70, top=(255, 160, 130), bottom=(225, 30, 25), extrude=(90, 10, 10))
            sc = 2.4 - 1.4 * ease(u / 0.18) if u < 0.18 else 1.0
            al = min(1, u / 0.1, (2.8 - u) / 0.3)
            g = lg.resize((int(lg.width * sc), int(lg.height * sc)), Image.BILINEAR) if sc != 1 else lg
            if al < 1:
                g = g.copy(); g.putalpha(g.split()[3].point(lambda p_: int(p_ * al)))
            ov.paste(g, (int(FX + 384 - g.width / 2), int(FY + 470 - g.height / 2)), g)
        if i >= iend:
            u = t - tt(iend)
            lg = logo("2.3 MIN SKIPPED", 66)
            sc = 2.4 - 1.4 * ease(u / 0.18) if u < 0.18 else 1.0 + 0.02 * math.sin(u * 3)
            g = lg.resize((int(lg.width * sc), int(lg.height * sc)), Image.BILINEAR)
            ov.paste(g, (int(FX + 384 - g.width / 2), int(FY + 336 - g.height / 2)), g)
        for a in list(bheat):
            bheat[a] *= 0.8
        header(im, "THE TURBO TUNNEL SKIP", t)
        out = compose(im, gl, ov)
        if i >= i7f and t < tt(i7f) + 0.12:
            out = flash(out, (t - tt(i7f)) / 0.12, (255, 230, 220))
        out = intro(out, "THE TURBO TUNNEL SKIP", t, sub="Level 3: crash, respawn, level over", size=120)
        sink.put(i, out)
    sink.close()
    return out_path


# ================================================================================================ 3. RNG CHAOS
def rng_chaos(out_path, dur=10.0, stills=None):
    a14, aw = cap("cap14"), cap("capwip")
    L8_14, L8_W = 12457, 29634 + 6                 # Level 8 entry; +6 aligns the two runs (identical toad path)
    N = nframes(dur)
    I2 = nframes(3.3)                              # panels begin
    K0 = 1400
    # frames into Level 8 shown at output frame i: real time for the flicker, half speed once the runs are side by side
    kof = lambda i: K0 + (i - I2) if i < I2 else K0 + (i - I2) // 2
    f14 = Footage("cap14", L8_14 + kof(I2), L8_14 + kof(N) + 2)
    fw = Footage("capwip", L8_W + kof(I2), L8_W + kof(N) + 2)
    T_TR, T_TR1 = 3.3, 4.1
    PS = 2.25
    PW, PH = int(256 * PS), int(224 * PS)
    LX, RX, PY = 344, 1000, 300
    BOXY, BW, BH, BPITCH = 820, 130, 62, 144
    t_div = (I2 + 2 * (1460 - K0)) / NES_FPS
    cues = [(0.0, "whoosh"), (0.18, "slam"), (1.5, "glitch"), (2.4, "glitch"), (T_TR, "whoosh"), (T_TR1, "blip"),
            (t_div, "ding"), (5.0, "tick")]
    write_cues(out_path, cues)
    rheat = np.zeros(4)
    prev = None
    sink = Sink(out_path, stills)
    for i in range(N):
        if sink.stop(i):
            break
        t = i / NES_FPS
        k = kof(i)
        r14, rw = L8_14 + k, L8_W + k
        v14 = [a14.r(r14, 0x25 + j) for j in range(4)]
        vw = [aw.r(rw, 0x25 + j) for j in range(4)]
        if prev is not None:
            rheat[np.array(v14) != np.array(prev)] = 1.0
        prev = v14
        if not sink.want(i):
            rheat *= 0.7
            continue
        im = background(t)
        gl, dg, ov, do = layers()
        p = ease(clamp01((t - T_TR) / (T_TR1 - T_TR)))
        # ---- panels
        if t >= T_TR:
            ks = pop_scale(t, T_TR + 0.15, 0.6)
            yoff = (1 - ks) * 700
            for (fo, cp_, r_, x, lab, sub, colr) in ((fw, aw, rw, LX, "FIRST RUN", "18:04, the first finished run", CYAN),
                                                     (f14, a14, r14, RX, "FINAL RUN", "12:23, the record", GOLD)):
                nes = fo.get(r_)
                y = PY + yoff
                nes_panel(im, nes, x, y, PS, border=colr, d=dg)
                txt(do, (x, y - 50), lab, 34, "ui", colr)
                txt(do, (x + PW, y - 42), sub, 22, "ui", DIM, anchor="ra")
                for box, o in objects_on_screen(cp_, r_):
                    if box[3] > 226 or box[1] < 10:
                        continue
                    bx = (x + box[0] * PS - 4, y + box[1] * PS - 4, x + box[2] * PS + 4, y + box[3] * PS + 4)
                    if o and o["slot"] == 0:
                        brackets(dg, bx, TOAD, 3)
                        chip(do, bx[0], bx[1] - 4, f"TOAD x{o['x']}", TOAD, 18)
                    elif o and o["id"] == 0x51:
                        dx_ = o["x"] - cp_.obj(r_ - 6, o["slot"])["x"]
                        brackets(dg, bx, RED, 4)
                        if dx_:
                            chip(do, bx[0], bx[3] + 4, ("\u2192 x" if dx_ > 0 else "\u2190 x") + str(o["x"]), RED, 18,
                                 fg=WHITE, anchor="lt")
        # ---- RNG rows: the big flicker (phase 1) morphs into the right panel's row
        for side in (0, 1) if t >= T_TR else (1,):
            vals = v14 if side == 1 else vw
            other = vw if side == 1 else v14
            for j in range(4):
                bx_big = (315 + j * 330, 430, 315 + j * 330 + 300, 650)
                x0 = (RX if side else LX) + j * BPITCH
                bx_small = (x0, BOXY, x0 + BW, BOXY + BH)
                if side == 1:
                    bx = tuple(bx_big[q] + (bx_small[q] - bx_big[q]) * p for q in range(4))
                else:
                    s = pop_scale(t, T_TR1 - 0.2, 0.4)
                    bx = scaled_box(bx_small, max(0.01, s))
                    if s <= 0.01:
                        continue
                h = bx[3] - bx[1]
                colr = GOLD if side else CYAN
                diff = t >= T_TR1 and vals[j] != other[j]
                hh = rheat[j] if side else 0.0
                do.rounded_rectangle(bx, radius=max(4, int(h * 0.1)), fill=(14, 22, 17, 240),
                                     outline=RED if diff else mix(colr, WHITE, hh), width=3)
                fs = h * 0.68
                txt(dg, ((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2 + h * 0.06), f"{vals[j]:02X}", fs, "monob",
                    mix(colr, WHITE, hh * 0.7), anchor="mm", shadow=0)
                ls = 26 * (1 - p) + 13 * p
                txt(do, (bx[0] + 8, bx[1] + 4), f"${0x25 + j:02X}", ls, "mono", DIM, shadow=0)
        if t >= T_TR1:
            al = 255 * clamp01((t - T_TR1) / 0.3)
            txt(dg, (960, BOXY + BH / 2), "\u2260", 54, "monob", A(RED, al), anchor="mm", shadow=0)
        # ---- phase-1 words
        if t < T_TR1:
            al = 255 * (1 - clamp01((t - T_TR) / 0.2)) * clamp01((t - 1.2) / 0.3)
            txt(do, (960, 340), "THE RANDOM NUMBER GENERATOR  \u00b7  RAM $25-$28", 40, "ui", A(WHITE, al), anchor="mm")
            txt(do, (960, 720), "mixed every frame \u2022 $28 also counts the CPU's idle loops", 30, "ui", A(DIM, al),
                anchor="mm")
            txt(do, (960, 770), "every enemy decision reads these four bytes", 30, "ui", A(GOLD, al), anchor="mm")
        # ---- bottom lines
        if t >= 4.4:
            kk = pop_scale(t, 4.4, 0.4)
            ch_ = "SAME BUTTONS IN BOTH RUNS HERE \u2014 DIFFERENT DICE"
            wch = tw(ch_, 22, "monob") + 16
            chip(do, 960 - wch / 2, 900 + (1 - kk) * 40, ch_, (40, 34, 14), 22, fg=GOLD, anchor="lt")
        if t >= 5.0:
            kk = pop_scale(t, 5.0, 0.5)
            line = "one different button press early \u2192 every random number after it changes"
            txt(dg, (960 + (1 - kk) * 200, 968), line, 34, "ui", A(WHITE, 255 * min(1, kk * 1.4)), anchor="mm")
        rheat *= 0.7
        header(im, "CHAOS", t)
        if t >= 1.35:
            txt(do, (80 + logo("CHAOS", 60).width + 24, 104), "LEVEL 8 \u00b7 INTRUDER EXCLUDER" +
                ("  \u00b7  HALF SPEED" if t >= T_TR else ""), 24, "ui", DIM, anchor="lm")
        out = compose(im, gl, ov)
        out = intro(out, "CHAOS", t, sub="where the random numbers come from", size=170)
        sink.put(i, out)
    sink.close()
    return out_path


# ================================================================================================ 4. INTEGRITY
SHA = "e2a1d2dc9d5933e2b18bba0b0d5021ad617dac52"


def integrity(out_path, dur=8.0, stills=None):
    N = nframes(dur)
    lines_in = (LOGS / "up14.inputs.txt").read_text(encoding="utf-8").splitlines()[1:]
    BAN = 4731                                      # 1-based input line = L3skipu input 594 (4137 + 594)
    TX0, TY0, TX1, TY1 = 80, 170, 1840, 1000
    LX, LY, LH = 130, 250, 50
    CWD = tw("0", 30, "monob") + 1
    cues = [(0.05, "tick"), (0.3, "tick"), (0.55, "tick"), (0.8, "blip"), (1.75, "ding"), (2.15, "blip"),
            (2.8, "ding"), (3.3, "whoosh"), (3.48, "slam"), (4.35, "whoosh"), (5.95, "glitch"), (6.4, "tick"),
            (6.9, "blip"), (7.2, "ding")]
    write_cues(out_path, cues)
    rng = random.Random(7)
    sink = Sink(out_path, stills)
    for i in range(N):
        if sink.stop(i):
            break
        if not sink.want(i):
            continue
        t = i / NES_FPS
        im = background(t)
        gl, dg, ov, do = layers()
        header(im, "PROOF", t, t0=0.0)
        txt(do, (80 + logo("PROOF", 60).width + 24, 104), "same inputs, same game, every time", 26, "ui", DIM, anchor="lm")
        # terminal
        do.rounded_rectangle((TX0, TY0, TX1, TY1), radius=16, fill=(6, 10, 8, 245), outline=(40, 62, 48), width=3)
        do.rounded_rectangle((TX0, TY0, TX1, TY0 + 46), radius=16, fill=(20, 30, 24))
        do.rectangle((TX0 + 3, TY0 + 30, TX1 - 3, TY0 + 46), fill=(20, 30, 24))
        for j, cc in enumerate(((235, 90, 80), (240, 190, 60), (110, 200, 90))):
            do.ellipse((TX0 + 22 + j * 30, TY0 + 14, TX0 + 40 + j * 30, TY0 + 32), fill=cc)
        txt(do, ((TX0 + TX1) / 2, TY0 + 23), "verify \u2014 toads/logs/up14.inputs.txt", 20, "mono", DIM, anchor="mm",
            shadow=0)
        if t < 4.3:
            # ------------------------------------------ phase A: two replays, same hash
            cmd = "python replay.py up14.inputs.txt --from-power-on --sha1-ram"
            n = int(len(cmd) * clamp01((t - 0.1) / 0.6))
            txt(do, (LX, LY), "$", 30, "monob", GOLD, shadow=0)
            txt(do, (LX + 34, LY), cmd[:n] + ("\u2588" if t < 0.8 and int(t * 6) % 2 == 0 else ""), 30, "mono", TEXT, shadow=0)

            def replay_line(y, ta, tb, label):
                if t < ta:
                    return
                k = clamp01((t - ta) / (tb - ta))
                kk = 1 - (1 - k) ** 2
                txt(do, (LX, y), label, 30, "mono", TEXT, shadow=0)
                bx0, bx1 = LX + 250, LX + 850
                do.rectangle((bx0, y + 6, bx1, y + 30), outline=(50, 80, 60), width=2)
                do.rectangle((bx0 + 3, y + 9, bx0 + 3 + (bx1 - bx0 - 6) * kk, y + 27), fill=TOAD)
                txt(do, (bx1 + 24, y), f"{int(46751 * kk):>6,} / 46,751 frames", 30, "mono", TOAD if k >= 1 else TEXT, shadow=0)

            def sha_line(y, ta, tb, ok_t):
                if t < ta:
                    return
                k = clamp01((t - ta) / (tb - ta))
                n = int(40 * k)
                s = SHA[:n] + "".join(rng.choice("0123456789abcdef") for _ in range(40 - n)) if k < 1 else SHA
                txt(do, (LX, y), "RAM sha1", 30, "mono", DIM, shadow=0)
                for q, ch in enumerate(s):
                    green = t >= ok_t + q * 0.006
                    col = TOAD if green else (TEXT if q < n else (70, 90, 78))
                    txt(dg if green else do, (LX + 250 + q * CWD, y), ch, 30, "monob" if green else "mono", col, shadow=0)

            replay_line(LY + LH * 1.4, 0.8, 1.7, "replay 1")
            sha_line(LY + LH * 2.4, 1.75, 2.05, 3.15)
            replay_line(LY + LH * 3.8, 2.15, 2.7, "replay 2")
            sha_line(LY + LH * 4.8, 2.8, 3.05, 3.15)
            if t >= 3.15:
                kk = clamp01((t - 3.15) / 0.25)
                txt(dg, (LX + 250 + 40 * CWD + 30, LY + LH * 4.8), "= same", 30, "monob", A(TOAD, 255 * kk), shadow=0)
            if t >= 3.3:
                u = t - 3.3
                lg = logo("MATCH", 150, top=(200, 255, 160), bottom=(40, 190, 60), extrude=(10, 60, 20))
                sc = 2.6 - 1.6 * ease(u / 0.18) if u < 0.18 else 1 + 0.015 * math.sin(u * 8)
                if t > 4.0:
                    sc *= 1 - ease((t - 4.0) / 0.3)
                if sc > 0.02:
                    g = lg.resize((max(1, int(lg.width * sc)), max(1, int(lg.height * sc))), Image.BILINEAR)
                    gl.paste(g, (int(960 - g.width / 2), int(820 - g.height / 2)), g)
        else:
            # ------------------------------------------ phase B: scanning the input file
            txt(do, (LX, LY - 6), "scanning for banned inputs (Up+Down or Left+Right together)\u2026", 26, "mono", DIM, shadow=0)
            txt(dg, (TX1 - 40, LY - 6), "MATCH", 28, "monob", TOAD, anchor="ra", shadow=0)
            check(dg, TX1 - 40 - tw("MATCH", 28, "monob") - 40, LY + 10, 24, TOAD, 4)
            T_SC0, T_SC1 = 4.35, 5.9
            k = clamp01((t - T_SC0) / (T_SC1 - T_SC0))
            pos = 1 + (BAN - 1) * (1 - (1 - k) ** 3)          # line at the centre, decelerating
            fixed = t >= 6.9
            VIS = 17
            cy0 = 590
            top = pos - VIS // 2
            base_line = int(math.floor(top))
            fracp = top - base_line
            blur = k < 0.85
            if t < T_SC1:
                dg.rectangle((LX - 20, cy0 - 6, LX + 1040, cy0 + 30), outline=A(GOLD, 200), width=2)
            for q in range(VIS + 1):
                ln = base_line + q
                if ln < 1 or ln > len(lines_in):
                    continue
                y = cy0 + (q - VIS // 2 - fracp) * 30
                if y < LY + 50 or y > TY1 - 110:
                    continue
                s = lines_in[ln - 1]
                if ln == BAN and not fixed:
                    s = "Down,Up"
                if ln == BAN and t >= T_SC1:
                    kk = pop_scale(t, T_SC1, 0.35)
                    hl = mix(RED, (40, 120, 50), clamp01((t - 6.9) / 0.3))
                    do.rectangle((LX - 20, y - 6, LX - 20 + (1060) * kk, y + 30), fill=A(mix(hl, BG, 0.55), 255))
                    dg.rectangle((LX - 20, y - 6, LX - 20 + (1060) * kk, y + 30), outline=A(hl, 255), width=3)
                dim = 1 - abs(q - VIS // 2 - fracp) / (VIS / 2 + 1)
                gcol = mix((30, 44, 36), (110, 130, 115), dim)
                scol = mix((40, 55, 46), TEXT, dim)
                txt(do, (LX + 110, y), f"{ln:>6}", 26, "mono", gcol, anchor="ra", shadow=0)
                shown = s if s else "\u00b7"
                if ln == BAN and fixed:
                    shown = "(no buttons)"
                    scol = mix(TOAD, WHITE, 1 - clamp01((t - 6.9) / 0.4))
                elif ln == BAN and t >= T_SC1:
                    scol = WHITE
                txt(do, (LX + 140, y), shown, 26, "monob" if ln == BAN else "mono", scol, shadow=0)
                if ln == BAN and 6.4 <= t < 6.9:
                    ks = clamp01((t - 6.4) / 0.3)
                    wdt = tw("Down,Up", 26, "monob")
                    do.line((LX + 136, y + 14, LX + 136 + (wdt + 8) * ks, y + 14), fill=RED, width=5)
            if t >= T_SC1:
                yb = cy0 - 4
                kk = pop_scale(t, T_SC1 + 0.1, 0.4)
                xch = LX + 1100 + (1 - kk) * 300
                if not fixed:
                    chip(do, xch, yb, "BANNED: UP+DOWN TOGETHER", RED, 26, fg=WHITE, anchor="lt")
                else:
                    chip(do, xch, yb, "REPLACED WITH NO INPUT", TOAD, 26, anchor="lt")
                txt(do, (xch, yb + 52), "Level 3 bike-skip segment, its input 594", 22, "ui", DIM)
            if t >= 7.2:
                kk = pop_scale(t, 7.2, 0.4)
                check(dg, LX + (1 - kk) * 200 + tw("re-verified: same result  ", 36, "monob"), TY1 - 60, 34, TOAD, 6)
                txt(dg, (LX + (1 - kk) * 200, TY1 - 80), "re-verified: same result", 36, "monob",
                    A(TOAD, 255 * min(1, kk * 1.5)), shadow=0)
            # scan counter
            txt(do, (TX1 - 40, TY1 - 72), f"line {int(pos):,} / 46,751", 24, "mono", DIM, anchor="ra", shadow=0)
        out = compose(im, gl, ov)
        if 3.48 <= t < 3.6:
            out = flash(out, (t - 3.48) / 0.12, (200, 255, 200))
        if 3.48 <= t < 3.85:
            out = shake(out, (t - 3.48) / 0.37, amp=18)
        sink.put(i, out)
    sink.close()
    return out_path


# ================================================================================================ 5. ARCHITECTURE
def architecture(out_path, dur=12.0, stills=None):
    N = nframes(dur)
    c = cap("cap14")
    T_CL, T_SE, T_EM, T_4, T_16, T_FB, T_BE, T_FI, T_PB, T_TAG = 1.35, 2.2, 3.3, 4.5, 5.5, 6.0, 6.5, 7.3, 8.1, 9.3
    cues = [(0.0, "whoosh"), (0.18, "slam"), (T_CL, "blip"), (T_SE, "blip"), (T_EM, "blip"), (T_4 - 0.05, "whoosh"),
            (T_16 - 0.6, "riser"), (T_16 - 0.05, "whoosh"), (T_FB, "tick"), (T_BE, "blip"), (T_FI, "blip"),
            (T_PB, "blip"), (T_TAG, "ding")]
    write_cues(out_path, cues)
    # 16 emulators, each showing a different part of the real run
    starts = [2560, 3300, 5560, 7700, 10450, 11600, 13300, 15900, 18900, 21500, 27600, 31200, 34700, 38400, 41400, 45600]
    t_on = [T_EM] + [T_4] * 3 + [T_16] * 12
    need = nframes(dur - T_EM) + 4
    foots = [None] * 16
    # boxes
    CL = (80, 400, 400, 650)
    SE = (470, 380, 830, 670)
    EMC = (1130, 535)
    BE = (1440, 230, 1840, 410)
    FI = (1440, 455, 1840, 635)
    PB = (1440, 680, 1840, 880)
    R1 = (EMC[0] - 220, EMC[1] - 193, EMC[0] + 220, EMC[1] + 193)

    def grid_rect(k, n, w, h, gap):
        cols = int(math.sqrt(n))
        rr, cc = divmod(k, cols)
        tw_ = cols * w + (cols - 1) * gap
        th_ = cols * h + (cols - 1) * gap
        x0 = EMC[0] - tw_ / 2 + cc * (w + gap)
        y0 = EMC[1] - th_ / 2 + rr * (h + gap)
        return (x0, y0, x0 + w, y0 + h)

    R4 = [grid_rect(k, 4, 216, 189, 10) for k in range(4)]
    R16 = [grid_rect(k, 16, 106, 93, 8) for k in range(16)]

    def lerp_box(a, b, k):
        return tuple(a[q] + (b[q] - a[q]) * k for q in range(4))

    def rect_of(k, t):
        if t < T_4:
            return R1 if k == 0 else None
        k4 = ease_out_back(clamp01((t - T_4) / 0.55), 1.2)
        if t < T_16:
            return lerp_box(R1, R4[k], k4) if k < 4 else None
        k16 = ease_out_back(clamp01((t - T_16) / 0.55), 1.2)
        return lerp_box(R4[k], R16[k], k16) if k < 4 else lerp_box(R4[k % 4], R16[k], k16)

    PBX = 10
    pb_foot = Footage("cap14", 1, 1 + int(nframes(dur - T_PB) * PBX) + 12)
    raw = (LOGS / "up14.inputs.txt").read_text(encoding="utf-8").splitlines()[1:][5000:5600]   # Level 4, run-length
    toks = []
    for s_ in raw:
        if toks and toks[-1][0] == s_:
            toks[-1][1] += 1
        else:
            toks.append([s_, 1])
    toks = [f"{(s_ or 'none')} x{n}" for s_, n in toks]
    code = ["def beam(state):", "  for press in moves:", "    s = emu.step(press)", "    score(s.ram)"]
    sink = Sink(out_path, stills)
    for i in range(N):
        if sink.stop(i):
            break
        t = i / NES_FPS
        # keep the footage streams moving even when no still is wanted (they are read lazily anyway)
        if not sink.want(i):
            continue
        im = background(t)
        gl, dg, ov, do = layers()

        def node(box, t0, title, sub=None, col=GOLD, tsize=34):
            s = pop_scale(t, t0, 0.5)
            if s <= 0.01:
                return 0
            bx = scaled_box(box, s)
            panel(do, bx, outline=col, fill=(12, 20, 15, 240), width=3)
            dg.rounded_rectangle(bx, radius=14, outline=A(col, 160), width=3)
            if s > 0.85:
                txt(do, (box[0] + 20, box[1] + 16), title, tsize, "ui", col)
                if sub:
                    txt(do, (box[0] + 20, box[1] + 18 + tsize + 8), sub, 22, "ui", DIM)
            return s

        def arrow(pts, t0, col=TOAD, width=4, dots=True):
            if t < t0:
                return
            k = clamp01((t - t0) / 0.35)
            end = polyline_partial(dg, pts, k, A(col, 220), width)
            if k >= 1:
                arrowhead(dg, pts[-2], pts[-1], A(col, 240), 16)
                if dots:
                    flow(dg, pts, t, A(WHITE, 220), n=2, speed=0.8, r=4)

        # ---- nodes
        if node(CL, T_CL, "CLAUDE", "writes the code", GOLD, 40) > 0.85:
            for j, ln in enumerate(code):
                n = int(len(ln) * clamp01((t - T_CL - 0.3 - j * 0.35) / 0.3))
                txt(do, (CL[0] + 22, CL[1] + 122 + j * 28), ln[:n], 19, "mono", TOAD, shadow=0)
        if node(SE, T_SE, "SEARCH PROGRAMS", "(written by Claude)", CYAN, 32) > 0.85:
            for j, ln in enumerate(["beam search", "brute force", "re-sync"]):
                kk = pop_scale(t, T_SE + 0.3 + j * 0.3, 0.35)
                if kk > 0:
                    x = SE[0] + 26 + (1 - kk) * 60
                    y = SE[1] + 120 + j * 44
                    do.ellipse((x, y + 8, x + 12, y + 20), fill=CYAN)
                    txt(do, (x + 26, y), ln, 30, "ui", A(WHITE, 255 * min(1, kk)))
        arrow([(CL[2], 525), (SE[0] - 2, 525)], T_SE - 0.25, GOLD)
        # ---- emulators
        if t >= T_EM:
            ncount = 16 if t >= T_16 else 4 if t >= T_4 else 1
            kk = pop_scale(t, T_EM, 0.4)
            txt(do, (EMC[0] - 220, 236), "EMULATORS", 32, "ui", TOAD)
            lab = f"\u00d7{ncount}"
            sc_ = 1 + 0.5 * (1 - pop_scale(t, {1: T_EM, 4: T_4, 16: T_16}[ncount], 0.4))
            txt(dg, (EMC[0] + 220, 232), lab, int(40 * sc_), "monob", GOLD, anchor="ra", shadow=0)
            rects = [rect_of(k, t) for k in range(16)]
            gleft = min(rb[0] for rb in rects if rb is not None)
            for k in range(16):
                rb = rects[k]
                if rb is None:
                    continue
                if foots[k] is None:
                    foots[k] = (Footage("cap14", starts[k], starts[k] + need), i)
                fo, i0 = foots[k]
                nes = fo.get(starts[k] + (i - i0))
                if k == 0 and t < T_4:
                    rb = scaled_box(rb, kk)
                w_, h_ = int(rb[2] - rb[0]), int(rb[3] - rb[1])
                if w_ < 4 or h_ < 4:
                    continue
                im.paste(nes.resize((w_, h_), Image.NEAREST), (int(rb[0]), int(rb[1])))
                dg.rectangle((rb[0] - 3, rb[1] - 3, rb[2] + 2, rb[3] + 2), outline=A(TOAD, 200), width=2)
                # search -> each emulator
                if t >= T_EM + 0.2 and rb[0] <= gleft + 2:      # one line per row, into the grid's left edge
                    ya = (rb[1] + rb[3]) / 2
                    pts = [(SE[2] + 2, 525), (SE[2] + 30, 525), (rb[0] - 12, ya)]
                    dg.line(pts, fill=A(CYAN, 110), width=2)
                    flow(dg, pts, t + k * 0.13, A(CYAN, 230), n=1, speed=1.1, r=3)
            txt(do, (EMC[0], 812), "real Battletoads, run by BizHawk", 21, "ui", DIM, anchor="ma")
        # feedback loop: RAM -> score
        if t >= T_FB:
            pts = [(EMC[0], 850), (EMC[0], 880), (650, 880), (650, SE[3] + 4)]
            arrow(pts, T_FB, CYAN, 3)
            if t >= T_FB + 0.3:
                txt(do, (680, 846), "reads RAM \u2192 scores every try", 22, "ui", CYAN)
        # ---- right column
        arrow([(R16[3][2] + 14 if t >= T_16 else EMC[0] + 230, 535), (1400, 535), (1400, 320), (BE[0] - 2, 320)], T_BE - 0.3,
              TOAD)
        if node(BE, T_BE, "BEST INPUTS", None, TOAD, 32) > 0.85:
            # a ticker of real (run-length) inputs, clipped to the box
            sw_, sh_ = BE[2] - BE[0] - 40, 44
            strip = Image.new("RGBA", (sw_, sh_), (0, 0, 0, 0))
            dst = ImageDraw.Draw(strip)
            x = sw_ - (t - T_BE) * 170
            j = 0
            while x < sw_ and j < len(toks):
                wdt = tw(toks[j], 22, "monob") + 16
                if x + wdt > 0:
                    chip(dst, x, 4, toks[j], (40, 70, 30), 22, fg=TOAD, anchor="lt")
                x += wdt + 10
                j += 1
            ov.paste(strip, (BE[0] + 20, BE[1] + 76), strip)
            txt(do, (BE[0] + 20, BE[1] + 136), "kept: the ones that score best", 20, "ui", DIM)
        arrow([(1640, BE[3] + 2), (1640, FI[1] - 2)], T_FI - 0.3, TOAD)
        if node(FI, T_FI, "INPUT FILE", None, GOLD, 32) > 0.85:
            n = int(46751 * ease(clamp01((t - T_FI - 0.2) / 1.0)))
            txt(dg, (FI[0] + 20, FI[1] + 70), f"{n:,}", 52, "monob", GOLD, shadow=0)
            txt(do, (FI[0] + 20 + tw("46,751", 52, "monob") + 16, FI[1] + 92), "frames", 26, "ui", DIM)
            txt(do, (FI[0] + 20, FI[1] + 138), "one line = the buttons for one frame", 20, "ui", DIM)
        arrow([(1640, FI[3] + 2), (1640, PB[1] - 2)], T_PB - 0.3, TOAD)
        if node(PB, T_PB, "PLAYBACK FROM POWER-ON", None, TOAD, 23) > 0.85:
            nes = pb_foot.get(1 + int((t - T_PB) * NES_FPS * PBX))
            th = nes.resize((150, 131), Image.NEAREST)
            ov.paste(th, (PB[0] + 20, PB[1] + 56))
            dg.rectangle((PB[0] + 17, PB[1] + 53, PB[0] + 172, PB[1] + 189), outline=A(TOAD, 200), width=2)
            txt(do, (PB[0] + 190, PB[1] + 70), "no save states", 22, "ui", TEXT)
            txt(do, (PB[0] + 190, PB[1] + 102), "same result", 22, "ui", TEXT)
            txt(do, (PB[0] + 190, PB[1] + 134), "every time", 22, "ui", TEXT)
            txt(dg, (PB[0] + 190, PB[1] + 166), f"\u00d7{PBX} speed", 18, "mono", DIM, shadow=0)
        # ---- tagline
        if t >= T_TAG:
            l1, l2 = "The AI doesn't play the game.", "It writes the programs that find the inputs."
            k1, k2 = pop_scale(t, T_TAG, 0.45), pop_scale(t, T_TAG + 0.6, 0.45)
            w1, w2 = tw(l1 + " ", 40, "ui"), tw(l2, 40, "ui")
            x0 = 960 - (w1 + w2) / 2
            txt(do, (x0, 950 + (1 - k1) * 40), l1, 40, "ui", A(WHITE, 255 * min(1, k1 * 1.5)), anchor="lm")
            if k2 > 0:
                txt(dg, (x0 + w1, 950 + (1 - k2) * 40), l2, 40, "ui", A(GOLD, 255 * min(1, k2 * 1.5)), anchor="lm")
        header(im, "HOW IT WORKS", t)
        out = compose(im, gl, ov)
        out = intro(out, "HOW IT WORKS", t, sub="Claude writes searches; the searches play", size=150)
        sink.put(i, out)
    sink.close()
    return out_path


CLIP_LIST = [("ramvision", ramvision, 14.0), ("bike_skip", bike_skip, 20.0), ("rng_chaos", rng_chaos, 10.0),
         ("integrity", integrity, 8.0), ("architecture", architecture, 12.0)]

if __name__ == "__main__":
    import time
    args = sys.argv[1:]
    stills = None
    if "--stills" in args:
        j = args.index("--stills")
        stills = [int(x) for x in args[j + 1].split(",")]
        args = args[:j] + args[j + 2:]
    want = set(args) or {n for n, _, _ in CLIP_LIST}
    for name, fn, d in CLIP_LIST:
        if name in want:
            t0 = time.time()
            p = fn(CLIPS / f"{name}.mp4", dur=d, stills=stills)
            print(f"{name}: {p}  ({time.time() - t0:.0f} s)", flush=True)
