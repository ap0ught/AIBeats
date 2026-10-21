"""Generate yt/run1080b.py (the route-parametrized run renderer) from yt/run1080.py by named replacements, so the two
stay comparable. Run once: python yt/mk_run1080b.py"""
import ast
import os
from pathlib import Path

YT = Path(__file__).resolve().parent
s = (YT / "run1080.py").read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)


def cut(a_text, b_text, new=""):
    global s
    a, b = s.index(a_text), s.index(b_text)
    assert a < b
    s = s[:a] + new + s[b:]


cut('"""The whole up14 run', "from __future__ import annotations", '''"""A captured run at 1920x1080 (2026-10-10, the corrected run): the game at 5x on the left, the AI panel on the right
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
''')
rep("import track  # noqa: E402\nfrom ramview import Cap  # noqa: E402\n", "from capsync import Sync  # noqa: E402\n")
rep("from render_overlay import load, run_splits, token_at, fmt_run, fmt_delta, fmt_tok  # noqa: E402",
    "from render_overlay import load, token_at, fmt_run, fmt_delta, fmt_tok  # noqa: E402")
rep('''NAME = "up14"
SRC = S.VIDEO / f"{NAME}.mkv"
CUES = YT / "run_cues.json"
OUTFILE = S.OUT / "run1080.mp4"
''', '''NAME = next((sys.argv[i + 1] for i, a_ in enumerate(sys.argv[:-1]) if a_ == "--name"), os.environ.get("RUN_NAME", "run1201"))
SRC = S.VIDEO / f"{NAME}.mkv"
CUES = YT / f"run_cues_{NAME}.json"
OUTFILE = S.OUT / f"run_{NAME}.mp4"
''')
cut("SYNC_FILE = YT", "BG, PANEL, GRID")
rep('''        self.wr = json.loads((S.TOADS / "knowledge" / "wr_splits.json").read_text(encoding="utf-8"))
        self.clock, self.levels, self.finish = run_splits(self.trace, self.n)
        self.cues = json.loads(CUES.read_text(encoding="utf-8")) if CUES.exists() else []
        self.final = next((c for c in self.cues if c["type"] == "final"), None)
        self.hold = S.nframes(self.final.get("dur", 4.0)) if self.final else 0
        self.cap = None

    def capture(self):
        if self.cap is None:
            self.cap = Cap("cap14")
        return self.cap
''', '''        self.wr = json.loads((S.TOADS / "knowledge" / "wr_splits_v2.json").read_text(encoding="utf-8"))
        lv = json.loads((S.LOGS / f"{NAME}.levels.json").read_text(encoding="utf-8"))
        self.clock, self.finish = lv["clock"], lv["finish"]
        self.levels = [tuple(x) for x in lv["levels"]]        # (level byte, enter frame, end = first black frame)
        self.cues = json.loads(CUES.read_text(encoding="utf-8")) if CUES.exists() else []
        self.final = next((c for c in self.cues if c["type"] == "final"), None)
        self.hold = S.nframes(self.final.get("dur", 1.5)) if self.final else 0
        self.sync = Sync(NAME)
''')
cut("_SYNC = None", "def logo_fit(text, size, maxw, **kw):")        # the object-tracking cue: never used in a run video
rep('''    lg = logo_fit(c.get("text", "12:23.39"), 210, GW - 120)''', '''    lg = logo_fit(c.get("text", ""), 210, GW - 120)''')
rep('''        sub = c.get("sub", "WORLD RECORD 12:29.25  ·  5.86 s FASTER")''', '''        sub = c.get("sub", "")''')
rep('''    """the 1280x1080 game area for input frame k with the cues active at k drawn over it"""
    g = nes.crop((0, TOP, 256, TOP + 216)).resize((GW, GH), Image.NEAREST)
    if hold_t is not None:
        return cue_final(g, run.final, hold_t, run)
''', '''    """the 1280x1080 game area for input frame k with the cues active at k drawn over it; from the final cue's frame on
    the final card lies over the live picture (hold_t: seconds into the frozen last frame)"""
    g = nes.crop((0, TOP, 256, TOP + 216)).resize((GW, GH), Image.NEAREST)
    if run.final and k >= run.final["frame"]:
        return cue_final(g, run.final, (k - run.final["frame"]) / S.NES_FPS + (hold_t or 0.0), run)
''')
rep('''    order = {"track": 0, "credit": 1}
    for c, t in sorted(act, key=lambda ct: order.get(ct[0]["type"], 9)):
        if c["type"] == "track":
            cue_track(g, c, t, run, k)
        elif c["type"] == "credit":
            cue_credit(g, c, t)
''', '''    for c, t in act:
        if c["type"] == "credit":
            cue_credit(g, c, t)
''')
cut("def lead_in(run):", "def render_part(a, b, out, with_audio, lead, hold=True, run=None):")
cut("def render_part(a, b, out, with_audio, lead, hold=True, run=None):", "def main():", '''def render_part(a, b, out, with_audio, hold=True, run=None):
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


''')
cut("def main():", 'if __name__ == "__main__":', '''def main():
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
    lst.write_text("".join(f"file '{p.as_posix()}'\\n" for p in parts), encoding="utf-8")
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


''')
ast.parse(s)
out = YT / "run1080b.py"
tmp = out.with_suffix(".py.tmp")
tmp.write_text(s, encoding="utf-8", newline="\n")
os.replace(tmp, out)
for bad in ("track.", "Cap(", "lead_in", "cap_row", "run_splits", "cue_track", "EXTRA_NAMES", "NOT_ENEMIES"):
    if bad in s:
        print("still present:", bad)
print("wrote", out, len(s.splitlines()), "lines")
