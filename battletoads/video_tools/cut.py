"""Join the pieces into the video.

    python cut.py draft          -> out/draft.mp4  (picture + music/sfx/game sound, no narration yet)

Section order and pieces: sections.py writes clips/<section>.list; s01/s02 are single clips; s04 and s10 come from
run1080. Each piece is clips/<name>.mp4 (+ clips/<name>.wav). Agent-made clips get their wav from <name>.sfx.json.
When the narration exists (voice/<section>.wav), each section is fitted to it (see fit_section)."""
from __future__ import annotations

import json
import subprocess
import sys

import numpy as np

from style import *  # noqa: F401,F403
import audio

ORDER = ["s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10", "s11"]
BED_GAIN = 0.16
FIXED = {"s01": ["s01_montage", "title_card"], "s02": ["s02_asked"], "s04": ["s04_screen"], "s10": ["s10_run"]}


def dur_of(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip())


def nframes_of(p):
    return int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                               "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout.strip())


def pieces(sec):
    if sec in FIXED:
        return FIXED[sec]
    lst = CLIPS / f"{sec}.list"
    return lst.read_text(encoding="utf-8").split() if lst.exists() else []


def piece_audio(name, n):
    """the piece's wav, or one built from its sfx cues, padded/trimmed to n video frames"""
    dur = n / NES_FPS
    wav = CLIPS / f"{name}.wav"
    if wav.exists():
        x = audio.load(wav)
    else:
        m = audio.Mix(dur + 1)
        m.add_cues(0, CLIPS / f"{name}.sfx.json", 0.7)
        x = m.buf
    want = int(round(dur * audio.SR))
    if len(x) < want:
        x = np.concatenate([x, np.zeros((want - len(x), 2), np.float32)])
    return x[:want]


def draft(out_name="draft"):
    vids, auds, chapters = [], [], []
    t = 0.0
    missing = []
    for sec in ORDER:
        chapters.append((t, sec))
        for name in pieces(sec):
            p = CLIPS / f"{name}.mp4"
            if not p.exists():
                missing.append(name)
                continue
            n = nframes_of(p)
            vids.append(p)
            if name == "s10_run":                           # the run carries its own sound
                a = audio.load(p)
                want = int(round(n / NES_FPS * audio.SR))
                a = np.concatenate([a, np.zeros((max(0, want - len(a)), 2), np.float32)])[:want]
            else:
                a = piece_audio(name, n)
            auds.append(a)
            t += n / NES_FPS
    lst = OUT / f"{out_name}.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in vids), encoding="utf-8")
    vtmp = OUT / f"{out_name}_v.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vtmp)], check=True)
    mix = np.concatenate(auds) if auds else np.zeros((1, 2), np.float32)
    # a quiet chiptune bed under the talking sections (s03..s09), faded in and out at the edges
    starts = dict((s, t0) for t0, s in chapters)
    b0, b1 = starts.get("s03"), starts.get("s10")
    if b0 is not None and b1 is not None and b1 > b0:
        bed = audio.chiptune(bars=int((b1 - b0) / 1.6) + 2, bpm=150, intensity=0.35)
        i0, i1 = int(b0 * audio.SR), int(b1 * audio.SR)
        bed = bed[:i1 - i0]
        fade = np.ones(len(bed), np.float32)
        fl = int(1.5 * audio.SR)
        fade[:fl] = np.linspace(0, 1, fl); fade[-fl:] = np.linspace(1, 0, fl)
        mix[i0:i0 + len(bed)] += bed * fade[:, None] * BED_GAIN
    peak = np.abs(mix).max() or 1
    if peak > 0.98:
        mix = np.tanh(mix / peak * 1.4) * 0.95
    wav = OUT / f"{out_name}.wav"
    audio.save(wav, mix)
    out = OUT / f"{out_name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vtmp), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(out)], check=True)
    (OUT / f"{out_name}_chapters.json").write_text(json.dumps(chapters), encoding="utf-8")
    print("wrote", out, f"{t:.1f} s", "missing:", missing)
    for c in chapters:
        print(f"  {int(c[0] // 60)}:{c[0] % 60:04.1f}  {c[1]}")




# ------------------------------------------------------------------ fitting the picture to the narration
VOICE = HERE / "voice"
HOLD_FIRST = ("level_losses", "progression", "numbers", "token_phases", "rules", "tas", "record_card", "integrity",
              "architecture", "ramvision", "bike_skip", "rng_chaos", "s05_research", "s06_beaten", "s07_beaten",
              "s07_final", "s04_screen", "s07_tower", "s05_search")
