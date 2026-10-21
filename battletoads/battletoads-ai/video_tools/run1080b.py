"""A captured run at 1920x1080 (2026-10-10, the corrected run): the game at 5x on the left, the AI panel on the right
(640 px), and a cue track (yt/run_cues_<name>.json) of level slams, research credits and the final card.

    python yt/run1080b.py --name run1201 --chunks 6               # writes yt/out/run_<name>.mp4
    RENDER_RANGE=1900,2000 python yt/run1080b.py --name run1201   # preview of input frames a..b with audio

<name> is what yt/run_capture.py recorded and yt/run_text.py wrote the text for. Differences from run1080.py:
- the clock stops at the cut to Professor T. Bird (logs/<name>.levels.json) and the capture runs on into his screen;
  the final card comes up over the live picture and the last frame is held for the cue's `dur`;
- level splits end on each level's first black frame; the record's are knowledge/wr_splits_v2.json;
- every output frame shows the exact picture of its emulated frame (capsync.py drops the dump's repeated frames), so a
  frame count on this video gives the run's real time; the sound is squeezed by the same 0.01 %.
Frame numbers are 1-based input frames. No burned-in captions (the owner forbids them).
"""
from __future__ import annotations

import argparse
import bisect
import json
import os
import subprocess
import sys
import time
from pathlib import Path

YT = Path(__file__).resolve().parent
sys.path.insert(0, str(YT))
sys.path.insert(0, str(YT.parent))

from PIL import Image, ImageDraw, ImageEnhance  # noqa: E402

import style as S  # noqa: E402
import fx  # noqa: E402
from capsync import Sync  # noqa: E402
from render_overlay import load, token_at, fmt_run, fmt_delta, fmt_tok  # noqa: E402

NAME = next((sys.argv[i + 1] for i, a_ in enumerate(sys.argv[:-1]) if a_ == "--name"), os.environ.get("RUN_NAME", "run1201"))
SRC = S.VIDEO / f"{NAME}.mkv"
CUES = YT / f"run_cues_{NAME}.json"
OUTFILE = S.OUT / f"run_{NAME}.mp4"
W, H = 1920, 1080
GW, GH = 1280, 1080            # game area: NES rows 4..219 at 5x
SC = 5
TOP = 4                        # first NES row shown
PX = 1280                      # panel x
M = 32                         # panel margin
X0, X1 = PX + M, W - M         # panel content box
CW = X1 - X0                   # 576
BG, PANEL, GRID, DIM, TEXT, TOAD, GOLD, RED, WHITE = S.BG, S.PANEL, S.GRID, S.DIM, S.TEXT, S.TOAD, S.GOLD, S.RED, S.WHITE
GREEN = (90, 230, 110)
SEP = (34, 50, 40)
CELL = (20, 30, 24)
CELL_LINE = (44, 60, 50)
PAD_OFF = (40, 52, 44)
LABEL = (120, 140, 126)


def mono(size, bold=False):
    return S.mono(size, bold)


F = dict(label=mono(16, True), timer=mono(54, True), wr=mono(54, True), note=mono(20), cell=mono(16, True),
         rowlab=mono(17, True), frame=mono(18), hold=mono(22, True), holdlab=mono(15, True), ctl=mono(13, True),
         tile_lab=mono(14, True), tile_val=mono(24, True), tok=mono(46, True), cost=mono(26, True), tokunit=mono(16, True),
         part=mono(16, True), stream=mono(17))


def charw(f):
    return f.getlength("M")


