"""Game-footage shots: a following camera, speed changes and slow motion, and overlay callbacks.

game_shot(...) yields 1920x1080 PIL frames. `row` = the RAM-capture row (0-based input index) shown in that frame;
capture frame = lead + row."""
from __future__ import annotations

import json

from fx import *  # noqa: F401,F403

LEADS = {"cap14": 6}
DATA_SHIFT = 1        # fallback for captures without a sync map
_SYNC = json.loads((HERE / "cap14_sync.json").read_text()) if (HERE / "cap14_sync.json").exists() else []


def data_row(capname, row):
    """the RAM/OAM row matching the picture of capture frame lead+row. For cap14 the capture repeats a frame every
    ~8,000 frames, so the offset steps from 5 down to 0 over the run (cap14_sync.json, measured by run1080's agent)."""
    if capname == "cap14" and _SYNC:
        df = 0
        for s in _SYNC:
            if row + 1 >= s["from"]:
                df = s["df"]
        return row + df
    return row + DATA_SHIFT
SRCS = {"cap14": VIDEO / "up14.mkv", "capwip": VIDEO / "fullrun_wip.mkv"}
_CAPS = {}


def cap_of(name):
    if name not in _CAPS:
        _CAPS[name] = Cap(name)
    return _CAPS[name]


def lead_of(name):
    if name not in LEADS:
        if name == "capwip":
            p = HERE / "wip_frames.txt"
            total = int(p.read_text().strip()) if p.exists() and p.read_text().strip() else None
            LEADS[name] = (total - cap_of(name).n) if total else 0
        else:
            LEADS[name] = lead_in(SRCS[name], cap_of(name).n)
    return LEADS[name]


def game_shot(capname, row0, nout, speed=1.0, slow=(), scale=8.0, follow=0.14, target="toad", draw=None,
              start_center=None, zoom=None, post=None):
    """nout output frames starting at capture row row0.
    speed: rows advanced per output frame outside slow-motion windows; slow: [(row_a, row_b, factor)] where each
    row is held `factor` output frames. target: 'toad' (camera follows the toad's sprites), (x,y) fixed, or None.
    zoom: optional fn(i, n) -> scale. draw(im, d, cam, row, i, info) adds overlays; post(im, i) -> im."""
    cap = cap_of(capname)
    src = SRCS[capname]
    lead = lead_of(capname)
    # how many source rows are needed
    rows = []
    r = float(row0)
    while len(rows) < nout:
        ri = int(r)
        k = next((f for a, b, f in slow if a <= ri <= b), None)
        if k:
            rows += [ri] * int(k)
            r += 1
        else:
            rows.append(ri)
            r += speed
    rows = rows[:nout]
    need = rows[-1] - rows[0] + 1
    frames = nes_frames(src, lead + rows[0], need)
    cur_row, cur = rows[0] - 1, None
    cam = Camera(scale, follow=follow)
    if start_center:
        cam.cx, cam.cy = start_center
    else:
        tb = toad_box(cap, rows[0]) if target == "toad" else None
        if tb:
            cam.cx, cam.cy = (tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2
        elif isinstance(target, tuple):
            cam.cx, cam.cy = target
    for i, row in enumerate(rows):
        while cur_row < row:
            cur = next(frames)
            cur_row += 1
        if zoom:
            cam.scale = zoom(i, nout)
        if target == "toad":
            tb = toad_box(cap, min(data_row(capname, row), cap.n - 1))
            if tb:
                cam.toward((tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2)
        elif isinstance(target, tuple):
            cam.toward(*target)
        im = cam.render(cur)
        im = scanlines(im, 0.10)
        d = ImageDraw.Draw(im)
        if draw:
            draw(im, d, cam, min(data_row(capname, row), cap.n - 1), i, dict(cap=cap, nes=cur, slow=any(a <= row <= b for a, b, _ in slow)))
        if post:
            im = post(im, i)
        yield im


# ---------------------------------------------------------------- common overlay pieces
def track(d, cam, cap, row, names=None, toad=True, enemy_col=RED, hp=True, only=None):
    """brackets + labels on the toad and named enemies; returns {name: box_out}. An enemy label that would sit on the
    toad's label goes under the enemy's box instead."""
    out = {}
    found = objects_on_screen(cap, row)
    tl = None
    for box, o in found:
        if o and o["slot"] == 0:
            x0, y0 = cam.to_out(box[0], box[1]); x1, y1 = cam.to_out(box[2], box[3])
            if toad:
                brackets(d, (x0, y0, x1, y1), TOAD, 6, grow=6)
                tl = chip(d, x0 - 6, y0 - 12, "TOAD", TOAD, 30)
            out["TOAD"] = (x0, y0, x1, y1)
    for box, o in found:
        if not o or o["slot"] == 0:
            continue
        x0, y0 = cam.to_out(box[0], box[1]); x1, y1 = cam.to_out(box[2], box[3])
        nm = (names or {}).get(o["id"] & 0x7F) or obj_name(cap, row, o)
        if not nm or (only and nm not in only):
            continue
        brackets(d, (x0, y0, x1, y1), enemy_col, 6, grow=6)
        text = f"{nm}  HP {o['hp']}" if hp else nm
        f = mono(30, True)
        wdt = d.textlength(text, font=f) + 16
        y_lab = y0 - 12
        if tl and x0 - 6 < tl[2] and x0 - 6 + wdt > tl[0] and y_lab - 44 < tl[3] and y_lab > tl[1]:
            chip(d, x0 - 6, y1 + 14, text, enemy_col, 30, fg=WHITE, anchor="lt")
        else:
            chip(d, x0 - 6, y_lab, text, enemy_col, 30, fg=WHITE)
        out[nm] = (x0, y0, x1, y1)
    return out


def tag(im, text, i, sub=None, col=TOAD, y=70):
    """corner tag that slides in from the left: a level / shot label"""
    d = ImageDraw.Draw(im)
    k = ease(min(1, i / 10))
    f = font("ROCKEB.TTF", 46)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    w = r - l + 60
    x = -w + (w + 50) * k
    d.polygon([(x, y), (x + w, y), (x + w - 22, y + 72), (x - 22, y + 72)], fill=(0, 0, 0))
    d.polygon([(x + 6, y + 6), (x + w - 6, y + 6), (x + w - 26, y + 66), (x - 14, y + 66)], fill=col)
    d.text((x + 24 - l, y + 36), text, font=f, fill=(0, 0, 0), anchor="lm")
    if sub:
        fs = mono(30, True)
        sx = x + 10
        d.rectangle((sx, y + 80, sx + d.textlength(sub, font=fs) + 24, y + 124), fill=(0, 0, 0))
        d.text((sx + 12, y + 102), sub, font=fs, fill=col, anchor="lm")
    return im


def readout(d, x, y, label, value, col=GOLD, big=64):
    """a big number with a small label above it (for speed / height / distance meters)"""
    d.text((x, y), label, font=mono(26, True), fill=col)
    fb = mono(big, True)
    for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3), (3, 3)):
        d.text((x + ox, y + 30 + oy), value, font=fb, fill=(0, 0, 0))
    d.text((x, y + 30), value, font=fb, fill=WHITE)
