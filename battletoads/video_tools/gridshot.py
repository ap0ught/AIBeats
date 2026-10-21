"""The emulator grid: 24 real attempts at the same stretch, each with one input changed, playing at once.
Crashes get marked as they happen; the one that makes it is the real run, and it zooms to full screen."""
from __future__ import annotations

import json

from fx import *  # noqa: F401,F403
from shots import tag


def grid_frames(name="grid_tt", lead=5, a0=140, a1=496, speed=2, cols=6, rows_=4, survivor_tile=15,
                header="ONE INPUT CHANGED PER ATTEMPT", zoom_out=14, pick_seed=0, mark_delay=-40, fail_label="CRASH",
                fail_count="CRASHED"):
    g = json.load(open(HERE / f"{name}.json"))
    L = g["L"]
    real = g["variants"][0]
    base_change = real["changes"][0][0] if real["changes"] else None
    deaths = [v for v in g["variants"][1:] if v["changes"] and v["changes"][0][0] != base_change
              and a0 + 60 <= v["changes"][0][0] + mark_delay <= a1 - 10]
    deaths.sort(key=lambda v: v["changes"][0][0])
    n_tiles = cols * rows_
    chosen = deaths[:n_tiles - 1]
    while len(chosen) < n_tiles - 1:                   # pad with other attempts if needed
        chosen.append(g["variants"][1 + len(chosen)])
    order = chosen[:]
    order.insert(survivor_tile, real)
    tw, th = W // cols, H // rows_
    src = VIDEO / f"{name}.mkv"
    gens = [nes_frames(src, lead + v["offset"] + a0, a1 - a0 + 1) for v in order]
    cur = [None] * n_tiles
    nout = (a1 - a0) // speed
    crashed_at = {}
    for idx, v in enumerate(order):
        if v is not real and v["changes"]:
            crashed_at[idx] = v["changes"][0][0] + mark_delay
    fx_big = font("ROCKEB.TTF", 64)
    for i in range(nout + zoom_out):
        row = a0 + min(i, nout - 1) * speed
        for t in range(n_tiles):
            for _ in range(speed if i and i < nout else (1 if i == 0 else 0)):
                try:
                    cur[t] = next(gens[t])
                except StopIteration:
                    pass
        im = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(im)
        n_crash = 0
        for t in range(n_tiles):
            cx, cy = (t % cols) * tw, (t // cols) * th
            g0 = cur[t].crop((0, 40, 256, 224))          # drop the score bar
            tile = g0.resize((tw, int(184 * tw / 256)), Image.NEAREST)
            top = max(0, (tile.height - th) // 2)
            tile = tile.crop((0, top, tw, top + th))
            ca = crashed_at.get(t)
            dead = ca is not None and row >= ca
            if dead:
                n_crash += 1
                k = min(1, (row - ca) / 30)
                tile = Image.blend(tile, ImageEnhance.Color(tile).enhance(0).point(lambda p: p * 0.5), 0.6 * k)
                red = Image.new("RGB", tile.size, (150, 0, 0))
                tile = Image.blend(tile, red, 0.35 * k)
            im.paste(tile, (cx, cy))
            if dead:
                k = min(1, (row - ca) / 8)
                s = int(40 + 30 * (1 - k))
                mx, my = cx + tw // 2, cy + th // 2
                d.line((mx - s, my - s, mx + s, my + s), fill=(255, 40, 40), width=12)
                d.line((mx - s, my + s, mx + s, my - s), fill=(255, 40, 40), width=12)
                chip(d, cx + 10, cy + th - 10, fail_label, RED, 24, fg=WHITE)
            d.rectangle((cx, cy, cx + tw - 1, cy + th - 1), outline=(0, 0, 0), width=3)
            chip(d, cx + 8, cy + 8, f"#{order[t]['v'] + 1:02d}", (0, 0, 0), 20, fg=DIM, anchor="lt")
        # survivor highlight once most have crashed
        sx, sy = (survivor_tile % cols) * tw, (survivor_tile // cols) * th
        if row > a0 + (a1 - a0) * 0.6:
            pulse = 0.5 + 0.5 * math.sin(i * 0.5)
            d.rectangle((sx + 2, sy + 2, sx + tw - 3, sy + th - 3), outline=tuple(int(c * (0.6 + 0.4 * pulse)) for c in GOLD), width=8)
            chip(d, sx + tw // 2, sy + th - 10, "MADE IT", GOLD, 26, anchor="mb")
        # header + counter
        d.rectangle((0, 0, W, 64), fill=(0, 0, 0))
        d.text((40, 32), header, font=mono(34, True), fill=TOAD, anchor="lm")
        d.text((W - 40, 32), f"{fail_count} {n_crash:2d}   MADE IT 1", font=mono(34, True), fill=GOLD, anchor="rm")
        if i >= nout:                                   # zoom the survivor to full screen
            k = ease((i - nout + 1) / zoom_out)
            surv = cur[survivor_tile]
            x0, y0 = sx * (1 - k), sy * (1 - k)
            ww, hh = tw + (W - tw) * k, th + (H - th) * k
            big = surv.resize((int(ww), int(ww * 224 / 256)), Image.NEAREST)
            top = (big.height - int(hh)) // 2
            big = big.crop((0, top, int(ww), top + int(hh)))
            im.paste(big, (int(x0), int(y0)))
        yield im


if __name__ == "__main__":
    w = Writer(OUT / "grid_test.mp4")
    for im in grid_frames():
        w.put(im)
    w.close()
    print(w.n)
