"""The tower, stitched from the final run's own frames (camera y = $89/$8A, world y = camY + screen y), and a ghost
race up it: the first finished run vs the final run, from the moment each lands in Level 12.
-> clips/s07_tower.mp4/.wav ; map at out/tower_map.png"""
from __future__ import annotations

import numpy as np

from shots import *  # noqa: F401,F403
import audio

L12 = {"cap14": (36192, 45057), "capwip": (54692, 65181)}     # landing -> the camera leaves the tower


def camy(cap, f):
    v = cap.r(f, 0x89) + 256 * cap.r(f, 0x8A)
    return v - 65536 if v > 32768 else v


def build_map(step=2):
    cap = cap_of("cap14")
    a, b = L12["cap14"]
    ys = [camy(cap, f) for f in range(a, b)]
    y0, y1 = min(ys), max(ys) + 224
    canvas = np.zeros((y1 - y0, 256, 3), np.uint8)
    filled = np.zeros(y1 - y0, bool)
    lead = lead_of("cap14")
    for k, nes in enumerate(nes_frames(SRCS["cap14"], lead + a, b - a)):
        if k % step:
            continue
        f = data_row("cap14", a + k)
        cy = camy(cap, min(f, cap.n - 1)) - y0
        arr = np.asarray(nes)
        # rows 40..224 are the playfield (the score bar is on top); later frames overwrite earlier ones
        canvas[cy + 40:cy + 224] = arr[40:224]
        filled[cy + 40:cy + 224] = True
    Image.fromarray(canvas).save(OUT / "tower_map.png")
    return y0, canvas


def toad_world_y(cap, f):
    tb = toad_box(cap, f)
    if not tb:
        return None
    return camy(cap, f) + (tb[1] + tb[3]) / 2, (tb[0] + tb[2]) / 2


def track_run(capname):
    cap = cap_of(capname)
    a, b = L12[capname]
    pts = []
    last = (0, 128)
    for f in range(a, b):
        p = toad_world_y(cap, f)
        if p:
            last = p
        pts.append(last)
    return pts


