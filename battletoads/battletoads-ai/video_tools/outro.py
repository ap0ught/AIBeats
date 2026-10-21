"""The owner's on-camera outro over the moving background.

His clip (outro/Battletoads outro.mp4, 25 fps, background already removed to black) is keyed with a row/column span
mask (fast, and it keeps dark details inside the silhouette such as the cap and eyes), placed over the outro
background, a like + subscribe pop-up lands when he says it, then he fades out first and the background follows over
FADE_BG seconds.     python outro.py  -> clips/s11_outro_final.mp4 (+ .wav)"""
from __future__ import annotations

import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from style import *  # noqa: F401,F403
import audio

SRC = HERE / "outro" / "Battletoads outro.mp4"
FADE_ME = 0.6
FADE_BG = 4.0


def speech_times():
    """(speech end, time he says subscribe/like) from a whisper pass saved in out/outro_words.json"""
    w = json.loads((OUT / "outro_words.json").read_text(encoding="utf-8"))
    end = max(x[1] for x in w)
    sub = next((x[0] for x in w if "subscri" in x[2].lower()), None)
    like = next((x[0] for x in w if x[2].lower().strip(" ,.!") in ("like", "liked")), None)
    return end, sub, like


def key_mask(fr):
    """alpha for one 1920x1080 frame: the subject = between the first and last bright pixel of each row AND each
    column (at quarter resolution), feathered"""
    small = np.asarray(fr.resize((480, 270), Image.BOX)).max(2)
    bright = small > 22
    m = np.zeros_like(bright)
    rows = np.nonzero(bright.any(1))[0]
    for r in rows:
        c = np.nonzero(bright[r])[0]
        m[r, c[0]:c[-1] + 1] = True
    cols = np.zeros_like(bright)
    for c in np.nonzero(bright.any(0))[0]:
        rr = np.nonzero(bright[:, c])[0]
        cols[rr[0]:rr[-1] + 1, c] = True
    m &= cols
    a = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    return a


