"""Section 02: "You asked for it". Best of the Zelda video (13 s) -> the YouTube comments slam in -> "warps or no
warps?" -> SO WE DID BATTLETOADS -> subscribe call to action.  -> clips/s02_asked.mp4 (+ .wav)"""
from __future__ import annotations

import subprocess

import numpy as np

from shots import *  # noqa: F401,F403
import audio

ZC = Path(r"../harness\youtube\clips_v3")


def zelda_frames(clip, t0, dur, speed=1.0):
    """frames of a 1280x720 Zelda clip, scaled to 1080p, `speed`x"""
    n_src = int(dur * speed * NES_FPS) + 2
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-i", str(ZC / clip), "-an", "-frames:v", str(n_src),
                          "-vf", "scale=1920:1080:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fb = W * H * 3
    src = []
    while True:
        raw = p.stdout.read(fb)
        if len(raw) < fb:
            break
        src.append(raw)
    n = int(dur * NES_FPS)
    for i in range(n):
        j = min(len(src) - 1, int(i * speed))
        yield Image.frombuffer("RGB", (W, H), src[j])


ZTAG = (255, 214, 90)


def zelda_part(w, m):
    t_start = w.n / NES_FPS
    parts = [("mosaic_day2.mp4", 6.0, 1.35, 1.0, "71 MINUTES OF ATTEMPTS"),
             ("mind_59_fight.mp4", 5.0, 1.35, 1.0, "WHAT THE PLANNER SEES"),
             ("run6_L8_keyroom.mp4", 1.5, 1.5, 2.0, "FIVE BLUE DARKNUTS"),
             ("map_route4.mp4", 6.0, 1.4, 4.0, "THE ROUTE IT PLANNED")]
    for pi, (clip, t0, dur, sp, label) in enumerate(parts):
        m.add_sfx(w.n / NES_FPS, "whoosh", 0.6)
        for i, im in enumerate(zelda_frames(clip, t0, dur, sp)):
            im = ImageEnhance.Contrast(im).enhance(1.05)
            if i < 4:
                im = flash(im, i / 4)
            tag(im, "AI PLAYS ZELDA", i if pi == 0 else 99, label, col=ZTAG, y=H - 230)
            if sp != 1.0:
                d = ImageDraw.Draw(im)
                chip(d, W - 50, H - 50, f"{sp:g}x SPEED", WHITE, 26, anchor="mb")
            w.put(vignette(im, 0.35))
    return t_start