POPINS = {"10a": 2296, "10b": 4137, "10c": 28951, "10d": 41522, "10e": 46084}   # run frames for the voice pop-ins


def voice_file(key):
    for p in sorted(VOICE.glob(f"{key}*")) if VOICE.exists() else []:
        if p.suffix.lower() in (".wav", ".m4a", ".mp3", ".flac", ".aac", ".ogg"):
            return p
    return None


def trim_silence(x, thr=0.01):
    a = np.abs(x).max(1)
    idx = np.nonzero(a > thr)[0]
    if not len(idx):
        return x
    return x[max(0, idx[0] - int(0.08 * audio.SR)): idx[-1] + int(0.25 * audio.SR)]


def held(name, extra):
    """a copy of the piece with its last frame held `extra` seconds longer"""
    src = CLIPS / f"{name}.mp4"
    out = OUT / "held" / f"{name}_{extra:.2f}.mp4"
    out.parent.mkdir(exist_ok=True)
    if not out.exists():
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", f"tpad=stop_mode=clone:stop_duration={extra:.3f}",
                        "-r", FPS, "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def final(out_name="final"):
    vids, auds, voice_track, chapters = [], [], [], []
    t = 0.0
    for sec in ORDER:
        chapters.append((t, sec))
        names = [n for n in pieces(sec) if (CLIPS / f"{n}.mp4").exists()]
        lens = {n: nframes_of(CLIPS / f"{n}.mp4") / NES_FPS for n in names}
        pic = sum(lens.values())
        vf = voice_file(sec[1:])                          # voice/03 is it possible.m4a -> s03
        vo = trim_silence(audio.load(vf)) if vf and sec != "s10" else None
        extra = 0.0
        if vo is not None:
            need_len = len(vo) / audio.SR + 0.9
            extra = max(0.0, need_len - pic)
        holders = [n for n in names if n in HOLD_FIRST] or names
        per = extra / max(1, len(holders))
        sec_start = t
        for n in names:
            p, d = CLIPS / f"{n}.mp4", lens[n]
            if per > 0.05 and n in holders:
                p = held(n, per)
                d += per
            vids.append(p)
            nfr = nframes_of(p)
            if n == "s10_run":
                a = audio.load(p)
            else:
                a = piece_audio(n, nframes_of(CLIPS / f"{n}.mp4"))
            want = int(round(nfr / NES_FPS * audio.SR))
            a = np.concatenate([a, np.zeros((max(0, want - len(a)), 2), np.float32)])[:want]
            auds.append(a)
            t += nfr / NES_FPS
        if vo is not None:
            voice_track.append((sec_start + 0.35, vo))
        if sec == "s10":
            for key, fr in POPINS.items():
                pv = voice_file(key)
                if pv:
                    voice_track.append((sec_start + fr / NES_FPS, trim_silence(audio.load(pv))))
    mix = np.concatenate(auds)
    # duck everything under the voice, then lay the voice on top
    env = np.ones(len(mix), np.float32)
    for t0, vo in voice_track:
        i0 = int(t0 * audio.SR)
        e = np.abs(vo).max(1)
        k = int(0.3 * audio.SR)
        e = np.convolve(e, np.ones(k) / k, mode="same")
        duck = 1 - 0.7 * np.clip(e * 12, 0, 1)
        seg = env[i0:i0 + len(duck)]
        env[i0:i0 + len(seg)] = np.minimum(seg, duck[:len(seg)])
    mix *= env[:, None]
    for t0, vo in voice_track:
        i0 = int(t0 * audio.SR)
        seg = mix[i0:i0 + len(vo)]
        mix[i0:i0 + len(seg)] += vo[:len(seg)] * 1.0
    peak = np.abs(mix).max() or 1
    if peak > 0.98:
        mix = np.tanh(mix / peak * 1.3) * 0.95
    lst = OUT / f"{out_name}.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in vids), encoding="utf-8")
    vtmp = OUT / f"{out_name}_v.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(vtmp)], check=True)
    wav = OUT / f"{out_name}.wav"
    audio.save(wav, mix)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vtmp), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(OUT / f"{out_name}.mp4")], check=True)
    (OUT / f"{out_name}_chapters.json").write_text(json.dumps(chapters), encoding="utf-8")
    print("wrote", OUT / f"{out_name}.mp4", f"{t:.1f} s")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "draft"
    (final if mode == "final" else draft)(sys.argv[2] if len(sys.argv) > 2 else mode)
