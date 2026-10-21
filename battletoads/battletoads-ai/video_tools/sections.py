"""The sections as lists of pieces. `python sections.py s03 s05` renders those sections' pieces (skips ones already
rendered unless FORCE=1) and writes clips/<section>.list = the piece order for the assembler."""
from __future__ import annotations

import os
import sys
import textwrap

from pieces import *  # noqa: F401,F403

V = VIDEO
FORCE = os.environ.get("FORCE") == "1"


def need(name):
    return FORCE or not (CLIPS / f"{name}.mp4").exists()


# ------------------------------------------------------------------ custom pieces
def p_time_reveal(name, big, sub, small_top, dur=4.0, bg_cap=("capwip", 66440), col=None):
    """a huge time slam: small line on top, the time in logo lettering, a sub line"""
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    m.add_sfx(0.0, "riser", 0.5)
    m.add_sfx(0.55, "slam", 1.0)
    m.add_sfx(1.4, "ding", 0.5)
    frames = list(game_shot(bg_cap[0], bg_cap[1], 2, scale=5.0))
    bg = darken(frames[-1], 0.35)
    for i in range(int(dur * NES_FPS)):
        t = i / NES_FPS
        im = bg.copy()
        d = ImageDraw.Draw(im)
        if t > 0.1:
            a = min(1, (t - 0.1) / 0.3)
            d.text((W // 2, 300), small_top, font=font("ROCKEB.TTF", 64), fill=tuple(int(c * a) for c in TEXT), anchor="mm")
        if t > 0.37:
            im = slam(im, big, t - 0.37, dur - 0.37 + 1, sub=None, size=230, y=540,
                      colors=col)
            d = ImageDraw.Draw(im)
        if t > 1.2:
            a = min(1, (t - 1.2) / 0.3)
            f = font("arialbd.ttf", 52)
            d.text((W // 2 + 3, 773), sub, font=f, fill=(0, 0, 0), anchor="mm")
            d.text((W // 2, 770), sub, font=f, fill=tuple(int(c * a) for c in GOLD), anchor="mm")
        w.put(vignette(im, 0.4))
    return done(w, m, name)


def p_research(name, dur=9.0):
    """the research pass: real source text scrolling past, key quotes lighting up"""
    srcs = [(TOADS / "knowledge" / "research.md", "knowledge/research.md")]
    lines = []
    for p, label in srcs:
        for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
            for wl in textwrap.wrap(l, 92) or [""]:
                lines.append(wl)
    keys = ["warp portals", "Level 1", "credits warp", "global timer", "RNG", "Turbo Tunnel", "rat boot", "$0B",
            "object", "checkpoint"]
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    n = int(dur * NES_FPS)
    f = mono(24)
    lh = 32
    total_scroll = min(len(lines) * lh - H, 9000)
    hits = []
    for i in range(n):
        t = i / n
        off = int(total_scroll * ease(t) * 1.0)
        im, d = Image.new("RGB", (W, H), BG), None
        d = ImageDraw.Draw(im)
        first = off // lh
        for j in range(first, min(len(lines), first + H // lh + 2)):
            y = j * lh - off + 20
            line = lines[j]
            hot = any(k.lower() in line.lower() for k in keys)
            col = TEXT if not hot else GOLD
            if hot:
                d.rectangle((380, y - 2, 380 + d.textlength(line, font=f) + 12, y + lh - 6), fill=(40, 34, 8))
                if (j, ) not in hits and abs(y - H / 2) < 30:
                    hits.append((j,)); m.add_sfx(i / NES_FPS, "tick", 0.5)
            d.text((386, y), line, font=f, fill=col)
        # side rail
        d.rectangle((0, 0, 340, H), fill=PANEL)
        d.text((40, 60), "RESEARCH DAY", font=font("ROCKEB.TTF", 44), fill=TOAD)
        y = 140
        for s in ["speedrun.com rules + API", "TASVideos submission notes", "Speed Demos Archive run notes",
                  "a fan's disassembly (feos)", "DataCrystal RAM map", "Lua tools from TAS authors"]:
            d.text((40, y), "+ " + s, font=mono(22, True), fill=TEXT)
            y += 44
        d.text((40, H - 80), f"{len(lines):,} lines of notes", font=mono(24, True), fill=GOLD)
        w.put(vignette(im, 0.3))
    m.add_sfx(0, "whoosh", 0.6)
    return done(w, m, name)


def l1_draw():
    st = {}

    def draw(im, d, cam, row, i, info):
        cap = info["cap"]
        track(d, cam, cap, row, names={0x20: "PSYKO-PIG"})
        land = 2073                                  # the clock starts when the toad lands (journal 013: frame 2,074)
        if row >= land:
            t = (row - land) / NES_FPS
            readout(d, W - 380, 70, "LEVEL 1 TIME", f"{t:5.2f}s", GOLD, 72)
    return draw


def tt_speed_draw(label_extra=None):
    def draw(im, d, cam, row, i, info):
        if label_extra:
            chip(d, W - 60, H - 60, label_extra, WHITE, 30, anchor="mb")
    return draw


def queen_draw():
    def draw(im, d, cam, row, i, info):
        cap = info["cap"]
        track(d, cam, cap, row, only={"DARK QUEEN"}, hp=False)
        q = cap.r(row, 0x586)
        readout(d, 60, H - 250, "HIT COUNTER ($586)", f"{q:3d} / 252", RED, 64)
        bar(d, 60, H - 120, 440, 26, q / 252, RED)
    return draw


# ------------------------------------------------------------------ sections
def s03():
    out = []
    if need("s03_slam"):
        p_slam_over("s03_slam", "IS IT EVEN POSSIBLE?", cam_frames(V / "day1_first_boot.mkv", 30.0, 4.6, (128, 100), drift=0.08),
                    dur=2.4)
    out.append("s03_slam")
    if need("s03_tt"):
        p_game("s03_tt", "capwip", 12560, 10.0, label="TURBO TUNNEL", sub="THE LEVEL EVERYONE REMEMBERS", game_gain=0.7)
    out.append("s03_tt")
    out += ["record_card", "rules"]
    return out


def s05():
    out = []
    if need("s05_slam"):
        p_slam_over("s05_slam", "DAY 1: POWER ON", cam_frames(V / "day1_first_arena.mkv", 6.0, 4.5, (128, 112), drift=0.1),
                    dur=2.4)
    out.append("s05_slam")
    if need("s05_buttons"):
        tests = [("intro_none", "NOTHING"), ("intro_iA", "A"), ("intro_iB", "B"), ("intro_iSt", "START"),
                 ("intro_iS", "SELECT"), ("intro_iU", "UP"), ("intro_iD", "DOWN"), ("intro_iL", "LEFT"),
                 ("intro_iR", "RIGHT"), ("intro_amash", "MASH A"), ("intro_startmash", "MASH START"),
                 ("intro_iRA", "RIGHT+A")]
        p_raw_grid("s05_buttons", [V / f"{f}.mkv" for f, _ in tests], [l for _, l in tests], 7.0, [31.0] * len(tests),
                   title="EXPERIMENT 1: WHAT DOES EVERY BUTTON DO ON THE TITLE SCREEN?", speed=2.0)
    out.append("s05_buttons")
    if need("s05_press"):
        fr = [1000, 1100, 1200, 1300, 1400, 1450, 1500, 1515, 1519, 1520, 1525, 1600]
        files = [V / (f"press_{k}.mkv" if (V / f"press_{k}.mkv").exists() else f"rpress_{k}.mkv") for k in fr]
        p_raw_grid("s05_press", files, [f"START @ {k}" for k in fr], 6.0, [14.0] * len(fr),
                   title="EXPERIMENT 2: PRESS START ON EVERY FRAME, FIND THE FIRST ONE THAT COUNTS", speed=2.0)
    out.append("s05_press")
    out.append("ramvision")
    if need("s05_research"):
        p_research("s05_research")
    out.append("s05_research")
    if need("s05_level1"):
        p_game("s05_level1", "cap14", 1990, 9.5, label="LEVEL 1: RAGNAROK'S CANYON", sub="TWO PIGS, ONE DASH, THE HIDDEN WARP",
               draw=l1_draw(), scale=6.5)
    out.append("s05_level1")
    if need("s05_search"):
        p_search_paths()
    out += ["s05_search", "architecture"]
    return out


def s06():
    out = []
    if need("s06_slam"):
        p_slam_over("s06_slam", "GOAL ONE: JUST BEAT IT", game_frames("capwip", 2200, 6.0), dur=2.4)
    out.append("s06_slam")
    if need("s06_rat_fail"):
        w_ = None
        p_raw_grid("s06_rat_fail", [V / "l3_naive.mkv"] * 4, ["TRY 1", "TRY 2", "TRY 3", "TRY 4"], 5.0, [2, 12, 22, 32],
                   cols=2, title="FIRST CONTACT WITH LEVEL 3: THE RATS WIN", speed=1.5)
    out.append("s06_rat_fail")
    shots = [
        ("s06_tt", "capwip", 9000, 7.0, 3.0, "TURBO TUNNEL", "8,290 FRAMES OF BIKE COURSE, SOLVED BY SEARCH", TOAD, None),
        ("s06_l4", "capwip", 21000, 6.0, 2.0, "ARCTIC CAVERNS", "ICE BLOCKS, SNOWMEN, A BOTTOMLESS PIT", CYAN, None),
        ("s06_l6", "capwip", 27600, 6.0, 1.5, "KARNATH'S LAIR", "THE SNAKES ARE THE PLATFORMS", ORANGE, None),
        ("s06_l9", "capwip", 39600, 6.0, 2.0, "TERRA TUBES", "SWIMMING: 3x SLOWER, AND A CURRENT THAT PULLS YOU DOWN", CYAN, None),
        ("s06_l10", "capwip", 46560, 4.0, 1.0, "RAT RACE", "KICK THE FALLING RAT: THE LEVEL ENDS", RED, None),
        ("s06_l11", "capwip", 49000, 5.0, 1.5, "CLINGER-WINGER", "KEEP TOP SPEED OR THE BUZZBALL CATCHES YOU", ORANGE, None),
        ("s06_l12", "capwip", 58000, 6.0, 2.0, "THE REVOLUTION", "A ROTATING TOWER, SPRINGS AND FACES", (200, 120, 255), None),
        ("s06_l13", "capwip", 66040, 7.0, 1.0, "THE DARK QUEEN", "21 HITS", RED, queen_draw()),
    ]
    for name, cap, row, dur, sp, label, sub, col, draw in shots:
        if need(name):
            p_game(name, cap, row, dur, speed=sp, label=label, sub=sub, col=col, draw=draw,
                   extra=(lambda im, i, s=sp: (ImageDraw.Draw(im).text((W - 60, H - 60), f"{s:g}x", font=mono(40, True),
                                                                        fill=WHITE, anchor="rb") or im) if s != 1 else im))
        out.append(name)
    if need("s06_fails"):
        from gridshot import grid_frames
        w, m = Writer(CLIPS / "s06_fails.mp4"), audio.Mix(8)
        for im in grid_frames("grid_tower", lead=_grid_lead("grid_tower"), a0=120, a1=410, speed=2, survivor_tile=5,
                              cols=4, rows_=3, header="THE TOWER: ONE INPUT CHANGED PER ATTEMPT", fail_label="FELL",
                              fail_count="FELL"):
            w.put(im)
        for k in range(6):
            m.add_sfx(1.0 + k * 0.3, "crash", 0.25)
        done(w, m, "s06_fails")
    out.append("s06_fails")
    if need("s06_beaten"):
        p_time_reveal("s06_beaten", "18:04.08", "THE RECORD: 12:29.25", "DAY 5: GAME BEATEN")
    out.append("s06_beaten")
    return out


def _grid_lead(name):
    import json as _j
    g = _j.load(open(HERE / f"{name}.json"))
    total = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                                "stream=nb_read_frames", "-of", "csv=p=0", str(VIDEO / f"{name}.mkv")],
                               capture_output=True, text=True).stdout.strip())
    return total - g["steps"]


SECTIONS = dict(s03=s03, s05=s05, s06=s06)



# ------------------------------------------------------------------ goal two, TAS, numbers, outro
def p_intros(name="s07_intros", dur=6.0):
    """the level-intro page: first run sits on it ~4 s, the final run presses a button"""
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    n = int(dur * NES_FPS)
    left = list(game_shot("capwip", 14634, n, scale=3.6, target=(128, 112)))
    right = list(game_shot("cap14", 4752, n, scale=3.6, target=(128, 112)))
    capL, capR = cap_of("capwip"), cap_of("cap14")
    tL = tR = None
    for i in range(n):
        im = Image.new("RGB", (W, H), BG)
        for j, (fr, cap, row0, lab, col) in enumerate(((left[i], capL, 14634, "FIRST RUN", (190, 190, 190)),
                                                     (right[i], capR, 4752, "FINAL RUN", TOAD))):
            x0 = j * 960
            crop = fr.crop((480, 0, 1440, H))
            im.paste(crop, (x0, 0))
            d = ImageDraw.Draw(im)
            appeared = toad_box(cap, data_row("cap14" if cap is capR else "capwip", row0 + i)) is not None and i > 5
            if j == 0 and appeared and tL is None:
                tL = i; m.add_sfx(i / NES_FPS, "blip", 0.7)
            if j == 1 and appeared and tR is None:
                tR = i; m.add_sfx(i / NES_FPS, "ding", 0.7)
            stop = tL if j == 0 else tR
            k = i if stop is None else stop
            chip(d, x0 + 40, 60, lab, col, 36, anchor="lt")
            readout(d, x0 + 40, 140, "ON THE INTRO PAGE", f"{k / NES_FPS:4.2f} s", GOLD, 72)
        d.line((960, 0, 960, H), fill=(0, 0, 0), width=8)
        d.text((W // 2, H - 60), "LEVEL 4 INTRO: ANY BUTTON SKIPS IT  ·  ABOUT 20 SECONDS SAVED OVER THE WHOLE RUN",
               font=mono(30, True), fill=WHITE, anchor="mm")
        w.put(vignette(im, 0.3))
    return done(w, m, name)


def s07():
    out = []
    if need("s07_slam"):
        p_slam_over("s07_slam", "GOAL TWO: SHAVE SECONDS", game_frames("cap14", 2200, 6.0), dur=2.4,
                    colors=((200, 255, 140), (40, 160, 30), (10, 50, 10)))
    out += ["s07_slam", "level_losses", "bike_skip"]
    if need("s07_intros"):
        p_intros()
    out += ["s07_intros", "rng_chaos", "s07_tower", "progression"]
    if need("s07_beaten"):
        p_time_reveal("s07_beaten", "12:28.60", "WORLD RECORD: 12:29.25", "RECORD BEATEN", bg_cap=("cap14", 46084),
                      col=((200, 255, 140), (40, 170, 30), (10, 50, 10)))
    out.append("s07_beaten")
    if need("s07_final"):
        p_time_reveal("s07_final", "12:23.39", "5.86 SECONDS UNDER THE RECORD", "ONE MORE PUSH", bg_cap=("cap14", 46084))
    out += ["s07_final", "integrity"]
    return out


def s08():
    return ["tas"]


def s09():
    return ["numbers", "token_phases"]


CREDITS = [
    ("THE RECORD TO BEAT", "jay_cee: 12:29.25, speedrun.com Battletoads (NES) Any% No Credits Warp"),
    ("RUN NOTES", "jc583 (Speed Demos Archive): warps, dash-jumps, the rat boot"),
    ("TOOL-ASSISTED RUNS (TASVideos)", "feos, Alyosha & Samsara · Lobsterzelda · MESHUGGAH & Koh1fds · Phil & Genisto"),
    ("THE GAME'S CODE AND MEMORY", "feos's disassembly and Lua tools · DataCrystal RAM map"),
    ("EMULATOR", "BizHawk (TASVideos)"),
    ("THE GAME", "Battletoads (NES, 1991): Rare / Tradewest"),
    ("THE AI", "Claude (Anthropic), working in Claude Code"),
]


def p_outro(name="s11_outro", dur=26.0):
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    mp = Image.open(OUT / "tower_map.png")
    big = mp.resize((int(mp.width * 4), int(mp.height * 4)), Image.NEAREST)
    n = int(dur * NES_FPS)
    games = ["ZELDA II", "CONTRA", "TMNT", "IKARUGA", "MEGA MAN", "NINJA GAIDEN"]
    m.add_sfx(0, "whoosh", 0.6)
    t_cta1, t_cta2, t_end = 8.0, 13.0, 18.0
    m.add_sfx(t_cta1, "slam", 0.9)
    m.add_sfx(t_cta2, "slam", 0.9)
    for k in range(len(games)):
        m.add_sfx(t_cta1 + 0.6 + k * 0.25, "blip", 0.5)
    for i in range(n):
        t = i / NES_FPS
        # background: the stitched tower drifting upward, dimmed
        off = int((big.height - H) * (1 - t / dur))
        bg = big.crop((0, off, big.width, off + H)).resize((W, H), Image.NEAREST) if big.width < W else big.crop((0, off, W, off + H))
        im = darken(bg, 0.22)
        d = ImageDraw.Draw(im)
        if t < t_cta1:                                    # credits
            d.text((W // 2, 110), "THANK YOU", font=font("ROCKEB.TTF", 80), fill=GOLD, anchor="mm")
            for k, (a, b) in enumerate(CREDITS):
                ta = 0.3 + k * 0.45
                if t < ta:
                    continue
                al = min(1, (t - ta) / 0.3)
                y = 220 + k * 112
                d.text((W // 2, y), a, font=mono(28, True), fill=tuple(int(c * al) for c in TOAD), anchor="mm")
                d.text((W // 2, y + 40), b, font=font("arialbd.ttf", 34), fill=tuple(int(c * al) for c in WHITE), anchor="mm")
        elif t < t_cta2:
            tt = t - t_cta1
            im = slam(im, "WHAT SHOULD IT PLAY NEXT?", tt, 99, size=110, y=330)
            d = ImageDraw.Draw(im)
            for k, g in enumerate(games):
                ta = 0.6 + k * 0.25
                if tt < ta:
                    continue
                kk = ease_out_back(min(1, (tt - ta) / 0.3))
                x = 330 + (k % 3) * 630
                y = 600 + (k // 3) * 170
                f = font("ROCKEB.TTF", int(60 * kk) + 1)
                d.text((x, y), g, font=f, fill=WHITE, anchor="mm")
            d.text((W // 2, 990), "TELL ME IN THE COMMENTS", font=mono(40, True), fill=GOLD, anchor="mm")
        elif t < t_end:
            tt = t - t_cta2
            im = slam(im, "WHAT DID IT DO WRONG?", tt, 99, size=120, y=420, sub="where would YOU have saved time?")
        else:                                              # end screen: leave room for YouTube's end-screen cards
            tt = t - t_end
            a = min(1, tt / 0.5)
            d.text((W // 2, 160), "THANKS FOR WATCHING", font=font("ROCKEB.TTF", 72), fill=tuple(int(c * a) for c in GOLD), anchor="mm")
            d.text((W // 2, H - 120), "subscribe for the next one", font=mono(34, True), fill=tuple(int(c * a) for c in TEXT), anchor="mm")
        w.put(vignette(im, 0.35))
    bed = audio.chiptune(bars=int(dur / 1.6) + 1, bpm=150, intensity=0.6)
    m.add(0, bed, 0.35)
    return done(w, m, name)


def p_outro_bg(name="s11_outro_bg", dur=30.0):
    """30 s of moving background for the owner's on-camera outro: the stitched tower drifting up behind a slow parade
    of the run's best moments, dimmed, with the logo small in the top corner; nothing in the middle third"""
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    mp = Image.open(OUT / "tower_map.png")
    tower = mp.resize((mp.width * 5, mp.height * 5), Image.NEAREST)
    lg = logo("AI vs BATTLETOADS", 56)
    moments = [(2296 - 60), 4400, 9950, 17500, 22500, 28900, 30000, 41500, 45900]
    cap = cap_of("cap14")
    tiles = []
    for r in moments:                              # a 4 s loop of each moment, small
        fr = list(nes_frames(SRCS["cap14"], 6 + r, 240))
        tiles.append([f.crop((0, 40, 256, 224)).resize((384, 276), Image.NEAREST) for f in fr[::2]])
    n = int(dur * NES_FPS)
    for i in range(n):
        t = i / NES_FPS
        off = int((tower.height - H) * (1 - t / dur))
        bg = Image.new("RGB", (W, H), BG)
        col = tower.crop((0, off, tower.width, off + H))
        for x in (-200, 1920 - tower.width + 200):
            bg.paste(col, (x, 0))
        im = darken(bg, 0.28)
        # two slow rivers of moments down the left and right edges
        for side in (0, 1):
            x = 40 if side == 0 else W - 40 - 384
            for j in range(4):
                y = int(((t * 60 + j * 300 + side * 150) % 1200) - 300) if side == 0 else int(H - (((t * 60 + j * 300) % 1200) - 300) - 276)
                tl = tiles[(j * 2 + side) % len(tiles)]
                fr = tl[i % len(tl)]
                fr = ImageEnhance.Brightness(fr).enhance(0.55)
                im.paste(fr, (x, y))
                ImageDraw.Draw(im).rectangle((x, y, x + 383, y + 275), outline=(30, 44, 34), width=3)
        im.paste(lg, (60, 40), lg)
        a = min(1.0, t / 1.0, (dur - t) / 1.5)
        im = Image.blend(Image.new("RGB", (W, H)), im, max(0.0, a))
        w.put(vignette(im, 0.45))
    bed = audio.chiptune(bars=int(dur / 1.6) + 1, bpm=150, intensity=0.45)
    fade = np.ones(len(bed), np.float32)
    fl = int(2 * audio.SR)
    fade[-fl:] = np.linspace(1, 0, fl)
    m.add(0, bed * fade[:, None], 0.3)
    return done(w, m, name)


def s11():
    if need("s11_outro_bg"):
        p_outro_bg()
    return ["s11_outro_bg"]


SECTIONS.update(s07=s07, s08=s08, s09=s09, s11=s11)


def p_search_paths(name="s05_search", dur=9.0):
    """every jump the search tried from one moment in Level 1, drawn as paths; the one it kept lights up"""
    d_ = json.load(open(HERE / "paths_l1.json"))
    S = d_["S"]
    N = 50                                               # up to the landing on the rock (before the warp lifts the toad)
    vs = d_["variants"]
    cap = cap_of("cap14")
    bgn = next(nes_frames(SRCS["cap14"], lead_of("cap14") + S + N - 1, 1))
    cam = Camera(7.5, cx=150, cy=140)
    bg = darken(scanlines(cam.render(bgn), 0.1), 0.6)
    camx_end = cap.r(data_row("cap14", S + N - 1), 0x87) + 256 * cap.r(data_row("cap14", S + N - 1), 0x88)
    landed = lambda v: v["path"][-1][2] >= 190
    n_ok = sum(1 for v in vs[1:] if landed(v)); n_bad = len(vs) - 1 - n_ok
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    n = int(dur * NES_FPS)
    t_draw0, t_draw1, t_pick = 1.0, 4.6, 5.4
    m.add_sfx(0, "whoosh", 0.6)
    m.add_sfx(t_pick, "ding", 0.8)
    for k in range(12):
        m.add_sfx(t_draw0 + k * 0.3, "tick", 0.4)

    def pts(v, upto):
        out = []
        for p in v["path"][:upto]:
            if p[0] is None or p[4] != 1:
                break
            q = cam.to_out(p[0] - camx_end, p[1] - 8)
            if out and abs(q[1] - out[-1][1]) > 160:      # a sprite jump (respawn / warp), not motion
                break
            out.append(q)
        return out
    for i in range(n):
        t = i / NES_FPS
        im = bg.copy()
        d = ImageDraw.Draw(im, "RGBA")
        upto = int(N * ease(min(1, max(0, (t - t_draw0) / (t_draw1 - t_draw0)))))
        pick = t > t_pick
        for v in vs[1:]:
            pp = pts(v, upto)
            if len(pp) < 2:
                continue
            ok = landed(v)
            col = (80, 230, 110, 200) if ok else (235, 70, 70, 140)
            if pick:
                col = col[:3] + (50,)
            d.line(pp, fill=col, width=3)
            if upto >= N - 1 and not pick:
                x, y = pp[-1]
                if ok:
                    d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=col)
                else:
                    d.line((x - 8, y - 8, x + 8, y + 8), fill=col, width=4); d.line((x - 8, y + 8, x + 8, y - 8), fill=col, width=4)
        if pick:
            pp = pts(vs[0], N)
            k = ease(min(1, (t - t_pick) / 0.8))
            pp = pp[:max(2, int(len(pp) * k))]
            d.line(pp, fill=GOLD + (255,), width=9)
            x, y = pp[-1]
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=GOLD + (255,))
            if k >= 1:
                chip(d, x + 24, y - 20, "THE ONE IT KEPT", GOLD, 34)
        d.rectangle((0, 0, W, 110), fill=(0, 0, 0, 200))
        d.text((50, 55), f"THE SAME JUMP, {len(vs) - 1} OTHER WAYS: ONLY A FEW LAND ON THE ROCK", font=mono(40, True),
               fill=TOAD, anchor="lm")
        if upto >= N - 1:
            chip(d, 60, H - 60, f"{n_bad} MISSED", RED, 36, fg=WHITE)
            chip(d, 400, H - 60, f"{n_ok} LANDED", (80, 230, 110), 36)
        w.put(vignette(im, 0.3))
    return done(w, m, name)




SCREEN_PARTS = [  # (rect on the 1920x1080 run screen, title, explanation)
    ((0, 0, 1280, 1080), "THE GAME", "the real run, live. Boxes come from the game's own sprite memory: the toad, and every enemy with its health"),
    ((1296, 296, 1904, 540), "WHAT / WHY", "what it is doing right now, and why it chose that over the alternatives"),
    ((1296, 548, 1590, 718), "THE CONTROLLER", "the exact buttons pressed on this frame. 46,751 frames, every one chosen by a search"),
    ((1296, 86, 1904, 285), "THE CLOCK", "the speedrun timer, and the record's pace in gold vs the AI in green, level by level"),
    ((1296, 724, 1904, 858), "READ FROM RAM", "the numbers it reads out of the console's memory instead of looking at the picture"),
    ((1296, 866, 1904, 1064), "TOKEN COUNTER", "how much AI thinking it took to work this part out, and what it was spent on"),
]


def p_screen(name="s04_screen", per=4.4, starts=None, end=None):
    src = HERE / "assets" / "run_preview_41300.mp4"
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True).stdout
    fb = W * H * 3
    frames = [raw[i:i + fb] for i in range(0, len(raw) - fb + 1, fb)]
    seq = frames + frames[::-1]
    intro = 1.6
    if starts is None:
        starts = [intro + k * per for k in range(len(SCREEN_PARTS))]
        end = starts[-1] + per + 0.6
    intro = min(intro, starts[0])
    dur = end
    w, m = Writer(CLIPS / f"{name}.mp4"), audio.Mix(dur + 1)
    m.add_sfx(0, "slam", 0.8)
    n = int(dur * NES_FPS)
    for k in range(len(SCREEN_PARTS)):
        m.add_sfx(starts[k], "blip", 0.7)
    for i in range(n):
        t = i / NES_FPS
        base = Image.frombuffer("RGB", (W, H), seq[int(i * 0.35) % len(seq)])
        if t < intro:
            im = slam(darken(base, 0.5), "HOW TO READ THE SCREEN", t, intro, size=110)
            w.put(im)
            continue
        if t < starts[0]:
            w.put(darken(base, 0.55)); continue
        k = max(i_ for i_ in range(len(starts)) if starts[i_] <= t)
        tk = t - starts[k]
        (x0, y0, x1, y1), title, text = SCREEN_PARTS[k]
        a = ease(min(1, tk / 0.35))
        dim = darken(base, 1 - 0.65 * a)
        dim.paste(base.crop((x0, y0, x1, y1)), (x0, y0))
        d = ImageDraw.Draw(dim)
        d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), outline=GOLD, width=6)
        # caption box on the opposite side
        on_left = x0 >= 1280
        bx0 = 70 if on_left else 1310
        bw = 1100 if on_left else 560
        by0 = 760 if k else 120
        f1, f2 = font("ROCKEB.TTF", 64), font("arialbd.ttf", 38)
        lines = textwrap.wrap(text, 46 if on_left else 26)
        bh = 110 + 50 * len(lines)
        slide = int((1 - a) * 60)
        d.rectangle((bx0, by0 + slide, bx0 + bw, by0 + bh + slide), fill=(0, 0, 0))
        d.rectangle((bx0, by0 + slide, bx0 + 12, by0 + bh + slide), fill=GOLD)
        d.text((bx0 + 40, by0 + 20 + slide), f"{k + 1}. {title}", font=f1, fill=GOLD)
        for j, l in enumerate(lines):
            d.text((bx0 + 40, by0 + 100 + j * 50 + slide), l, font=f2, fill=WHITE)
        if on_left:                                       # arrow from the caption to the highlighted part
            ax, ay = bx0 + bw, by0 + bh // 2 + slide
            tx, ty = x0 - 10, (y0 + y1) // 2
            d.line((ax, ay, tx, ty), fill=GOLD, width=6)
            ang = math.atan2(ty - ay, tx - ax)
            d.polygon([(tx, ty), (tx - 30 * math.cos(ang - 0.4), ty - 30 * math.sin(ang - 0.4)),
                       (tx - 30 * math.cos(ang + 0.4), ty - 30 * math.sin(ang + 0.4))], fill=GOLD)
        w.put(dim)
    return done(w, m, name)


def s04():
    if need("s04_screen"):
        p_screen()
    return ["s04_screen"]


SECTIONS.update(s04=s04)


if __name__ == "__main__":
    for s in sys.argv[1:]:
        order = SECTIONS[s]()
        (CLIPS / f"{s}.list").write_text("\n".join(order), encoding="utf-8")
        print(s, order, flush=True)
