"""Section 01: the opening montage, cut to an original 150 BPM chiptune loop, one shot per bar (1.6 s).
No timer, no record: just the coolest moments. Ends on the Dark Queen's last hit, freeze, flash, black.
-> clips/s01_montage.mp4 (+ .wav)"""
from __future__ import annotations

import numpy as np

from shots import *  # noqa: F401,F403
from gridshot import grid_frames
import audio

BPM = 150
BAR = 4 * 60 / BPM * NES_FPS            # output frames per bar (96.16)


def bar_frames(i):
    return int(round((i + 1) * BAR)) - int(round(i * BAR))


def cut_flash(im, i, n=4):
    return flash(im, i / n) if i < n else im


def height(cap, row):
    return cap.r(row, 0x439) + 256 * cap.r(row, 0x42A)


def shot_tt(n):
    def draw(im, d, cam, row, i, info):
        tag(im, "TURBO TUNNEL", i, "WALLS AT 12 PX PER FRAME")
    return game_shot("capwip", 13560, n, draw=draw, scale=8.0)


def shot_swim(n):
    def draw(im, d, cam, row, i, info):
        tag(im, "TERRA TUBES", i, "SWIMMING: 3x SLOWER THAN WALKING", col=CYAN)
    return game_shot("cap14", 22420, n, draw=draw, scale=8.0, speed=1.5)


def shot_clinger(n):
    def draw(im, d, cam, row, i, info):
        boxes = track(d, cam, info["cap"], row, only={"BUZZBALL"}, hp=False, toad=False)
        tag(im, "CLINGER-WINGER", i, "DON'T LET THE BUZZBALL CATCH YOU", col=ORANGE)
    return game_shot("cap14", 29960, n, draw=draw, scale=6.0, target=(128, 130))


def shot_ratboot(n):
    def draw(im, d, cam, row, i, info):
        track(d, cam, info["cap"], row, only={"RAT"}, hp=True)
        tag(im, "RAT RACE", i, "THE RAT BOOT", col=RED)
        if info["slow"]:
            chip(d, W - 60, H - 60, "SLOW MOTION", WHITE, 30, anchor="mb")

    def post(im, i):
        return im
    return game_shot("cap14", 28905, n, draw=draw, scale=7.5, slow=[(28944, 28956, 3)])


def shot_spring(n):
    start = {}

    def draw(im, d, cam, row, i, info):
        h = height(info["cap"], row)
        start.setdefault("h", h)
        tag(im, "THE REVOLUTION", i, "PUMP THE SPRING", col=(200, 120, 255))
        readout(d, W - 420, H - 220, "HEIGHT GAINED", f"+{max(0, h - start['h'])} px", GOLD)
    return game_shot("cap14", 41556, n, draw=draw, scale=7.5, follow=0.25)


def shot_boot(n):
    def draw(im, d, cam, row, i, info):
        track(d, cam, info["cap"], row, only={"HORNHEAD"})
        tag(im, "THE BIG BOOT", i, "47 DAMAGE IN ONE KICK", col=GOLD)
        if info["slow"]:
            chip(d, W - 60, H - 60, "SLOW MOTION", WHITE, 30, anchor="mb")
    return game_shot("cap14", 41452, n, draw=draw, scale=7.0, slow=[(41494, 41508, 3)])


def shot_queen(n):
    hit = 46084
    def draw(im, d, cam, row, i, info):
        track(d, cam, info["cap"], row, only={"DARK QUEEN"}, hp=False)
        tag(im, "ARMAGEDDON", i, "THE DARK QUEEN", col=RED)
    # play up to the hit, then hold it
    lead_rows = n // 2
    rows_slow = [(hit, hit, n - lead_rows)]
    return game_shot("cap14", hit - lead_rows + 1, n, draw=draw, scale=6.0, slow=rows_slow, follow=0.08)


def build():
    out = CLIPS / "s01_montage.mp4"
    w = Writer(out)
    shots = [("grid", 2), ("tt", 1), ("swim", 1), ("clinger", 1), ("rat", 1), ("spring", 1), ("boot", 1), ("queen", 1)]
    fns = dict(tt=shot_tt, swim=shot_swim, clinger=shot_clinger, rat=shot_ratboot, spring=shot_spring, boot=shot_boot,
               queen=shot_queen)
    bar = 0
    cuts = []
    for name, bars in shots:
        n = sum(bar_frames(bar + j) for j in range(bars))
        cuts.append((w.n / NES_FPS, name))
        gen = grid_frames() if name == "grid" else fns[name](n)
        for i in range(n):
            try:
                im = next(gen)
            except StopIteration:
                pass
            if name != "grid":
                im = cut_flash(im, i)
            if name == "queen":
                hold_from = n // 2
                if i >= hold_from:                       # the hit: flash, shake, then fade to black at the end
                    k = (i - hold_from) / (n - hold_from)
                    im = shake(flash(im, (i - hold_from) / 10), (i - hold_from) / 30, 30)
                    if k > 0.7:
                        im = Image.blend(im, Image.new("RGB", (W, H)), (k - 0.7) / 0.3)
            w.put(vignette(im, 0.3))
        bar += bars
    w.close()
    dur = w.n / NES_FPS
    # audio: the loop + an impact on every cut + a crash under the grid + a big hit on the queen
    m = audio.Mix(dur + 1)
    loop = audio.chiptune(bars=bar, bpm=BPM)
    m.add(0, loop, 0.55)
    for t, name in cuts:
        m.add_sfx(t, "slam" if name in ("grid", "queen") else "whoosh", 0.7)
    for k in range(8):
        m.add_sfx(1.2 + k * 0.22, "crash", 0.25)
    m.add_sfx(cuts[-1][0] + (bar_frames(bar - 1) // 2) / NES_FPS, "slam", 1.0)
    wav = m.write(CLIPS / "s01_montage.wav", dur)
    print("montage", round(dur, 2), "s; cuts", [(round(t, 2), n) for t, n in cuts])
    return out, wav


if __name__ == "__main__":
    build()
