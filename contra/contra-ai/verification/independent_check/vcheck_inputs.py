"""Independent input-rule checker. Reads only the input file. Writes vcheck_inputs.out.json and prints a summary.

Rules checked (the project's own):
  * only the 8 NES buttons of one controller appear (the file format has a single controller column)
  * never Left+Right, never Up+Down on one frame
  * per button: press-to-press gap >= 5 frames, every hold >= 2 frames, every release (between two presses) >= 2
Reported per button: presses, shortest press-to-press gap, shortest hold, shortest release, most presses that START
inside any 60-frame window, and the same for any 6-frame... (not a rule, for information).
Frame numbering: row i (0-based, header skipped) is applied on emulator frame i + 2 of a fresh launch.
"""
import json
import sys
from collections import Counter
from pathlib import Path

BUTTONS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
path = Path(sys.argv[1] if len(sys.argv) > 1 else r"run_chain2.inputs.txt")
raw = path.read_bytes()
text = raw.decode("utf-8")
lines = text.split("\n")
if lines and lines[-1] == "":
    lines = lines[:-1]                       # the final newline terminates the last row
header = [l for l in lines if l.startswith("#")]
rows = []
bad_tokens = Counter()
for l in lines:
    if l.startswith("#"):
        continue
    l = l.rstrip("\r")
    toks = [t for t in l.replace(",", "+").split("+") if t]
    for t in toks:
        if t not in BUTTONS:
            bad_tokens[t] += 1
    if len(set(toks)) != len(toks):
        bad_tokens["<duplicate in row>"] += 1
    rows.append(frozenset(toks))
N = len(rows)
FR = lambda i: i + 2                         # row index -> emulator frame

res = {"file": str(path), "bytes": len(raw), "header": header, "rows": N, "unknown_tokens": dict(bad_tokens)}
res["rows_with_cr"] = text.count("\r")
used = Counter()
for r in rows:
    for b in r:
        used[b] += 1
res["frames_held_per_button"] = {b: used[b] for b in BUTTONS}
lr = [FR(i) for i, r in enumerate(rows) if "Left" in r and "Right" in r]
ud = [FR(i) for i, r in enumerate(rows) if "Up" in r and "Down" in r]
res["left_right_frames"] = lr
res["up_down_frames"] = ud

per = {}
fails = []
for b in BUTTONS:
    held = [b in r for r in rows]
    presses = [i for i in range(N) if held[i] and (i == 0 or not held[i - 1])]
    releases = [i for i in range(N) if not held[i] and i > 0 and held[i - 1]]       # first frame up
    holds = []
    for k, p in enumerate(presses):
        e = p
        while e < N and held[e]:
            e += 1
        holds.append((e - p, p, e == N))          # (length, start row, runs to end of file)
    gaps = [(presses[k + 1] - presses[k], presses[k]) for k in range(len(presses) - 1)]
    rels = []
    for r in releases:
        e = r
        while e < N and not held[e]:
            e += 1
        if e < N:                                  # a release that is followed by another press
            rels.append((e - r, r))
    # most presses starting in any window of W frames
    def densest(W):
        best, at, j = 0, None, 0
        for k in range(len(presses)):
            while presses[k] - presses[j] >= W:
                j += 1
            if k - j + 1 > best:
                best, at = k - j + 1, presses[j]
        return best, (FR(at) if at is not None else None)
    d60 = densest(60)
    d600 = densest(600)
    d1800 = densest(1800)
    d = {
        "presses": len(presses),
        "frames_held": sum(held),
        "min_press_to_press_gap": (min(gaps)[0] if gaps else None),
        "min_gap_at_frame": (FR(min(gaps)[1]) if gaps else None),
        "count_gap_lt5": sum(1 for g in gaps if g[0] < 5),
        "min_hold": (min(holds)[0] if holds else None),
        "min_hold_at_frame": (FR(min(holds)[1]) if holds else None),
        "count_hold_lt2": sum(1 for h in holds if h[0] < 2),
        "min_release": (min(rels)[0] if rels else None),
        "min_release_at_frame": (FR(min(rels)[1]) if rels else None),
        "count_release_lt2": sum(1 for r in rels if r[0] < 2),
        "most_presses_in_60_frames": d60[0],
        "densest_60_window_starts_at_frame": d60[1],
        "most_presses_in_600_frames": d600[0],
        "densest_600_window_starts_at_frame": d600[1],
        "most_presses_in_1800_frames": d1800[0],
        "densest_1800_window_starts_at_frame": d1800[1],
        "gap_histogram_lt12": dict(sorted(Counter(g[0] for g in gaps if g[0] < 12).items())),
        "hold_histogram_lt6": dict(sorted(Counter(h[0] for h in holds if h[0] < 6).items())),
        "release_histogram_lt6": dict(sorted(Counter(r[0] for r in rels if r[0] < 6).items())),
    }
    per[b] = d
    if d600[0] > 109:
        fails.append(f"{b}: {d600[0]} presses in 600 frames from frame {d600[1]} (limit 109)")
    if d1800[0] > 246:
        fails.append(f"{b}: {d1800[0]} presses in 1800 frames from frame {d1800[1]} (limit 246)")
    if d["count_gap_lt5"]:
        fails.append(f"{b}: {d['count_gap_lt5']} press-to-press gaps under 5 (min {d['min_press_to_press_gap']} at frame {d['min_gap_at_frame']})")
    if d["count_hold_lt2"]:
        fails.append(f"{b}: {d['count_hold_lt2']} holds under 2 frames (first at frame {d['min_hold_at_frame']})")
    if d["count_release_lt2"]:
        fails.append(f"{b}: {d['count_release_lt2']} releases under 2 frames (first at frame {d['min_release_at_frame']})")
    if b == "Start":
        res["start_presses"] = [{"frame": FR(p), "hold": h[0]} for p, h in zip(presses, holds)]
    if b == "Select":
        res["select_presses"] = [{"frame": FR(p), "hold": h[0]} for p, h in zip(presses, holds)]