def like_sub(im, t):
    """like + subscribe pop-up in the lower right, t = seconds since it started (lasts ~4.5 s)"""
    if t < 0 or t > 4.6:
        return im
    d = ImageDraw.Draw(im)
    k = ease_out_back(min(1, t / 0.35)) if t < 4.2 else max(0.0, 1 - (t - 4.2) / 0.4)
    x0, y0 = 70, 920
    # like button
    lw = int(220 * k)
    if lw > 20:
        liked = t > 0.9
        d.rounded_rectangle((x0, y0, x0 + lw, y0 + 90), 45, fill=(40, 40, 40) if not liked else (60, 120, 255))
        if k > 0.8:
            # thumbs up glyph
            cx, cy = x0 + 50, y0 + 45
            d.rectangle((cx - 20, cy - 4, cx - 10, cy + 22), fill=WHITE)
            d.rounded_rectangle((cx - 8, cy - 8, cx + 22, cy + 22), 6, fill=WHITE)
            d.polygon([(cx - 6, cy - 6), (cx + 2, cy - 26), (cx + 10, cy - 24), (cx + 8, cy - 6)], fill=WHITE)
            d.text((x0 + 90, y0 + 45), "LIKE", font=font("arialbd.ttf", 40), fill=WHITE, anchor="lm")
    # subscribe button
    sx = x0 + 240
    sw = int(380 * k)
    if sw > 20:
        subbed = t > 2.0
        d.rounded_rectangle((sx, y0, sx + sw, y0 + 90), 45, fill=(60, 60, 60) if subbed else (230, 25, 25))
        if k > 0.8:
            d.text((sx + sw // 2, y0 + 45), "SUBSCRIBED" if subbed else "SUBSCRIBE", font=font("arialbd.ttf", 40),
                   fill=WHITE, anchor="mm")
    # cursor clicks like, then subscribe
    if 0.3 < t < 3.2:
        tx, ty = (x0 + 110, y0 + 60) if t < 1.5 else (sx + 190, y0 + 60)
        if t < 0.9:
            kx = ease((t - 0.3) / 0.6)
            px, py = int(900 + (tx - 900) * kx), int(1060 + (ty - 1060) * kx)
        elif t < 1.5:
            px, py = tx, ty
        else:
            kx = ease(min(1, (t - 1.5) / 0.5))
            px, py = int(x0 + 110 + (sx + 190 - x0 - 110) * kx), ty
        d.polygon([(px, py), (px, py + 46), (px + 12, py + 35), (px + 22, py + 56), (px + 31, py + 51), (px + 21, py + 31),
                   (px + 37, py + 31)], fill=WHITE, outline=(0, 0, 0))
    return im


def build():
    end, sub_t, like_t = speech_times()
    pop_t = (like_t if like_t is not None else sub_t if sub_t is not None else end - 5.0) - 0.3
    dur = end + 0.3 + FADE_ME + FADE_BG
    bgp = CLIPS / "s11_outro_bg_long.mp4"
    if not bgp.exists():
        sys.path.insert(0, str(HERE))
        from sections import p_outro_bg
        p_outro_bg("s11_outro_bg_long", dur=max(40.0, dur + 1))
    me = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(SRC), "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo",
                           "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    bg = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(bgp), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fb = W * H * 3
    w = Writer(CLIPS / "s11_outro_final.mp4")
    n = int(dur * NES_FPS)
    last_me = None
    for i in range(n):
        t = i / NES_FPS
        rb = bg.stdout.read(fb)
        im = Image.frombuffer("RGB", (W, H), rb).copy() if len(rb) == fb else im
        raw = me.stdout.read(fb)
        if len(raw) == fb:
            last_me = Image.frombuffer("RGB", (W, H), raw).copy()
        a_me = 1.0 - min(1.0, max(0.0, (t - end - 0.3) / FADE_ME))
        if last_me is not None and a_me > 0:
            alpha = key_mask(last_me)
            if a_me < 1:
                alpha = alpha.point(lambda p: int(p * a_me))
            im.paste(last_me, (0, 0), alpha)
        im = like_sub(im, t - pop_t)
        k_bg = 1.0 - min(1.0, max(0.0, (t - end - 0.3 - FADE_ME) / FADE_BG))
        if k_bg < 1:
            im = Image.blend(Image.new("RGB", (W, H)), im, k_bg)
        w.put(im)
    w.close()
    # sound: his voice on top, the background music ducked under him and faded with the picture
    m = audio.Mix(dur + 1)
    voice = audio.load(SRC)
    v_db = 20 * np.log10(np.sqrt(np.mean(voice[np.abs(voice).max(1) > 0.01] ** 2)) + 1e-9)
    voice = voice * 10 ** ((-18.0 - v_db) / 20)
    bed = audio.load(CLIPS / "s11_outro_bg_long.wav")[:int(dur * audio.SR)]
    env = np.full(len(bed), 0.3, np.float32)
    fl0 = int((end + 0.3) * audio.SR)
    env[fl0:] = np.linspace(1.0, 1.0, len(env) - fl0)
    fo = int((end + 0.3 + FADE_ME) * audio.SR)
    tail = len(env) - fo
    if tail > 0:
        env[fo:] = np.linspace(1.0, 0.0, tail)
    m.add(0, bed * env[:, None], 1.0)
    m.add(0, voice[:int(dur * audio.SR)], 1.0)
    m.add_sfx(pop_t + 0.05, "whoosh", 0.5)
    m.add_sfx(pop_t + 0.9, "blip", 0.7)
    m.add_sfx(pop_t + 2.0, "ding", 0.6)
    m.write(CLIPS / "s11_outro_final.wav", w.n / NES_FPS)
    print("outro", round(w.n / NES_FPS, 2), "s; speech ends", round(end, 2), "pop-up at", round(pop_t, 2))


if __name__ == "__main__":
    build()
