"""Verifier's own scan of a route input list: banned presses, Start, controller-2 tokens, press rates, and (optionally)
whether the list equals the intro + the named segment files.

    python u16v_scan.py <inputs file> [segment ...]
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
P1 = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")

path = Path(sys.argv[1])
segs = sys.argv[2:]
raw_bytes = path.read_bytes()
text = raw_bytes.decode("utf-8")
crlf = text.count("\r\n")
stray_cr = text.count("\r") - crlf
print(f"line endings: {crlf} CRLF, {text.count(chr(10)) - crlf} bare LF, {stray_cr} stray CR (the CR of a CRLF is stripped; nothing else is)")
rows = [r[:-1] if r.endswith("\r") else r for r in text.split("\n")]
header = rows[0]
if rows[-1] == "":
    rows = rows[:-1]
lines = rows[1:]
print(f"file {path} sha1 {hashlib.sha1(raw_bytes).hexdigest()} header {header!r} input lines {len(lines)}")
frames = []
unknown = Counter()
odd_chars = Counter()
for n, ln in enumerate(lines, 1):
    for ch in ln:
        if not (ch.isalpha() or ch in ",+"):
            odd_chars[ch] += 1
    toks = [t for t in ln.replace("+", ",").split(",") if t]
    for t in toks:
        if t not in P1:
            unknown[t] += 1
    if len(set(toks)) != len(toks):
        print(f"  frame {n}: duplicate token in {ln!r}")
    frames.append(frozenset(toks))
print("tokens that are not one of the 8 controller-1 buttons (P2 prefixes, typos, anything):", dict(unknown) or "none")
print("characters other than letters , + in input lines:", dict(odd_chars) or "none")
lr = [n for n, f in enumerate(frames, 1) if "Left" in f and "Right" in f]
ud = [n for n, f in enumerate(frames, 1) if "Up" in f and "Down" in f]
st = [n for n, f in enumerate(frames, 1) if "Start" in f]
se = [n for n, f in enumerate(frames, 1) if "Select" in f]
print(f"Left+Right frames: {len(lr)} {lr[:20]}")
print(f"Up+Down frames: {len(ud)} {ud[:20]}")
print(f"Start frames: {len(st)} {st}")
print(f"Select frames: {len(se)}; first {se[:10]} last {se[-10:]}")
cnt = Counter()
for f in frames:
    for b in f:
        cnt[b] += 1
print("frames held per button:", {b: cnt[b] for b in P1})
print("frames with no button:", sum(1 for f in frames if not f))
combos = Counter(",".join(sorted(f)) for f in frames)
print("distinct button combinations:", len(combos))
for c, k in combos.most_common():
    print(f"   {k:6d}  {c or '(none)'}")
# press rates: new presses of one button inside any 60-frame window; and alternating 1-frame A/B mashing
for b in ("A", "B", "Select", "Left", "Right", "Up", "Down"):
    downs = [n for n in range(1, len(frames) + 1) if b in frames[n - 1] and (n == 1 or b not in frames[n - 2])]
    best, where = 0, None
    j = 0
    for i in range(len(downs)):
        while downs[i] - downs[j] >= 60:
            j += 1
        if i - j + 1 > best:
            best, where = i - j + 1, downs[j]
    print(f"button {b}: {len(downs)} presses; most presses inside one 60-frame window: {best} (window starts at frame {where})")
# runs of frame-by-frame alternation (A,B,A,B or A,-,A,-): frames where the A state flips every frame for >= 6 frames
def flips(b):
    out, start, run = [], None, 0
    for n in range(2, len(frames) + 1):
        if (b in frames[n - 1]) != (b in frames[n - 2]):
            if run == 0:
                start = n - 1
            run += 1
        else:
            if run >= 6:
                out.append((start, run + 1))
            run = 0
    if run >= 6:
        out.append((start, run + 1))
    return out
for b in ("A", "B", "Select"):
    fl = flips(b)
    print(f"button {b}: stretches where it toggles on every frame for 7+ frames (30 presses/s): {len(fl)}; total frames {sum(r for _, r in fl)}")
    for s0, r in fl:
        print(f"     frames {s0}-{s0 + r - 1} ({r})")
if segs:
    intro = [("Right", 1170), ("Start", 4), ("A", 727), ("", 16)]
    built = []
    for b, n in intro:
        built += [b] * n
    bounds = [("intro", 1, len(built))]
    for name in segs:
        j = json.loads((HERE / "logs" / f"pbeam_{name}.json").read_text())
        a = len(built) + 1
        built += j["inputs"]
        bounds.append((name, a, len(built)))
    norm = [frozenset(t for t in x.replace("+", ",").split(",") if t) for x in built]
    print(f"intro + segments {segs}: {len(norm)} frames; equal to the file frame for frame: {norm == frames}")
    if norm != frames:
        for i, (x, y) in enumerate(zip(norm, frames), 1):
            if x != y:
                print("  first difference at frame", i, sorted(x), sorted(y))
                break
        print("  lengths", len(norm), len(frames))
    for name, a, b in bounds:
        print(f"   {name:16s} frames {a:6d}-{b:6d} ({b - a + 1})")
