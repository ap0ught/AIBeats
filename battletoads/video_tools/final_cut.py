"""The final cut: every section's picture fitted to the owner's narration, with cuts landing on the words.

    python final_cut.py            -> out/battletoads_final.mp4, out/battletoads_final.srt, out/battletoads_final_chapters.txt

Per section: the narration starts at VO_START (or wherever puts a chosen phrase on a chosen moment); an anchored piece
starts just before its phrase is spoken; unanchored pieces share the time between anchors in proportion to their own
length; a piece that gets more time than it has holds its last frame, one that gets less is trimmed. Everything else
(music bed, sound effects, game audio) is ducked under the voice."""
from __future__ import annotations

import difflib
import json
import re
import subprocess

import numpy as np

from style import *  # noqa: F401,F403
import audio
from vo_find import find, length

VOICE = HERE / "voice"
ADJ = OUT / "adj"
ADJ.mkdir(exist_ok=True)
VO_START = 0.35
LEAD = 0.12                     # a cut lands this much before its word
TAIL = 0.9                      # picture continues this long after the narration ends
MIN_PIECE = 1.0
BED_GAIN = 0.16
VOICE_DB = -18.0               # narration loudness (RMS of the voiced parts)
DUCK = 0.2                    # everything else drops to this gain (-14 dB) while the voice speaks

PLAN = {
    "s01": dict(pieces=["s01_montage", "title_card"]),
    "s02": dict(pieces=["s02_asked"], vo="02", vo_start=0.5),
    "s03": dict(pieces=["s03_slam", "s03_tt", "record_card", "rules"], vo="03",
                anchors={"record_card": "the world record for this game", "rules": "same rules a human does"}),
    "s04": dict(pieces=["s04_screen"], vo="04"),
    "s05": dict(pieces=["s05_slam", "architecture", "s05_buttons", "s05_press", "ramvision", "s05_research", "s05_level1",
                        "s05_search"], vo="05",
                anchors={"s05_buttons": "running experiments", "s05_press": "earliest frame",
                         "ramvision": "looking for the toad", "s05_research": "research day", "s05_level1": "on level one",
                         "s05_search": "every one of these red lines"}),
    "s06": dict(pieces=["s06_slam", "s06_rat_fail", "s06_tt", "s06_l4", "s06_l6", "s06_l9", "s06_l10", "s06_l11", "s06_l12",
                        "s06_l13", "s06_fails", "s06_beaten"], vo="06",
                anchors={"s06_rat_fail": "the rats in level 3", "s06_tt": "the turbo tunnel", "s06_l4": "level 4 the arctic",
                         "s06_l6": "in karnas slayer", "s06_l9": "then the terror tubes", "s06_l10": "in the rat race",
                         "s06_l11": "cleaning a winger", "s06_l12": "then the tower", "s06_l13": ("then the dark queen", 0.45),
                         "s06_fails": "a lot of failing", "s06_beaten": "but on day 5"}),
    "s07": dict(pieces=["s07_slam", "level_losses", "bike_skip", "s07_intros", "rng_chaos", "s07_tower", "progression",
                        "s07_beaten", "s07_final", "integrity"], vo="07",
                anchors={"level_losses": "compare every level", "bike_skip": "the turbo tunnel was",
                         "s07_intros": "smaller stuff", "rng_chaos": "the chaos part", "s07_tower": "the tower is where",
                         "progression": "time just kept dropping", "s07_beaten": "record beaten",
                         "s07_final": "so we kept going", "integrity": "every run gets double checked"}),
    "s08": dict(pieces=["tas"], vo="08"),
    "s09": dict(pieces=["numbers", "token_phases"], vo="09", tail=0.4),
    "s10": dict(pieces=["s10_run"]),                    # no voice during the run (owner, 2026-10-08)
    "s11": dict(pieces=["s11_outro_final"]),            # the owner on camera over the background (outro.py)
}


