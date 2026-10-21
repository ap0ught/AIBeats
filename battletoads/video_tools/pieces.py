"""Reusable pieces. Each piece renders clips/<name>.mp4 and clips/<name>.wav (same length) and returns the duration.
Section scripts (sections.py) list pieces in order; the assembler joins them."""
from __future__ import annotations

import json
import subprocess

import numpy as np

from shots import *  # noqa: F401,F403
import audio


def done(w, m, name):
    w.close()
    dur = w.n / NES_FPS
    m.write(CLIPS / f"{name}.wav", dur)
    return dur


def raw_frames(path, t0, dur, speed=1.0):
    """frames of any raw NES capture (no RAM), from t0 seconds, `speed`x"""
    start = int(t0 * NES_FPS)
    need = int(dur * NES_FPS * speed) + 2
    src = list(nes_frames(path, start, need))
    for i in range(int(dur * NES_FPS)):
        yield src[min(len(src) - 1, int(i * speed))]


def p_slam_over(name, text, frames_fn, dur=2.2, sub=None, size=140, dim=0.5, sfx="slam", colors=None):
    """a title slam over moving footage (frames_fn(n) yields 1920x1080 images)"""
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    m.add_sfx(0, sfx, 0.9)
    n = int(dur * NES_FPS)
    for i, im in enumerate(frames_fn(n)):
        im = darken(im, dim)
        w.put(vignette(slam(im, text, i / NES_FPS, dur, sub=sub, size=size, colors=colors), 0.35))
    return done(w, m, name)


def cam_frames(path, t0, scale=6.0, center=(128, 120), speed=1.0, drift=0.0):
    def gen(n):
        cam = Camera(scale, cx=center[0], cy=center[1])
        for i, nes in enumerate(raw_frames(path, t0, n / NES_FPS + 0.1, speed)):
            if i >= n:
                break
            if drift:
                cam.scale = scale * (1 + drift * i / n)
            yield scanlines(cam.render(nes), 0.1)
    return gen


def game_frames(capname, row0, scale=8.0, speed=1.0, **kw):
    def gen(n):
        return game_shot(capname, row0, n, scale=scale, speed=speed, **kw)
    return gen


def p_game(name, capname, row0, dur, speed=1.0, scale=8.0, label=None, sub=None, col=TOAD, draw=None, slow=(),
           target="toad", game_gain=0.8, sfx=(), extra=None):
    """a gameplay shot with the level tag, optional overlays (draw) and the capture's own sound"""
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    n = int(dur * NES_FPS)

    def dr(im, d, cam, row, i, info):
        if draw:
            draw(im, d, cam, row, i, info)
        if label:
            tag(im, label, i, sub, col=col)
    for i, im in enumerate(game_shot(capname, row0, n, speed=speed, scale=scale, draw=dr, slow=slow, target=target)):
        if extra:
            im = extra(im, i)
        w.put(vignette(cut_in(im, i), 0.3))
    if game_gain and not slow:
        lead = lead_of(capname)
        ga = audio.game_audio(SRCS[capname], lead + row0, int(n * speed))
        if speed != 1.0:                                # sped-up footage: take every speed-th chunk (keeps pitch)
            chunk = int(audio.SR / NES_FPS)
            idx = np.concatenate([np.arange(int(i * speed) * chunk, int(i * speed) * chunk + chunk) for i in range(n)])
            idx = idx[idx < len(ga)]
            ga = ga[idx]
        m.add(0, ga, game_gain)
    for t, s, g in sfx:
        m.add_sfx(t, s, g)
    return done(w, m, name)


def cut_in(im, i, n=3):
    return flash(im, i / n) if i < n else im


def p_raw_grid(name, files, labels, dur, t0s=None, cols=4, title=None, speed=1.0, highlight=None, sfx_every=None):
    """a grid of raw captures (day-one experiments) playing at once, each labelled"""
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    rows_ = (len(files) + cols - 1) // cols
    top = 80 if title else 0
    tw, th = W // cols, (H - top) // rows_
    gens = [raw_frames(f, (t0s[i] if t0s else 0), dur, speed) for i, f in enumerate(files)]
    n = int(dur * NES_FPS)
    m.add_sfx(0, "whoosh", 0.6)
    for i in range(n):
        im = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(im)
        for k, g in enumerate(gens):
            try:
                fr = next(g)
            except StopIteration:
                continue
            cx, cy = (k % cols) * tw, top + (k // cols) * th
            appear = k * 3
            if i < appear:
                continue
            t = fr.resize((tw, int(224 * tw / 256)), Image.NEAREST)
            tt = max(0, (t.height - th) // 2)
            t = t.crop((0, tt, tw, tt + th))
            im.paste(t, (cx, cy))
            d.rectangle((cx, cy, cx + tw - 1, cy + th - 1), outline=(0, 0, 0), width=4)
            col = GOLD if highlight == k else TOAD
            chip(d, cx + 10, cy + th - 10, labels[k], col, 24)
            if highlight == k and i > n * 0.55:
                d.rectangle((cx + 3, cy + 3, cx + tw - 4, cy + th - 4), outline=GOLD, width=8)
        if title:
            d.rectangle((0, 0, W, top), fill=(0, 0, 0))
            d.text((40, top // 2), title, font=mono(38, True), fill=TOAD, anchor="lm")
        w.put(im)
    return done(w, m, name)


def p_clip(name, src_mp4, sfx_json=None):
    """an agent-made clip: copy its audio cues into a wav"""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src_mp4)],
                               capture_output=True, text=True).stdout.strip())
    m = audio.Mix(dur + 1)
    if sfx_json:
        m.add_cues(0, sfx_json, 0.7)
    m.write(CLIPS / f"{name}.wav", dur)
    return dur