def comment_card(path, scale):
    im = Image.open(path).convert("RGB")
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    pad = 18
    card = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (255, 255, 255, 255))
    card.paste(im, (pad, pad))
    sh = Image.new("RGBA", (card.width + 40, card.height + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((20, 26, card.width + 20, card.height + 26), 18, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 16, fill=255)
    sh.paste(card, (20, 20), mask)
    return sh


def comments_part(w, m):
    # background: the Battletoads title screen, blurred and darkened, slowly zooming
    title = next(nes_frames(VIDEO / "up14.mkv", 6 + 700, 1))
    bg0 = backdrop(title)
    cards = [("comment2.png", 1.75, (-4, 150, 120)), ("comment3.png", 1.75, (3, 1000, 330)),
             ("comment4.png", 1.6, (-2, 260, 560)), ("comment5.png", 2.4, (2, 1000, 700))]
    cards = [(comment_card(HERE / "assets" / f, s), r, x, y) for f, s, (r, x, y) in cards]
    beat = 0.55
    n = int((beat * len(cards) + 3.0) * NES_FPS)
    t0 = w.n / NES_FPS
    for k in range(len(cards)):
        m.add_sfx(t0 + k * beat, "slam", 0.75)
    m.add_sfx(t0 + beat * len(cards) + 0.5, "ding", 0.6)
    for i in range(n):
        t = i / NES_FPS
        z = 1 + 0.04 * t
        bg = bg0.resize((int(W * z), int(H * z)), Image.BILINEAR)
        bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
        im = bg.copy()
        last_land = None
        for k, (c, rot, x, y) in enumerate(cards):
            tk = t - k * beat
            if tk < 0:
                continue
            land = 0.14
            sc = 1.0 if tk >= land else 2.2 - 1.2 * ease(tk / land)
            cc = c.rotate(rot, resample=Image.BICUBIC, expand=True)
            if sc != 1.0:
                cc = cc.resize((int(cc.width * sc), int(cc.height * sc)), Image.BILINEAR)
            cx = x + c.width // 2 - (cc.width // 2) if x < 600 else x - c.width // 2 + (c.width - cc.width) // 2
            cx = int(x - (cc.width - c.width) / 2) if x < 600 else int(W - 80 - c.width - (cc.width - c.width) / 2)
            im.paste(cc, (cx, int(y - (cc.height - c.height) / 2)), cc)
            if tk >= land:
                last_land = tk - land
        if last_land is not None and last_land < 0.3:
            im = shake(im, last_land / 0.3, 18)
        # the question: zoom in on "Warps or no warps?"
        tq = t - beat * len(cards) - 0.3
        if tq > 0:
            k = ease(min(1, tq / 0.6))
            c5, rot, x5, y5 = cards[3]
            d = ImageDraw.Draw(im)
            # highlight box around the words on the last card (image coords 233..360 x 55..72 at scale 2.4)
            bx0 = int(W - 80 - c5.width) + 20 + 18 + int(233 * 2.4)
            by0 = y5 + 20 + 18 + int(53 * 2.4)
            bx1, by1 = bx0 + int(130 * 2.4), by0 + int(22 * 2.4)
            d.rounded_rectangle((bx0 - 10, by0 - 6, bx1 + 10, by1 + 6), 10, outline=GOLD, width=int(2 + 6 * k))
            if k > 0.5:
                a = min(1, (tq - 0.3) / 0.3)
                band = im.crop((0, 0, W, 230))
                im.paste(ImageEnhance.Brightness(band).enhance(1 - 0.75 * a), (0, 0))
                big = logo("WARPS OR NO WARPS?", 110)
                bb = big.copy(); bb.putalpha(big.split()[3].point(lambda p: int(p * a)))
                im.paste(bb, ((W - big.width) // 2, 115 - big.height // 2), bb)
        w.put(vignette(im, 0.3))


def subscribe_part(w, m):
    """SO WE DID BATTLETOADS slam, then the subscribe button gets clicked"""
    t0 = w.n / NES_FPS
    bgf = next(nes_frames(VIDEO / "up14.mkv", 6 + 2000, 1))
    bg = darken(backdrop(bgf), 0.8)
    n1 = int(1.8 * NES_FPS)
    m.add_sfx(t0, "slam", 0.9)
    for i in range(n1):
        w.put(vignette(slam(bg, "SO WE DID BATTLETOADS", i / NES_FPS, 1.8, size=130), 0.3))
    # subscribe
    t1 = w.n / NES_FPS
    n2 = int(3.6 * NES_FPS)
    m.add_sfx(t1, "whoosh", 0.6)
    m.add_sfx(t1 + 1.2, "blip", 0.9)
    m.add_sfx(t1 + 1.6, "ding", 0.7)
    for i in range(n2):
        t = i / NES_FPS
        im = bg.copy()
        d = ImageDraw.Draw(im)
        k = ease_out_back(min(1, t / 0.4))
        cx, cy = W // 2, 520
        clicked = t > 1.2
        bw, bh = int(560 * k), int(130 * k)
        if bw > 10:
            col = (60, 60, 60) if clicked else (230, 25, 25)
            press = 0.94 if 1.2 < t < 1.3 else 1.0
            bw2, bh2 = int(bw * press), int(bh * press)
            d.rounded_rectangle((cx - bw2 // 2, cy - bh2 // 2, cx + bw2 // 2, cy + bh2 // 2), bh2 // 2, fill=col)
            if k > 0.8:
                txt = "SUBSCRIBED" if clicked else "SUBSCRIBE"
                d.text((cx, cy), txt, font=font("arialbd.ttf", 56), fill=WHITE, anchor="mm")
            # bell
            if clicked:
                ang = math.sin((t - 1.2) * 30) * 25 * max(0, 1 - (t - 1.2) / 1.2)
                bell = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
                bd = ImageDraw.Draw(bell)
                bd.pieslice((20, 14, 100, 100), 180, 360, fill=WHITE)
                bd.rectangle((20, 56, 100, 84), fill=WHITE)
                bd.polygon([(12, 92), (108, 92), (100, 80), (20, 80)], fill=WHITE)
                bd.ellipse((50, 92, 70, 110), fill=WHITE)
                bell = bell.rotate(ang, center=(60, 14), resample=Image.BICUBIC)
                im.paste(bell, (cx + bw // 2 + 30, cy - 60), bell)
        # cursor
        if 0.5 < t < 2.6:
            kx = ease(min(1, (t - 0.5) / 0.6))
            px = int(W * 0.78 + (cx + 60 - W * 0.78) * kx)
            py = int(H * 0.9 + (cy + 20 - H * 0.9) * kx)
            d.polygon([(px, py), (px, py + 52), (px + 14, py + 40), (px + 26, py + 64), (px + 36, py + 58),
                       (px + 24, py + 36), (px + 42, py + 36)], fill=WHITE, outline=(0, 0, 0))
        if t > 1.5:
            a = min(1, (t - 1.5) / 0.4)
            f = font("arialbd.ttf", 46)
            txt = "KEEP THE COMMENTS COMING"
            d.text((cx + 3, 720 + 3 + (1 - a) * 20), txt, font=f, fill=(0, 0, 0), anchor="mm")
            d.text((cx, 720 + (1 - a) * 20), txt, font=f, fill=tuple(int(c * a) for c in GOLD), anchor="mm")
        w.put(vignette(im, 0.3))


def build():
    out = CLIPS / "s02_asked.mp4"
    w = Writer(out)
    m = audio.Mix(40)
    zelda_part(w, m)
    tz = w.n / NES_FPS
    comments_part(w, m)
    subscribe_part(w, m)
    w.close()
    dur = w.n / NES_FPS
    bed = audio.chiptune(bars=int(dur / 1.6) + 1, bpm=150, intensity=0.4)
    m.add(0, bed, 0.25)
    m.write(CLIPS / "s02_asked.wav", dur)
    print("s02", round(dur, 2), "s (zelda", round(tz, 2), ")")


if __name__ == "__main__":
    build()
