"""Composite a BizHawk dump with the AI panel: reasoning, the controller, live RAM, and the TOKEN COUNTER.

    python render_overlay.py <session> [tokens.json]

Reads logs/<session>.{inputs,events,trace}.txt and video/<session>.mkv, writes video/<session>_overlay.mp4.
tokens.json (default logs/<session>.tokens.json) is a list of keyframes {"frame": f, "tokens": n, "cost": $,
"label": "..."}: the counter rolls between them, so each stretch of footage shows what it cost to get there.
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
LOGS, VIDEO = HERE / "logs", HERE / "video"
FONTS = Path(r"C:\Windows\Fonts")

W, H = 1280, 720
SCALE = 3
GW, GH = 256 * SCALE, 224 * SCALE
GX, GY = 0, (H - GH) // 2
PX = GW
FPS = "60.0988"
NES_FPS = 60.0988
WARP_BLACK = 170               # frames between the screen going black and the level byte changing on a warp (blackcal.py: 170/173/168)

BG = (8, 12, 10)
PANEL_BG = (12, 18, 14)
GRID = (22, 32, 26)
DIM = (95, 112, 100)
TEXT = (205, 215, 205)
ACCENT = (120, 220, 60)        # toad green
GOLD = (255, 200, 40)
RED = (235, 70, 70)
PAD_OFF = (38, 48, 42)


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


F_TITLE = font("consolab.ttf", 22)
F_BIG = font("consolab.ttf", 17)
F_TEXT = font("consola.ttf", 16)
F_SMALL = font("consola.ttf", 13)
F_TOK = font("consolab.ttf", 30)
F_CAP = font("arialbd.ttf", 23)
F_TIMER = font("consolab.ttf", 34)
GREEN = (90, 230, 110)


def load_captions(name):
    p = LOGS / f"{name}.captions.txt"
    if not p.exists():
        return []
    rows = []
    for l in p.read_text(encoding="utf-8").splitlines():
        a, b, t = l.split("	", 2)
        rows.append((int(a), int(b), t))
    return sorted(rows)


def draw_caption(im, text):
    """closed captions: a darkened band at the bottom of the game picture, up to two centred lines"""
    lines = textwrap.wrap(text, 58)[:3]
    lh = 30
    bh = lh * len(lines) + 16
    y0 = GY + GH - bh - 14
    box = (GX + 24, y0, GX + GW - 24, y0 + bh)
    region = im.crop(box).point(lambda v: v * 0.25)
    im.paste(region, box)
    d = ImageDraw.Draw(im)
    for i, line in enumerate(lines):
        y = y0 + 8 + i * lh
        cx = GX + GW // 2
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            d.text((cx + ox, y + oy), line, font=F_CAP, fill=(0, 0, 0), anchor="mt")
        d.text((cx, y), line, font=F_CAP, fill=(255, 255, 255), anchor="mt")


def load(name):
    inputs = [tuple(b for b in l.replace("+", ",").split(",") if b)
              for l in (LOGS / f"{name}.inputs.txt").read_text().splitlines() if not l.startswith("#")]
    events = []
    p = LOGS / f"{name}.events.txt"
    if p.exists():
        for l in p.read_text().splitlines():
            fr, _, txt = l.partition("\t")
            events.append((int(fr), txt))
    trace = {}
    for l in (LOGS / f"{name}.trace.txt").read_text().splitlines():
        fr, _, st = l.split("\t")
        trace[int(fr)] = {k: int(v) for k, _, v in (t.partition("=") for t in st.split())}
    return inputs, events, trace


def fmt_time(frame):
    t = frame / NES_FPS
    return f"{int(t // 60):02d}:{t % 60:06.3f}"


def fmt_tok(n):
    return f"{n / 1e6:,.2f}M" if n >= 1e6 else f"{n / 1e3:,.0f}k"


def draw_controller(d, x, y, held):
    def c(on):
        return ACCENT if on else PAD_OFF
    d.rounded_rectangle((x, y, x + 240, y + 90), radius=8, fill=(28, 36, 30), outline=(60, 76, 64))
    cx, cy, a = x + 45, y + 45, 12
    d.rectangle((cx - a, cy - 3 * a, cx + a, cy + 3 * a), fill=(48, 60, 52))
    d.rectangle((cx - 3 * a, cy - a, cx + 3 * a, cy + a), fill=(48, 60, 52))
    d.rectangle((cx - a, cy - 3 * a, cx + a, cy - a), fill=c("Up" in held))
    d.rectangle((cx - a, cy + a, cx + a, cy + 3 * a), fill=c("Down" in held))
    d.rectangle((cx - 3 * a, cy - a, cx - a, cy + a), fill=c("Left" in held))
    d.rectangle((cx + a, cy - a, cx + 3 * a, cy + a), fill=c("Right" in held))
    for i, (b, lab) in enumerate((("Select", "SEL"), ("Start", "START"))):
        bx = x + 92 + i * 44
        d.rounded_rectangle((bx, y + 50, bx + 30, y + 62), radius=6, fill=c(b in held))
        d.text((bx + 15, y + 68), lab, font=F_SMALL, fill=DIM, anchor="mt")
    for i, b in enumerate(("B", "A")):
        bx = x + 180 + i * 34
        d.ellipse((bx, y + 28, bx + 28, y + 56), fill=(RED if b in held else PAD_OFF), outline=(90, 30, 30))
        d.text((bx + 14, y + 68), b, font=F_SMALL, fill=DIM, anchor="mt")


def token_at(keys, k):
    """Roll between keyframes with an ease so the counter visibly spins, then settles, at each milestone."""
    if not keys:
        return None
    if k <= keys[0]["frame"]:
        return keys[0]["tokens"], keys[0]["cost"], keys[0].get("label", "")
    for a, b in zip(keys, keys[1:]):
        if a["frame"] <= k < b["frame"]:
            t = (k - a["frame"]) / max(1, b["frame"] - a["frame"])
            t = 1 - (1 - t) ** 3
            return (a["tokens"] + (b["tokens"] - a["tokens"]) * t, a["cost"] + (b["cost"] - a["cost"]) * t,
                    b.get("label", ""))
    return keys[-1]["tokens"], keys[-1]["cost"], keys[-1].get("label", "")


def fmt_run(t):
    return f"{int(t // 60):02d}:{t % 60:05.2f}"


def fmt_delta(dt):
    a = abs(dt)
    return f"{'+' if dt >= 0 else '-'}{int(a // 60)}:{a % 60:04.1f}"


def run_ends(trace, n):
    """The two ending events of a run, from the trace: {'clock': landing frame, 'queen_speech_cut': frame of the FIRST
    level-byte 13 -> 254 change (the cut to the Dark Queen's speech; NOT the end of the run), 'tbird_cut': frame of the
    SECOND 13 -> 254 change (the cut to Professor T. Bird's final dialogue = where the leaderboard clock stops)}.
    Either is None when the trace stops before it. See knowledge/end_timing.md."""
    clock = None
    cuts = []
    prev_lv = prev_an = None
    for k in range(1, n + 1):
        kv = trace.get(k)
        if not kv:
            continue
        lv, an = kv.get("level"), kv.get("anim")
        if clock is None and lv == 1 and prev_an == 5 and an == 4:
            clock = k
        if prev_lv == 13 and lv == 254:
            cuts.append(k)
        prev_lv, prev_an = lv, an
    return {"clock": clock, "queen_speech_cut": cuts[0] if cuts else None, "tbird_cut": cuts[1] if len(cuts) > 1 else None}


def run_splits(trace, n):
    """(clock start frame, [[level byte, enter frame, end frame or None]], finish frame or None) from the trace.

    FINISH (fixed 2026-10-09): the run ends on the leaderboard's terms, at the cut to Professor T. Bird's final dialogue
    = the SECOND time the level byte goes 13 -> 254. The FIRST 13 -> 254 is only the cut to the Dark Queen's speech;
    taking it as the finish made up14 read 12:23.39 when its real time is 12:31.75. The old number stays available as
    run_splits.queen_speech_cut (and from run_ends()). A trace that stops before the T. Bird cut has finish None: that
    run is not finished, and Level 13 has no end."""
    clock = None
    levels = []
    finish = None
    queen_cut = None
    prev_lv = prev_an = None
    for k in range(1, n + 1):
        kv = trace.get(k)
        if not kv:
            continue
        lv, an = kv.get("level"), kv.get("anim")
        if clock is None and lv == 1 and prev_an == 5 and an == 4:
            clock = k
        if lv != prev_lv and lv not in (0, 254, 255) and (not levels or levels[-1][0] != lv):
            if levels:                                  # a level ends on the record's terms: the first black frame. After a
                levels[-1][2] = k - (WARP_BLACK if levels[-1][0] in (1, 4, 8) else 0)   # warp that is ~170 frames before the level byte changes
            levels.append([lv, k, None])
        if levels and levels[-1][0] == 13 and prev_lv == 13 and lv == 254:
            if queen_cut is None:
                queen_cut = k                           # cut to the Dark Queen's speech: the game goes back to the tower after it
            elif finish is None:
                finish = k                              # cut to Professor T. Bird: the clock stops here
                levels[-1][2] = k
        prev_lv, prev_an = lv, an
    run_splits.queen_speech_cut = queen_cut
    return clock, levels, finish


run_splits.queen_speech_cut = None


def draw_race(d, x0, y0, wr, t, levels, k, finish):
    """two rows of ten level cells: where the world record is at this run time, and where the AI is"""
    lv = wr["levels"]
    cw = (W - 16 - x0) // len(lv)

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
        if e is None:                                   # level end unknown: pace it on the record's own duration
            dur = (lv[i]["end"] - (lv[i - 1]["end"] if i else 0.0)) * NES_FPS
            return i + min(0.98, (k - a) / max(1.0, dur))
        return i + min(1.0, (k - a) / max(1, e - a))

    for row, (lab, pos, col) in enumerate((("WR", wr_pos() if t >= 0 else 0.0, GOLD), ("AI", ai_pos(), ACCENT))):
        y = y0 + row * 20
        d.text((x0 - 28, y), lab, font=F_SMALL, fill=col)
        for i, L in enumerate(lv):
            cx = x0 + i * cw
            d.rectangle((cx, y, cx + cw - 2, y + 14), fill=(24, 34, 28), outline=(52, 68, 56))
            fill = max(0.0, min(1.0, pos - i))
            if fill > 0:
                d.rectangle((cx + 1, y + 1, cx + 1 + int((cw - 4) * fill), y + 13), fill=tuple(int(c * 0.55) for c in col))
            d.text((cx + cw // 2 - 1, y + 1), str(L["num"]), font=F_SMALL, fill=TEXT, anchor="mt")
        mx = x0 + int(min(len(lv), pos) * cw)
        d.rectangle((mx - 2, y - 2, mx + 1, y + 16), fill=col)


def render(name, tokfile=None):
    inputs, events, trace = load(name)
    caps = load_captions(name)
    keys = json.loads(Path(tokfile or LOGS / f"{name}.tokens.json").read_text()) \
        if Path(tokfile or LOGS / f"{name}.tokens.json").exists() else []
    n = len(inputs)
    import os
    rng = os.environ.get("RENDER_RANGE")               # "a,b": preview only frames a..b (1-based)
    ra, rb = (int(v) for v in rng.split(",")) if rng else (1, 10 ** 9)
    src = VIDEO / f"{name}.mkv"
    out = VIDEO / (f"{name}_overlay.mp4" if not rng else f"{name}_preview_{ra}_{rb}.mp4")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", FPS, "-i", "-", "-ss", f"{(ra - 1) / NES_FPS:.3f}", "-i", str(src), "-map", "0:v", "-map", "1:a?",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], stdin=subprocess.PIPE)
    base = Image.new("RGB", (W, H), BG)
    bd = ImageDraw.Draw(base)
    bd.rectangle((PX, 0, W, H), fill=PANEL_BG)
    for gy in range(0, H, 24):
        bd.line((PX, gy, W, gy), fill=GRID)
    bd.line((PX, 0, PX, H), fill=(40, 60, 46), width=2)
    bd.text((PX + 16, 12), "AI CONTROLLER", font=F_TITLE, fill=ACCENT)
    bd.text((PX + 16, 42), "RUN TIME", font=F_SMALL, fill=DIM)
    bd.text((PX + 280, 42), "WORLD RECORD (jay_cee)", font=F_SMALL, fill=DIM)
    bd.text((PX + 16, 166), "WHAT  /  WHY", font=F_SMALL, fill=DIM)
    bd.text((PX + 16, 300), "INPUT", font=F_SMALL, fill=DIM)
    bd.text((PX + 16, 414), "READ FROM RAM", font=F_SMALL, fill=DIM)
    bd.text((PX + 16, 502), "TOKENS SPENT BUILDING THIS RUN", font=F_SMALL, fill=DIM)
    bd.text((PX + 16, 618), "FRAME STREAM", font=F_SMALL, fill=DIM)
    wr = json.loads((HERE / "knowledge" / "wr_splits.json").read_text())
    clock, levels, finish = run_splits(trace, n)
    bd.text((PX + 280, 58), fmt_run(wr["total"]), font=F_TIMER, fill=GOLD)

    fb = 256 * 224 * 3
    total = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                                "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(src)],
                               capture_output=True, text=True).stdout.strip() or n)
    for _ in range(max(0, total - n)):
        dec.stdout.read(fb)
    ti, feed = -1, []
    for k in range(n):
        raw = dec.stdout.read(fb)
        if len(raw) < fb:
            break
        if k + 1 < ra:
            feed.append(f"f{k + 1:05d}")
            continue
        if k + 1 > rb:
            break
        im = base.copy()
        im.paste(Image.frombuffer("RGB", (256, 224), raw).resize((GW, GH), Image.NEAREST), (GX, GY))
        for a, b, t in caps:
            if a <= k + 1 <= b:
                draw_caption(im, t)
                break
        d = ImageDraw.Draw(im)
        held = set(inputs[k])
        kv = trace.get(k + 1, {})
        while ti + 1 < len(events) and events[ti + 1][0] <= k + 1:
            ti += 1
        d.text((W - 16, 16), f"frame {k + 1:05d}", font=F_SMALL, fill=DIM, anchor="rt")
        kk = min(k + 1, finish) if finish else k + 1
        started = bool(clock and k + 1 >= clock)
        rt = (kk - clock) / NES_FPS if started else 0.0
        d.text((PX + 16, 58), fmt_run(rt), font=F_TIMER, fill=(255, 255, 255) if started else DIM)
        note, ncol = ("" if started else "clock starts when the toad lands"), DIM
        for b, a, e in levels:                              # the last finished level's split against the record's
            wl = next((L for L in wr["levels"] if L["byte"] == b), None)
            if started and e and e <= k + 1 and wl:
                dt = (e - clock) / NES_FPS - wl["end"]
                note = f"after level {wl['num']}: {fmt_delta(dt)} vs the record"
                ncol = RED if dt > 0 else GREEN
        if finish and k + 1 >= finish:
            note = f"FINAL: {fmt_delta(rt - wr['total'])} vs the record"
            ncol = RED if rt > wr["total"] else GREEN
        d.text((PX + 16, 96), note, font=F_SMALL, fill=ncol)
        draw_race(d, PX + 46, 120, wr, rt if started else -1.0, levels, k + 1, finish)
        d.line((PX + 16, 160, W - 16, 160), fill=GRID)
        if ti >= 0:
            head, _, why = events[ti][1].partition("||")
            y = 184
            for line in textwrap.wrap(head, 44)[:3]:
                d.text((PX + 16, y), line, font=F_BIG, fill=ACCENT)
                y += 21
            y += 4
            for line in textwrap.wrap(why, 54)[:2]:
                d.text((PX + 16, y), line, font=F_TEXT, fill=TEXT)
                y += 18
        d.line((PX + 16, 294, W - 16, 294), fill=GRID)
        draw_controller(d, PX + 16, 318, held)
        d.text((PX + 272, 334), "HOLDING", font=F_SMALL, fill=DIM)
        d.text((PX + 272, 352), " + ".join(inputs[k]) if inputs[k] else "(nothing)", font=F_BIG,
               fill=ACCENT if inputs[k] else DIM)
        if kv:
            hp = sum(1 for i in range(6) if kv.get(f"hud{i}") == 244)
            foes = sum(1 for s in range(2, 8) if kv.get(f"id{s}") and kv.get(f"hp{s}") and kv.get(f"id{s}") not in (6, 34))
            wx = kv.get("x", 0) + 256 * ((kv.get("xh", 0) + 128) % 256 - 128)
            cam = kv.get("cam_lo", kv.get("camera", 0)) + 256 * kv.get("cam_hi", 0)
            rows = [("TOAD", f"x={wx:3d} y={kv.get('y', 0):3d} h={kv.get('height', 0):3d}"),
                    ("HEALTH", "#" * hp + "." * (6 - hp)), ("LIVES", str(kv.get("lives", 0))),
                    ("CAMERA", str(cam)), ("ENEMIES", str(foes)), ("LEVEL", str(kv.get("level", 0)))]
            for i, (lab, val) in enumerate(rows):
                cx, cy = PX + 16 + (i % 2) * 250, 434 + (i // 2) * 22
                d.text((cx, cy), lab, font=F_SMALL, fill=DIM)
                d.text((cx + 72, cy - 2), val, font=F_TEXT, fill=TEXT)
        tk = token_at(keys, k + 1)
        if tk:
            tok, cost, label = tk
            d.text((PX + 16, 518), fmt_tok(tok), font=F_TOK, fill=GOLD)
            d.text((PX + 250, 526), f"~${cost:,.2f}", font=F_BIG, fill=GOLD)
            seg = next(((a, b) for a, b in zip(keys, keys[1:]) if a["frame"] <= k + 1 < b["frame"]), None)
            if seg:                                  # what this stretch of footage cost to solve, and what the tokens went on
                a, b = seg
                d.text((PX + 16, 554), f"THIS PART COST {fmt_tok(b['tokens'] - a['tokens'])} TOKENS (~${b['cost'] - a['cost']:,.0f}) TO WORK OUT:",
                       font=F_SMALL, fill=GOLD)
                for i, line in enumerate(textwrap.wrap(b.get("why", b.get("label", "")), 60)[:3]):
                    d.text((PX + 16, 571 + i * 15), line, font=F_SMALL, fill=TEXT)
            else:
                d.text((PX + 16, 554), label[:56], font=F_SMALL, fill=DIM)
        feed.append(f"f{k + 1:05d} {('+'.join(inputs[k]) or '-')[:12]:<12} x={kv.get('x', 0) + 256 * ((kv.get('xh', 0) + 128) % 256 - 128):3d} "
                    f"y={kv.get('y', 0):3d} cam={kv.get('cam_lo', 0) + 256 * kv.get('cam_hi', 0):3d}")
        lines = feed[-5:]
        for i, line in enumerate(lines):
            age = len(lines) - 1 - i
            sh = max(70, 220 - age * 16)
            d.text((PX + 16, 636 + i * 15), line, font=F_SMALL, fill=(sh, sh, sh) if age else ACCENT)
        enc.stdin.write(im.tobytes())
        if (k + 1) % 600 == 0:
            print(f"  {k + 1}/{n}", flush=True)
    dec.stdout.close()
    enc.stdin.close()
    enc.wait()
    print("wrote", out)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