def wrap(text, f, width, max_lines):
    """word wrap to a pixel width (monospace); returns (lines, overflowed)"""
    n = max(8, int(width // charw(f)))
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        if not cur:
            cur = w_
        elif len(cur) + 1 + len(w_) <= n:
            cur += " " + w_
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    lines = [l if len(l) <= n else l[:n - 1] + "…" for l in lines]
    if len(lines) > max_lines:
        last = lines[max_lines - 1]
        lines = lines[:max_lines - 1] + [(last[:n - 1].rstrip() + "…") if len(last) >= n - 1 else last + "…"]
        return lines, True
    return lines, False


def fit_wrap(text, sizes, bold, width, max_lines):
    """largest font in `sizes` whose wrap fits max_lines"""
    for s in sizes:
        f = mono(s, bold)
        lines, over = wrap(text, f, width, max_lines)
        if not over:
            return f, lines
    return f, lines


# ------------------------------------------------------------------------------------------------ data
class Run:
    def __init__(self):
        self.inputs, self.events, self.trace = load(NAME)
        self.n = len(self.inputs)
        self.ev_frames = [e[0] for e in self.events]
        self.keys = json.loads((S.LOGS / f"{NAME}.tokens.json").read_text(encoding="utf-8"))
        self.wr = json.loads((S.TOADS / "knowledge" / "wr_splits_v2.json").read_text(encoding="utf-8"))
        lv = json.loads((S.LOGS / f"{NAME}.levels.json").read_text(encoding="utf-8"))
        self.clock, self.finish = lv["clock"], lv["finish"]
        self.levels = [tuple(x) for x in lv["levels"]]        # (level byte, enter frame, end = first black frame)
        self.cues = json.loads(CUES.read_text(encoding="utf-8")) if CUES.exists() else []
        self.final = next((c for c in self.cues if c["type"] == "final"), None)
        self.hold = S.nframes(self.final.get("dur", 1.5)) if self.final else 0
        self.sync = Sync(NAME)


# ------------------------------------------------------------------------------------------------ panel
def label(d, x, y, text, col=LABEL):
    """section label: a small green tick and spaced capitals"""
    d.rectangle((x, y + 2, x + 3, y + 13), fill=TOAD if col == LABEL else col)
    f = F["label"]
    step = charw(f) + 2.2
    for i, ch in enumerate(text):
        d.text((x + 12 + i * step, y), ch, font=f, fill=col)


# vertical layout of the panel (top y of each block)
Y_TITLE = 26
Y_TIMELAB = 94
Y_TIMER = 116
Y_NOTE = 180
Y_RACE = 214
Y_SEP1 = 286
Y_WHAT = 302
Y_SEP2 = 540
Y_INPUT = 556
Y_SEP3 = 714
Y_RAM = 730
Y_SEP4 = 856
Y_TOK = 872


def panel_base(run):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((PX, 0, W, H), fill=PANEL)
    for gy in range(0, H, 6):                   # a faint scanline texture on the panel
        if gy % 12 == 0:
            d.line((PX, gy, W, gy), fill=(14, 21, 16))
    d.line((PX, 0, PX, H), fill=(44, 70, 52), width=2)
    d.line((PX + 2, 0, PX + 2, H), fill=(16, 26, 19), width=2)
    lg = fx.logo("AI CONTROLLER", 40, top=(210, 255, 140), bottom=(70, 180, 40), extrude=(18, 60, 12))
    if lg.width > CW - 170:
        lg = lg.resize((CW - 170, int(lg.height * (CW - 170) / lg.width)), Image.LANCZOS)
    im.paste(lg, (X0 - 4, Y_TITLE + 32 - lg.height // 2), lg)
    label(d, X0, Y_TIMELAB, "RUN TIME")
    label(d, X0 + 300, Y_TIMELAB, "WORLD RECORD", col=(190, 160, 70))
    d.text((X1, Y_TIMELAB - 1), "jay_cee", font=mono(17), fill=(190, 160, 70), anchor="ra")
    d.text((X0 + 300, Y_TIMER), fmt_run(run.wr["total"]), font=F["wr"], fill=GOLD)
    for y in (Y_SEP1, Y_SEP2, Y_SEP3, Y_SEP4):
        d.line((X0, y, X1, y), fill=SEP, width=1)
    label(d, X0, Y_WHAT, "WHAT  /  WHY")
    label(d, X0, Y_INPUT, "INPUT")
    label(d, X0 + 300, Y_INPUT, "FRAME STREAM")
    label(d, X0, Y_RAM, "READ FROM RAM")
    label(d, X0, Y_TOK, "TOKENS SPENT BUILDING THIS RUN")
    return im


def draw_race(d, x0, y0, wr, t, levels, k, finish):
    lv = wr["levels"]
    lx = x0 + 44
    cw = (X1 - lx) / len(lv)

    def wr_pos():
        prev = 0.0
        for i, L in enumerate(lv):
            if t < L["end"]:
                return i + max(0.0, t - prev) / max(0.01, L["end"] - prev)
            prev = L["end"]
        return float(len(lv))

    def ai_pos():
        order = [L["byte"] for L in lv]
        cur = None
        for b, a, e in levels:
            if a <= k:
                cur = (b, a, e)
        if cur is None or cur[0] not in order or t < 0:
            return 0.0
        if finish and k >= finish:
            return float(len(lv))
        b, a, e = cur
        i = order.index(b)
        if e is None:
            dur = (lv[i]["end"] - (lv[i - 1]["end"] if i else 0.0)) * S.NES_FPS
            return i + min(0.98, (k - a) / max(1.0, dur))
        return i + min(1.0, (k - a) / max(1, e - a))

    rh, gap = 26, 10
    for row, (lab, pos, col) in enumerate((("WR", wr_pos() if t >= 0 else 0.0, GOLD), ("AI", ai_pos(), TOAD))):
        y = y0 + row * (rh + gap)
        d.text((x0, y + rh // 2), lab, font=F["rowlab"], fill=col, anchor="lm")
        for i, L in enumerate(lv):
            cx0 = lx + i * cw
            cx1 = lx + (i + 1) * cw - 4
            d.rectangle((cx0, y, cx1, y + rh), fill=CELL, outline=CELL_LINE)
            fill = max(0.0, min(1.0, pos - i))
            if fill > 0:
                d.rectangle((cx0 + 1, y + 1, cx0 + 1 + (cx1 - cx0 - 2) * fill, y + rh - 1),
                            fill=tuple(int(c * 0.5) for c in col))
        mx = min(lx + min(len(lv), pos) * cw, X1)
        d.rectangle((mx - 1, y - 4, mx + 1, y + rh + 4), fill=col)
        for i, L in enumerate(lv):
            cx0, cx1 = lx + i * cw, lx + (i + 1) * cw - 4
            d.text(((cx0 + cx1) / 2, y + rh / 2 + 1), str(L["num"]), font=F["cell"],
                   fill=WHITE if pos - i >= 1 else TEXT, anchor="mm", stroke_width=2, stroke_fill=CELL)


def draw_controller(d, x, y, held, s=1.0):
    """NES pad, 250 x 94 at s=1"""
    def c(on):
        return TOAD if on else PAD_OFF
    w_, h_ = int(250 * s), int(94 * s)
    d.rounded_rectangle((x, y, x + w_, y + h_), radius=int(10 * s), fill=(26, 34, 29), outline=(62, 80, 68), width=2)
    cx, cy, a = x + int(48 * s), y + h_ // 2, int(12 * s)
    d.rectangle((cx - a, cy - 3 * a, cx + a, cy + 3 * a), fill=(46, 58, 50))
    d.rectangle((cx - 3 * a, cy - a, cx + 3 * a, cy + a), fill=(46, 58, 50))
    d.rectangle((cx - a + 1, cy - 3 * a + 1, cx + a - 1, cy - a), fill=c("Up" in held))
    d.rectangle((cx - a + 1, cy + a, cx + a - 1, cy + 3 * a - 1), fill=c("Down" in held))
    d.rectangle((cx - 3 * a + 1, cy - a + 1, cx - a, cy + a - 1), fill=c("Left" in held))
    d.rectangle((cx + a, cy - a + 1, cx + 3 * a - 1, cy + a - 1), fill=c("Right" in held))
    for i, (b, lab) in enumerate((("Select", "SEL"), ("Start", "START"))):
        bx = x + int((96 + i * 44) * s)
        d.rounded_rectangle((bx, cy + 2, bx + int(32 * s), cy + 2 + int(12 * s)), radius=int(6 * s), fill=c(b in held))
        d.text((bx + int(16 * s), cy + int(22 * s)), lab, font=F["ctl"], fill=DIM, anchor="mt")
    for i, b in enumerate(("B", "A")):
        bx = x + int((198 + i * 33) * s)
        r = int(14 * s)
        d.ellipse((bx - r, cy - r - 6, bx + r, cy + r - 6), fill=(RED if b in held else PAD_OFF), outline=(96, 34, 30), width=2)
        d.text((bx, cy + int(22 * s)), b, font=F["ctl"], fill=DIM, anchor="mt")


ABBR = {"Right": "R", "Left": "L", "Up": "U", "Down": "D", "A": "A", "B": "B", "Start": "St", "Select": "Se"}


def stream_line(run, k):
    inp = run.inputs[k - 1]
    kv = run.trace.get(k, {})
    wx = kv.get("x", 0) + 256 * ((kv.get("xh", 0) + 128) % 256 - 128)
    s = "+".join(ABBR.get(b, b) for b in inp) or "-"
    return f"{k:05d}  {s[:7]:<7} x={wx:>3} y={kv.get('y', 0):>3}"


def draw_panel(im, run, k):
    d = ImageDraw.Draw(im)
    inputs, trace, wr = run.inputs, run.trace, run.wr
    d.text((X1, Y_TITLE + 22), f"FRAME {k:05d}", font=F["frame"], fill=DIM, anchor="rm")
    # ---- run time + note + race
    kk = min(k, run.finish) if run.finish else k
    started = bool(run.clock and k >= run.clock)
    rt = (kk - run.clock) / S.NES_FPS if started else 0.0
    d.text((X0, Y_TIMER), fmt_run(rt), font=F["timer"], fill=WHITE if started else DIM)
    note, ncol = ("clock starts when the toad lands" if not started else ""), DIM
    for b, a, e in run.levels:
        wl = next((L for L in wr["levels"] if L["byte"] == b), None)
        if started and e and e <= k and wl:
            dt = (e - run.clock) / S.NES_FPS - wl["end"]
            note = f"after level {wl['num']}: {fmt_delta(dt)} vs the record"
            ncol = RED if dt > 0 else GREEN
    if run.finish and k >= run.finish:
        note = f"FINAL: {fmt_delta(rt - wr['total'])} vs the record"
        ncol = RED if rt > wr["total"] else GREEN
    if note:
        if ncol != DIM:
            d.ellipse((X0, Y_NOTE + 5, X0 + 10, Y_NOTE + 15), fill=ncol)
            d.text((X0 + 20, Y_NOTE), note, font=F["note"], fill=ncol)
        else:
            d.text((X0, Y_NOTE), note, font=F["note"], fill=ncol)
    draw_race(d, X0, Y_RACE, wr, rt if started else -1.0, run.levels, k, run.finish)
    # ---- what / why
    ti = bisect.bisect_right(run.ev_frames, k) - 1
    if ti >= 0:
        head, _, why = run.events[ti][1].partition("||")
        fh, hl = fit_wrap(head, (23, 22, 21, 20), True, CW, 4)
        y = Y_WHAT + 28
        lh = int(fh.size * 1.27)
        for line in hl:
            d.text((X0, y), line, font=fh, fill=TOAD)
            y += lh
        y += 8
        if why:
            fw, wl_ = fit_wrap(why, (19, 18, 17), False, CW - 16, 3)
            d.line((X0 + 2, y + 2, X0 + 2, y + len(wl_) * int(fw.size * 1.3) - 6), fill=(70, 90, 76), width=3)
            for line in wl_:
                d.text((X0 + 16, y), line, font=fw, fill=TEXT)
                y += int(fw.size * 1.3)
    # ---- input + frame stream
    held = set(inputs[k - 1])
    draw_controller(d, X0, Y_INPUT + 28, held)
    d.text((X0, Y_INPUT + 140), "HOLDING", font=F["holdlab"], fill=DIM, anchor="lm")
    d.text((X0 + 76, Y_INPUT + 140), " + ".join(inputs[k - 1]) if inputs[k - 1] else "(nothing)", font=F["hold"],
           fill=TOAD if inputs[k - 1] else DIM, anchor="lm")
    sx = X0 + 300
    rows = [j for j in range(k - 4, k + 1) if j >= 1]
    for i, j in enumerate(rows):
        age = k - j
        sh = max(70, 210 - age * 32)
        d.text((sx, Y_INPUT + 30 + (5 - len(rows) + i) * 24), stream_line(run, j), font=F["stream"],
               fill=TOAD if age == 0 else (sh, sh + 8, sh))
    # ---- RAM tiles (4 x 2)
    kv = trace.get(k, {})
    if kv:
        hp = sum(1 for i in range(6) if kv.get(f"hud{i}") == 244)
        foes = sum(1 for s in range(2, 8) if kv.get(f"id{s}") and kv.get(f"hp{s}") and kv.get(f"id{s}") not in (6, 34))
        wx = kv.get("x", 0) + 256 * ((kv.get("xh", 0) + 128) % 256 - 128)
        cam = kv.get("cam_lo", kv.get("camera", 0)) + 256 * kv.get("cam_hi", 0)
        tiles = [("TOAD X", str(wx)), ("TOAD Y", str(kv.get("y", 0))), ("HEIGHT", str(kv.get("height", 0))),
                 ("CAMERA", str(cam)), ("HEALTH", None), ("LIVES", str(kv.get("lives", 0))),
                 ("ENEMIES", str(foes)), ("LEVEL", str(kv.get("level", 0)))]
        tw = CW / 4
        for i, (lab, val) in enumerate(tiles):
            tx, ty = X0 + (i % 4) * tw, Y_RAM + 28 + (i // 4) * 48
            d.text((tx, ty), lab, font=F["tile_lab"], fill=DIM)
            if val is None:
                for p in range(6):
                    on = p < hp
                    d.rectangle((tx + p * 18, ty + 21, tx + p * 18 + 13, ty + 39), fill=TOAD if on else PAD_OFF)
            else:
                d.text((tx, ty + 17), val, font=F["tile_val"], fill=TEXT)
    # ---- tokens
    tk = token_at(run.keys, k)
    if tk:
        tok, cost, lab = tk
        y = Y_TOK + 24
        d.text((X0, y), f"{int(tok):,}", font=F["tok"], fill=GOLD)
        d.text((X1, y + 2), f"~${cost:,.2f}", font=F["cost"], fill=GOLD, anchor="ra")
        d.text((X1, y + 34), "AT API PRICES", font=F["tokunit"], fill=(160, 135, 60), anchor="ra")
        y += 56
        seg = next(((a, b) for a, b in zip(run.keys, run.keys[1:]) if a["frame"] <= k < b["frame"]), None)
        if seg is None and len(run.keys) > 1 and k >= run.keys[-1]["frame"]:
            seg = (run.keys[-2], run.keys[-1])
        if seg:
            a, b = seg
            d.text((X0, y), f"THIS PART COST {fmt_tok(b['tokens'] - a['tokens'])} TOKENS (~${b['cost'] - a['cost']:,.0f})"
                            f" TO WORK OUT:", font=F["part"], fill=GOLD)
            why = b.get("why", b.get("label", ""))
            fw, lines = fit_wrap(why, (18, 17), False, CW, 3)
            if len(lines) == 3 and lines[-1].endswith("…"):
                fw, lines = fit_wrap(why, (17, 16), False, CW, 4)
            y += 24
            for line in lines:
                d.text((X0, y), line, font=fw, fill=TEXT)
                y += int(fw.size * 1.25)
        else:
            d.text((X0, y), lab.upper(), font=F["part"], fill=GOLD)


# ------------------------------------------------------------------------------------------------ cues over the game
_CARD = {}


def credit_card(title, body):
    key = (title, body)
    if key in _CARD:
        return _CARD[key]
    ft, fb = mono(34, True), mono(25)
    tw = max(ft.getlength(title), fb.getlength(body))
    w_, h_ = int(tw) + 8 + 30 + 34, 30 + 36 + 12 + 26 + 28
    im = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w_ - 1, h_ - 1), fill=(6, 10, 8, 222))
    d.rectangle((0, 0, 7, h_ - 1), fill=GOLD + (255,))
    d.line((8, 0, w_ - 1, 0), fill=(70, 60, 20, 255))
    d.text((8 + 30, 28), title, font=ft, fill=WHITE + (255,))
    d.text((8 + 30, 28 + 36 + 12), body, font=fb, fill=(200, 212, 200, 255))
    _CARD[key] = im
    return im


def cue_credit(g, c, t):
    card = credit_card(c["title"], c["body"])
    dur = c.get("dur", 5.0)
    tin, tout = 0.4, 0.35
    if t < tin:
        p = 1 - (1 - t / tin) ** 3
    elif t > dur - tout:
        p = 1 - S.ease((t - (dur - tout)) / tout)
    else:
        p = 1.0
    x = int(40 - (card.width + 60) * (1 - p))
    y = c.get("y", 128 if c.get("pos") == "top" else GH - 56 - card.height)
    g.paste(card, (x, y), card)


def logo_fit(text, size, maxw, **kw):
    lg = fx.logo(text, size, **kw)
    if lg.width > maxw:
        lg = lg.resize((maxw, int(lg.height * maxw / lg.width)), Image.LANCZOS)
    return lg


def game_shake(g, t, amp):
    if t >= 1:
        return g
    import random
    r = random.Random(int(t * 1000))
    a = amp * (1 - t) ** 2
    out = Image.new("RGB", g.size, (0, 0, 0))
    out.paste(g, (int(r.uniform(-a, a)), int(r.uniform(-a, a))))
    return out


def slam_logo(g, lg, t, dur, cx, cy, land=0.18, out_t=0.25, whip=True):
    """the logo half of fx.slam, centred at (cx, cy) inside the game area and clipped to it: zooms in from 2.4x,
    lands with a flash, holds, whips out to the left"""
    if t < land:
        k = t / land
        sc = 2.4 - 1.4 * S.ease(k)
        al = min(1.0, k * 2)
    else:
        sc, al = 1.0, 1.0
    xoff = 0
    if whip and t > dur - out_t:
        k = (t - (dur - out_t)) / out_t
        xoff = -int((cx + lg.width) * S.ease(k) ** 1.6)
    im = lg if abs(sc - 1) < 1e-3 else lg.resize((max(1, int(lg.width * sc)), max(1, int(lg.height * sc))), Image.BILINEAR)
    if al < 1:
        im = im.copy()
        im.putalpha(im.split()[3].point(lambda p: int(p * al)))
    g.paste(im, (int(cx - im.width / 2 + xoff), int(cy - im.height / 2)), im)
    if land <= t < land + 0.12:
        g = Image.blend(g, Image.new("RGB", g.size, WHITE), max(0.0, 0.6 * (1 - (t - land) / 0.12) ** 2))
    return g


def slam_base(g, t, dur, dark=0.4, land=0.18, fade_out=0.3):
    """the picture half of a slam: darkened while the title is up, shaken when it lands"""
    dk = 1 - S.ease((t - (dur - fade_out)) / fade_out) if t > dur - fade_out else S.ease(t / 0.12)
    if dk > 0:
        g = ImageEnhance.Brightness(g).enhance(1 - dark * dk)
    if t >= land:
        g = game_shake(g, (t - land) / 0.35, 14)
    return g


_LEVEL = {}


def level_logo(c):
    text = c["text"]
    key = (text, c.get("size", 84))
    if key not in _LEVEL:
        kicker, _, name = text.partition(": ")
        if name:
            lg_k = logo_fit(kicker, 52, GW - 120, top=(210, 255, 140), bottom=(70, 180, 40), extrude=(18, 60, 12))
            lg_n = logo_fit(name, c.get("size", 84), GW - 100)
            comb = Image.new("RGBA", (max(lg_k.width, lg_n.width), lg_k.height + lg_n.height - 4), (0, 0, 0, 0))
            comb.paste(lg_k, ((comb.width - lg_k.width) // 2, 0), lg_k)
            comb.paste(lg_n, ((comb.width - lg_n.width) // 2, lg_k.height - 4), lg_n)
            _LEVEL[key] = comb
        else:
            _LEVEL[key] = logo_fit(text, c.get("size", 84), GW - 100)
    return _LEVEL[key]


def cue_final(g, c, t, run):
    dk = S.ease(t / 0.35)
    g = ImageEnhance.Brightness(g).enhance(1 - 0.62 * dk)
    lg = logo_fit(c.get("text", ""), 210, GW - 120)
    if t >= 0.18:
        g = game_shake(g, (t - 0.18) / 0.35, 14)
    g = slam_logo(g, lg, t, 99, GW // 2, 470, whip=False)
    if t > 0.25:
        k = S.ease((t - 0.25) / 0.3)
        d = ImageDraw.Draw(g)
        sub = c.get("sub", "")
        f = S.font("arialbd.ttf", 42)
        y = 470 + lg.height // 2 + 40 + int((1 - k) * 24)
        col = tuple(int(v * k) for v in WHITE)
        for ox, oy in ((-3, 0), (3, 0), (0, -3), (0, 3), (3, 3)):
            d.text((GW // 2 + ox, y + oy), sub, font=f, fill=(0, 0, 0), anchor="mt")
        d.text((GW // 2, y), sub, font=f, fill=col, anchor="mt")
        d.line((GW // 2 - 220, y + 66, GW // 2 + 220, y + 66), fill=tuple(int(v * k) for v in GOLD), width=3)
        d.text((GW // 2, y + 82), c.get("sub2", "1 player  ·  human speedrun rules  ·  every input chosen by the AI"),
               font=S.font("arialbd.ttf", 28), fill=tuple(int(v * k) for v in (200, 212, 200)), anchor="mt")
    return g


def game_frame(nes, run, k, hold_t=None):
    """the 1280x1080 game area for input frame k with the cues active at k drawn over it; from the final cue's frame on
    the final card lies over the live picture (hold_t: seconds into the frozen last frame)"""
    g = nes.crop((0, TOP, 256, TOP + 216)).resize((GW, GH), Image.NEAREST)
    if run.final and k >= run.final["frame"]:
        return cue_final(g, run.final, (k - run.final["frame"]) / S.NES_FPS + (hold_t or 0.0), run)
    act = []
    for c in run.cues:
        if c["type"] == "final":
            continue
        dur = c.get("dur", 1.6 if c["type"] == "level" else 5.0)
        if c["frame"] <= k < c["frame"] + S.nframes(dur):
            act.append((c, (k - c["frame"]) / S.NES_FPS))
    for c, t in act:
        if c["type"] == "level":
            g = slam_base(g, t, c.get("dur", 1.6))
    for c, t in act:
        if c["type"] == "credit":
            cue_credit(g, c, t)
    for c, t in act:
        if c["type"] == "level":
            g = slam_logo(g, level_logo(c), t, c.get("dur", 1.6), GW // 2, c.get("y", 300))
    return g


# ------------------------------------------------------------------------------------------------ rendering
def render_part(a, b, out, with_audio, hold=True, run=None):
    """input frames a..b (1-based, inclusive) to `out`; the last frame is held for the final cue's `dur` when b is the
    capture's last frame"""
    run = run or Run()
    b = min(b, run.n)
    base = panel_base(run)
    c0, c1 = run.sync.cidx(a), run.sync.cidx(b)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", S.FPS, "-i", "-"]
    if with_audio:
        cmd += ["-ss", f"{c0 / S.NES_FPS:.6f}", "-i", str(SRC), "-map", "0:v", "-map", "1:a",
                "-af", "apad", "-shortest", "-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-an"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", S.FPS, str(out)]
    enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    src = S.nes_frames(SRC, c0, c1 - c0 + 1)
    ci, nes, count = c0 - 1, None, 0
    for k in range(a, b + 1):
        tgt = run.sync.cidx(k)                     # the dump repeats a picture now and then: skip the repeats
        while ci < tgt:
            nes = next(src, None)
            ci += 1
            if nes is None:
                break
        if nes is None:
            print(f"WARNING: the capture ended at input frame {k}", flush=True)
            break
        im = base.copy()
        im.paste(game_frame(nes, run, k), (0, 0))
        draw_panel(im, run, k)
        enc.stdin.write(im.tobytes())
        count += 1
        if count % 1200 == 0:
            print(f"  [{a}-{b}] {k}  {count / (time.time() - t0):.1f} fps", flush=True)
    if hold and run.final and b >= run.n and nes is not None:
        for j in range(run.hold):
            im = base.copy()
            im.paste(game_frame(nes, run, run.n, hold_t=(j + 1) / S.NES_FPS), (0, 0))
            draw_panel(im, run, run.n)
            enc.stdin.write(im.tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"wrote {out}  ({count} frames, {time.time() - t0:.0f} s)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--chunks", type=int, default=0)
    ap.add_argument("--part", help="a,b (internal: one chunk, video only)")
    ap.add_argument("--out")
    args = ap.parse_args()
    if args.part:
        a, b = (int(v) for v in args.part.split(","))
        render_part(a, b, Path(args.out), False)
        return
    run = Run()
    print(f"{NAME}: inputs {run.n}, clock {run.clock}, finish {run.finish}, cues {len(run.cues)}, capture repeats after "
          f"{run.sync.dups}", flush=True)
    rng = os.environ.get("RENDER_RANGE")
    if rng:
        a, b = (int(v) for v in rng.split(","))
        render_part(a, b, S.OUT / f"run_{NAME}_preview_{a}_{b}.mp4", True, hold=False, run=run)
        return
    n = max(1, min(6, args.chunks))
    edges = [1 + round(i * run.n / n) for i in range(n)] + [run.n + 1]
    tmp = S.OUT / f"run_{NAME}_chunks"
    tmp.mkdir(exist_ok=True)
    procs, parts = [], []
    for i in range(n):
        a, b = edges[i], edges[i + 1] - 1
        p = tmp / f"part{i:02d}.mp4"
        parts.append(p)
        procs.append(subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--name", NAME, "--part", f"{a},{b}",
                                       "--out", str(p)]))
        print(f"chunk {i}: frames {a}..{b} -> {p.name} (pid {procs[-1].pid})", flush=True)
    rc = [p.wait() for p in procs]
    if any(rc):
        sys.exit(f"chunk failed: {rc}")
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    vid = tmp / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vid)],
                   check=True)
    # sound: the capture's own from input 1's picture, squeezed by the few repeated frames it carries (0.01 %), faded
    # out as the picture freezes for the final card
    tempo = (run.n + len(run.sync.dups)) / run.n
    end = run.n / S.NES_FPS
    af = f"atempo={tempo:.8f},afade=t=out:st={end - 0.8:.3f}:d=0.8,apad"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vid), "-ss", f"{run.sync.first / S.NES_FPS:.6f}", "-i", str(SRC),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", af, "-shortest", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(OUTFILE)], check=True)
    print("wrote", OUTFILE, flush=True)


if __name__ == "__main__":
    main()