def movavg(v, n):
    """centred moving average in O(len) (np.convolve with a 0.5 s window is far too slow on minutes of audio)"""
    c = np.cumsum(np.concatenate([[0.0], v]))
    h = n // 2
    i = np.arange(len(v))
    lo, hi = np.clip(i - h, 0, len(v)), np.clip(i + h + 1, 0, len(v))
    return ((c[hi] - c[lo]) / (hi - lo)).astype(np.float32)


def level(x, target_db=VOICE_DB if "VOICE_DB" in globals() else -18.0, win_s=1.5, max_cut_db=8.0, max_boost_db=4.0):
    """slow automatic leveling of a narration take: the loudness of every ~1.5 s stretch of speech is pulled toward
    the target (excited lines come down, quiet ones come up a little), smoothly so it never pumps"""
    mono = np.abs(x).max(1)
    win = int(win_s * audio.SR)
    p = movavg(mono ** 2, win)
    voiced = movavg((mono > 0.01).astype(np.float32), win)
    rms = np.sqrt(p / np.maximum(voiced, 0.05)) + 1e-6
    g_db = np.clip(target_db - 20 * np.log10(rms), -max_cut_db, max_boost_db)
    g_db = np.where(voiced > 0.1, g_db, 0.0)
    g = 10 ** (movavg(g_db.astype(np.float32), int(0.6 * audio.SR)) / 20)
    return (x * g[:, None]).astype(np.float32)


def run(cmd):
    subprocess.run(cmd, check=True)


def nframes_of(p):
    return int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                               "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def piece_audio(name, n_src, n_out):
    """the piece's own sound (wav, or its sfx cues), cut/padded to n_out frames"""
    wav = CLIPS / f"{name}.wav"
    if name == "s10_run":
        x = audio.load(CLIPS / f"{name}.mp4")
    elif wav.exists():
        x = audio.load(wav)
    else:
        m = audio.Mix(n_src / NES_FPS + 1)
        m.add_cues(0, CLIPS / f"{name}.sfx.json", 0.4)
        x = m.buf
    want = int(round(n_out / NES_FPS * audio.SR))
    if len(x) < want:
        x = np.concatenate([x, np.zeros((want - len(x), 2), np.float32)])
    return x[:want]