def render(speed=10, name="s07_tower"):
    y0, mp = build_map()
    MH = mp.shape[0]
    fin, wip = track_run("cap14"), track_run("capwip")
    n_f, n_w = len(fin), len(wip)
    nout = int(n_w / speed) + int(2.5 * NES_FPS)
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(nout / NES_FPS + 1)
    mapimg = Image.fromarray(mp)
    S = 3.0                                             # main view scale
    view_w, view_h = int(256 * S), H
    big = mapimg.resize((int(256 * S), int(MH * S)), Image.NEAREST)
    mini_h = H - 160
    mini = mapimg.resize((150, mini_h), Image.BILINEAR)
    mini = ImageEnhance.Brightness(mini).enhance(0.7)
    wait_f = wait_w = 0
    prev_f = prev_w = None
    done_f = done_w = None
    for i in range(nout):
        kf = min(n_f - 1, int(i * speed))
        kw = min(n_w - 1, int(i * speed))
        yf, xf = fin[kf]
        yw, xw = wip[kw]
        if kf >= n_f - 1 and done_f is None:
            done_f = i; m.add_sfx(i / NES_FPS, "ding", 0.8)
        if kw >= n_w - 1 and done_w is None:
            done_w = i; m.add_sfx(i / NES_FPS, "blip", 0.6)
        lead_y = min(yf, yw) - y0
        top = int(max(0, min(MH * S - view_h, lead_y * S - view_h * 0.45)))
        im = Image.new("RGB", (W, H), BG)
        im.paste(big.crop((0, top, view_w, top + view_h)), (120, 0))
        d = ImageDraw.Draw(im)
        for (yy, xx, col, lab) in ((yw, xw, (170, 170, 170), "FIRST RUN"), (yf, xf, TOAD, "FINAL")):
            oy = (yy - y0) * S - top
            ox = 120 + xx * S
            if -60 < oy < H + 60:
                d.ellipse((ox - 22, oy - 22, ox + 22, oy + 22), outline=col, width=6)
                chip(d, ox + 30, oy, lab, col, 26, anchor="lt" if col == TOAD else "lb")
        # minimap
        mx, my = 1040, 110
        im.paste(mini, (mx, my))
        d.rectangle((mx - 3, my - 3, mx + 153, my + mini_h + 3), outline=(60, 80, 64), width=3)
        for (yy, col) in ((yw, (170, 170, 170)), (yf, TOAD)):
            py = my + (yy - y0) / MH * mini_h
            d.polygon([(mx - 30, py - 14), (mx - 6, py), (mx - 30, py + 14)], fill=col)
        d.text((mx + 75, 60), "THE TOWER", font=mono(30, True), fill=TEXT, anchor="mm")
        # timers + waiting
        tx = 1300
        d.text((tx, 120), "LEVEL 12: THE TOWER", font=font("ROCKEB.TTF", 40), fill=(200, 120, 255))
        for j, (lab, k, n_, wt, col, dn) in enumerate((("FIRST RUN", kw, n_w, wait_w, (190, 190, 190), done_w),
                                                     ("FINAL RUN", kf, n_f, wait_f, TOAD, done_f))):
            y = 240 + j * 330
            d.text((tx, y), lab, font=mono(34, True), fill=col)
            t = k / NES_FPS
            d.text((tx, y + 46), f"{int(t // 60)}:{t % 60:05.2f}", font=mono(96, True), fill=WHITE if dn is None else col)
            if dn is not None:
                chip(d, tx + 420, y + 10, "TOP", col, 30)
        if done_f is not None:
            gap = (n_w - n_f) / NES_FPS
            a = min(1, (i - done_f) / 12)
            d.text((tx, 830), "FINAL RUN IS AHEAD BY", font=mono(30, True), fill=tuple(int(c * a) for c in TEXT))
            d.text((tx, 870), f"{gap:.1f} SECONDS", font=font("ROCKEB.TTF", 72), fill=tuple(int(c * a) for c in GOLD))
        d.text((tx, H - 70), f"{speed}x SPEED", font=mono(30, True), fill=DIM)
        # the fun part: a seizure warning while it speeds up, then a countdown to the top
        t_s = i / NES_FPS
        left = max(0.0, (n_f - 1) / speed / NES_FPS - t_s)
        if t_s < 2.2:
            on = int(t_s * 8) % 2 == 0
            bw, bh = 1000, 150
            bx, by = 120 + (768 - bw) // 2 + 100, 380
            stripe = Image.new("RGB", (bw, bh), (20, 20, 20))
            sd = ImageDraw.Draw(stripe)
            for x in range(-bh, bw, 60):
                sd.polygon([(x, bh), (x + 30, bh), (x + 30 + bh, 0), (x + bh, 0)], fill=GOLD if on else (60, 50, 10))
            sd.rectangle((14, 14, bw - 15, bh - 15), fill=(0, 0, 0))
            sd.text((bw // 2, 52), "SEIZURE WARNING", font=font("ROCKEB.TTF", 64), fill=GOLD if on else RED, anchor="mm")
            sd.text((bw // 2, 108), "THE TOWER AT 10x SPEED", font=mono(30, True), fill=WHITE, anchor="mm")
            k = ease_out_back(min(1, t_s / 0.25))
            st = stripe.resize((max(1, int(bw * k)), max(1, int(bh * k))))
            im.paste(st, (bx + (bw - st.width) // 2, by + (bh - st.height) // 2))
            if t_s < 0.15:
                im = flash(im, t_s / 0.15)
            d = ImageDraw.Draw(im)
        if t_s >= 1.8:
            a = min(1, (t_s - 1.8) / 0.3)
            d.rectangle((140, 40, 640, 150), fill=(0, 0, 0))
            d.rectangle((140, 40, 152, 150), fill=GOLD)
            if done_f is None:
                d.text((172, 58), "TOWER CLEARED IN", font=mono(26, True), fill=tuple(int(c * a) for c in TEXT))
                d.text((172, 88), f"{left:4.1f} s", font=mono(56, True), fill=tuple(int(c * a) for c in GOLD))
            else:
                d.text((172, 70), "CLEARED!", font=font("ROCKEB.TTF", 56), fill=TOAD)
        w.put(vignette(im, 0.25))
    m.add_sfx(0, "whoosh", 0.6)
    for k in range(int(2.0 / 0.25)):                   # warning beeps under the banner
        m.add_sfx(0.1 + k * 0.25, "blip", 0.35)
    w.close()
    m.write(CLIPS / f"{name}.wav", w.n / NES_FPS)
    print(name, w.n / NES_FPS, "s; first run", n_w, "final", n_f, "waits", wait_w, wait_f)


if __name__ == "__main__":
    render()