res["per_button"] = per
if lr:
    fails.append(f"Left+Right on {len(lr)} frames (first {lr[0]})")
if ud:
    fails.append(f"Up+Down on {len(ud)} frames (first {ud[0]})")
if bad_tokens:
    fails.append(f"unknown tokens {dict(bad_tokens)}")
# trailing idle rows
t = N
while t > 0 and not rows[t - 1]:
    t -= 1
res["last_nonempty_row_frame"] = FR(t - 1) if t else None
res["trailing_idle_rows"] = N - t
lead = 0
while lead < N and not rows[lead]:
    lead += 1
res["leading_idle_rows"] = lead
res["first_nonempty_row_frame"] = FR(lead) if lead < N else None
# the first 40 non-empty presses, to look for the Konami code (Up Up Down Down Left Right Left Right B A [Start])
seq = []
prev = frozenset()
for i, r in enumerate(rows[:3000]):
    new = r - prev
    for b in BUTTONS:
        if b in new:
            seq.append((FR(i), b))
    prev = r
res["first_presses"] = seq[:40]
res["fails"] = fails
res["verdict"] = "PASS" if not fails else "FAIL"
Path(__file__).with_name("vcheck_inputs.out.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

print("file", path, "bytes", len(raw), "rows", N, "header", header)
print("unknown tokens", dict(bad_tokens), "| CR chars", res["rows_with_cr"])
print("Left+Right frames", len(lr), "| Up+Down frames", len(ud))
print("leading idle rows", lead, "first input frame", res["first_nonempty_row_frame"], "| last input frame",
      res["last_nonempty_row_frame"], "trailing idle rows", res["trailing_idle_rows"])
print(f"{'button':7} {'presses':>7} {'held':>6} {'minGap':>6} {'@':>6} {'minHold':>7} {'@':>6} {'minRel':>6} {'@':>6} {'max/60f':>7} {'@':>6}")
for b in BUTTONS:
    d = per[b]
    print(f"{b:7} {d['presses']:7} {d['frames_held']:6} {str(d['min_press_to_press_gap']):>6} {str(d['min_gap_at_frame']):>6} "
          f"{str(d['min_hold']):>7} {str(d['min_hold_at_frame']):>6} {str(d['min_release']):>6} {str(d['min_release_at_frame']):>6} "
          f"{d['most_presses_in_60_frames']:7} {str(d['densest_60_window_starts_at_frame']):>6}"
          f"  /600f {d['most_presses_in_600_frames']} @{d['densest_600_window_starts_at_frame']}  /1800f {d['most_presses_in_1800_frames']} @{d['densest_1800_window_starts_at_frame']}")
for b in ("B", "A"):
    print(b, "gap histogram (<12):", per[b]["gap_histogram_lt12"], "hold (<6):", per[b]["hold_histogram_lt6"],
          "release (<6):", per[b]["release_histogram_lt6"])
print("Start presses:", res["start_presses"])
print("Select presses:", res["select_presses"])
print("first presses:", res["first_presses"])
print("VERDICT", res["verdict"])
for f in fails:
    print("  FAIL", f)