def fitted(name, n_src, n_out):
    """the piece as exactly n_out frames: copied, trimmed, or with its last frame held"""
    src = CLIPS / f"{name}.mp4"
    if n_out == n_src:
        return src
    out = ADJ / f"{name}_{n_out}.mp4"
    if out.exists():
        return out
    enc = ["-an", "-r", FPS, "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p"]
    hold = n_out - n_src
    if hold <= 0:
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-frames:v", str(n_out)] + enc + [str(out)])
    elif hold < int(1.2 * NES_FPS):                    # short: just hold the last frame
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf",
             f"tpad=stop_mode=clone:stop_duration={hold / NES_FPS + 0.5:.3f}", "-frames:v", str(n_out)] + enc + [str(out)])
    else:                                              # long: the last frame slowly pushes in, so it never looks frozen
        last = ADJ / f"{name}_last.png"
        run(["ffmpeg", "-y", "-v", "error", "-sseof", "-0.05", "-i", str(src), "-frames:v", "1", "-update", "1", str(last)])
        tail = ADJ / f"{name}_push{hold}.mp4"
        z = 0.05 / hold                                # 5% zoom over the hold
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(last), "-vf",
             f"scale=3840:2160,zoompan=z='1+{z:.7f}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={hold}:s=1920x1080:fps={FPS}",
             "-frames:v", str(hold)] + enc + [str(tail)])
        lst = ADJ / f"{name}_{n_out}.txt"
        lst.write_text(f"file '{src.as_posix()}'\nfile '{tail.as_posix()}'\n", encoding="utf-8")
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def plan_section(sec, p):
    names = p["pieces"]
    nat = {n: nframes_of(CLIPS / f"{n}.mp4") for n in names}
    vo = p.get("vo")
    vo_start, vo_len = 0.0, 0.0
    if vo:
        vo_len = length(vo)
        vo_start = p.get("vo_start", VO_START)
        if "vo_phrase" in p:
            ph, at = p["vo_phrase"]
            vo_start = max(0.0, at - find(vo, ph))
    # fixed starts (seconds)
    fixed = {names[0]: 0.0}
    for n, ph in p.get("anchors", {}).items():
        delta = 0.0
        if isinstance(ph, tuple):
            ph, delta = ph
        fixed[n] = vo_start + find(vo, ph) - LEAD + delta
    natural_total = sum(nat.values()) / NES_FPS
    if vo:
        last_fixed = max(fixed.values())
        end = max(vo_start + vo_len + p.get("tail", TAIL), last_fixed + MIN_PIECE)
    else:
        end = natural_total
    starts = {}
    idx = [i for i, n in enumerate(names) if n in fixed] + [len(names)]
    for a, b in zip(idx, idx[1:]):
        t0 = fixed[names[a]]
        t1 = fixed[names[b]] if b < len(names) else end
        group = names[a:b]
        tot = sum(nat[n] for n in group)
        t = t0
        for n in group:
            starts[n] = t
            t += (t1 - t0) * nat[n] / tot
    order = [(starts[n], n) for n in names]
    out = []
    for i, (s, n) in enumerate(order):
        e = order[i + 1][0] if i + 1 < len(order) else end
        n_out = max(int(round(MIN_PIECE * NES_FPS)), int(round((e - s) * NES_FPS)))
        out.append((n, nat[n], n_out))
    return out, vo_start


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def captions(vo, t0):
    """script text, timed by aligning its words to the whisper words of the narration file"""
    script = (HERE / "voice_text" / ("09b" if vo == "09" else vo)).with_suffix(".txt").read_text(encoding="utf-8").split()
    ws = json.loads((VOICE / "words.json").read_text(encoding="utf-8"))[vo]
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    sm = difflib.SequenceMatcher(None, [norm(w) for w in script], [norm(w[2]) for w in ws], autojunk=False)
    times = [None] * len(script)
    for a, b, size in sm.get_matching_blocks():
        for k in range(size):
            times[a + k] = (ws[b + k][0], ws[b + k][1])
    # fill gaps by interpolation
    known = [i for i, x in enumerate(times) if x]
    for i in range(len(times)):
        if times[i] is None:
            lo = max([k for k in known if k < i], default=None)
            hi = min([k for k in known if k > i], default=None)
            if lo is not None and hi is not None:
                f = (i - lo) / (hi - lo)
                st = times[lo][1] + (times[hi][0] - times[lo][1]) * f
                times[i] = (st, st + 0.2)
            elif lo is not None:
                times[i] = (times[lo][1], times[lo][1] + 0.3)
            else:
                times[i] = (times[hi][0] - 0.3, times[hi][0]) if hi is not None else (0, 0.3)
    cues, cur = [], []
    for i, w in enumerate(script):
        cur.append(i)
        text = " ".join(script[j] for j in cur)
        if len(text) > 38 or w.endswith((".", "?", "!")) or i == len(script) - 1:
            cues.append((t0 + times[cur[0]][0], t0 + times[cur[-1]][1] + 0.15, text))
            cur = []
    return cues


def build(name="battletoads_final"):
    vids, auds, voice_track, chapters, cues = [], [], [], [], []
    t = 0.0
    for sec, p in PLAN.items():
        chapters.append((t, sec))
        plan, vo_start = plan_section(sec, p)
        sec_t0 = t
        for n, n_src, n_out in plan:
            if n == "s10_run":
                n_out = n_src
            vids.append(fitted(n, n_src, n_out))
            auds.append(piece_audio(n, n_src, n_out))
            t += n_out / NES_FPS
        if p.get("vo"):
            x = audio.load(VOICE / f"{p['vo']}.wav")
            voice_track.append((sec_t0 + vo_start, x))
            cues += captions(p["vo"], sec_t0 + vo_start)
        for key, fr in p.get("popins", {}).items():
            x = audio.load(VOICE / f"{key}.wav")
            voice_track.append((sec_t0 + fr / NES_FPS, x))
            txt = (HERE / "voice_text" / f"{key}.txt").read_text(encoding="utf-8").strip()
            cues.append((sec_t0 + fr / NES_FPS, sec_t0 + fr / NES_FPS + len(x) / audio.SR, txt))
        print(f"{sec}: {t - sec_t0:6.1f} s  " + " ".join(f"{n}:{n_out / NES_FPS:.1f}" for n, _, n_out in plan), flush=True)
    mix = np.concatenate(auds)
    # music bed under s03..s09
    st = dict((s, t0) for t0, s in chapters)
    i0, i1 = int(st["s03"] * audio.SR), int(st["s10"] * audio.SR)
    bed = audio.chiptune(bars=int((i1 - i0) / audio.SR / 1.6) + 2, bpm=150, intensity=0.35)[:i1 - i0]
    fade = np.ones(len(bed), np.float32)
    fl = int(1.5 * audio.SR)
    fade[:fl] = np.linspace(0, 1, fl); fade[-fl:] = np.linspace(1, 0, fl)
    mix[i0:i0 + len(bed)] += bed * fade[:, None] * BED_GAIN
    # the voice at a steady level, everything else well under it while it speaks
    def rms_db(v):
        return 20 * np.log10(np.sqrt(np.mean(v ** 2)) + 1e-9)
    voice_track = [(t0, level(x * 10 ** ((VOICE_DB - rms_db(x[np.abs(x).max(1) > 0.01] if (np.abs(x).max(1) > 0.01).any() else x)) / 20)))
                   for t0, x in voice_track]
    env = np.ones(len(mix), np.float32)
    win = int(0.5 * audio.SR)
    for t0, x in voice_track:
        a = int(t0 * audio.SR)
        act = (movavg(np.abs(x).max(1), win) > 0.004).astype(np.float32)
        act = movavg(act, win)                                          # smooth the edges (~0.25 s ramps)
        duck = 1 - (1 - DUCK) * np.clip(act * 1.5, 0, 1)
        pad = int(0.3 * audio.SR)
        duck = np.concatenate([np.linspace(1, duck[0], pad), duck, np.linspace(duck[-1], 1, pad)])
        a -= pad
        lo, hi = max(0, a), min(len(env), a + len(duck))
        env[lo:hi] = np.minimum(env[lo:hi], duck[lo - a:hi - a])
    mix *= env[:, None]
    for t0, x in voice_track:
        a = int(t0 * audio.SR)
        seg = mix[a:a + len(x)]
        mix[a:a + len(seg)] += x[:len(seg)]
    peak = np.abs(mix).max() or 1
    if peak > 0.98:
        mix = np.tanh(mix / peak * 1.25) * 0.95
    lst = OUT / f"{name}.txt"
    lst.write_text("".join(f"file '{v.as_posix()}'\n" for v in vids), encoding="utf-8")
    vtmp = OUT / f"{name}_v.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vtmp)])
    wav = OUT / f"{name}.wav"
    audio.save(wav, mix)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(vtmp), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "256k", "-shortest", str(OUT / f"{name}.mp4")])
    vtmp.unlink()
    (OUT / f"{name}.srt").write_text("".join(f"{i + 1}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n\n"
                                             for i, (a, b, txt) in enumerate(sorted(cues))), encoding="utf-8")
    titles = {"s01": "Opening", "s02": "You asked for Battletoads", "s03": "Is it even possible?",
              "s04": "How to read the screen", "s05": "Day 1: power on", "s06": "Goal one: just beat it",
              "s07": "Goal two: shave seconds", "s08": "What's a TAS?", "s09": "By the numbers",
              "s10": "The full run, from power on", "s11": "Outro"}
    (OUT / f"{name}_chapters.txt").write_text("".join(f"{int(a // 60)}:{int(a % 60):02d} {titles[s]}\n" for a, s in chapters),
                                              encoding="utf-8")
    print("wrote", OUT / f"{name}.mp4", f"{t:.1f} s ({int(t // 60)}:{t % 60:04.1f})")


if __name__ == "__main__":
    build()
