"""NesHawk port of up17 (copy of u17p_scan.py) (track "NESHAWK PORT"): scan of a ported input list and of its per-frame RAM capture.

    python u17p_scan.py <inputs file> [<capture tag>]      e.g. u17p_scan.py logs/fix/core_u17p.inputs.txt u17v1

Part 1 (the file alone): tokens that are not one of the 8 controller-1 buttons, Left+Right / Up+Down frames, every
Start frame, Select frames, fastest press rates.
Part 2 (with a capture made by `core_check_toads.py run <tag> --inputs <that file> --tail 0`): the events read from the
captured RAM - landing ($3B5 5 -> 4 in Level 1), every level-byte change, the Queen's last hit, both 13 -> 254 cuts -
and the run time (second cut - landing) / 60.0988; the game's own pad bytes ($29 controller 1, $2A / $2C controller 2).

Reads only. Writes nothing but its stdout.
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
P1 = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")
NTSC = 60.0988
RECORD_S = 749.25


def clock(fr):
    s = fr / NTSC
    return f"{int(s // 60)}:{s % 60:05.2f}"


path = Path(sys.argv[1])
if not path.is_absolute():
    path = HERE / path
raw = path.read_bytes()
text = raw.decode("utf-8")
rows = [r[:-1] if r.endswith("\r") else r for r in text.split("\n")]
if rows and rows[-1] == "":
    rows = rows[:-1]
header = rows[0] if rows and rows[0].startswith("#") else ""
lines = [r for r in rows if not r.startswith("#")]
print(f"file {path.name}  sha1 {hashlib.sha1(raw).hexdigest()}  header {header!r}  input frames {len(lines)}")
frames = []
unknown, odd = Counter(), Counter()
for n, ln in enumerate(lines, 1):
    for ch in ln:
        if not (ch.isalpha() or ch in ",+"):
            odd[ch] += 1
    toks = [t for t in ln.replace("+", ",").split(",") if t]
    for t in toks:
        if t not in P1:
            unknown[t] += 1
    frames.append(frozenset(toks))
lr = [n for n, f in enumerate(frames, 1) if "Left" in f and "Right" in f]
ud = [n for n, f in enumerate(frames, 1) if "Up" in f and "Down" in f]
st = [n for n, f in enumerate(frames, 1) if "Start" in f]
se = [n for n, f in enumerate(frames, 1) if "Select" in f]
print("tokens that are not one of the 8 controller-1 buttons (P2, typos, anything):", dict(unknown) or "none")
print("characters other than letters , + :", dict(odd) or "none")
print(f"Left+Right frames: {len(lr)} {lr[:20]}")
print(f"Up+Down frames: {len(ud)} {ud[:20]}")
print(f"Start frames: {len(st)} {st}")
print(f"Select frames: {len(se)}")
cnt = Counter(b for f in frames for b in f)
print("frames held per button:", {b: cnt[b] for b in P1})
for b in ("A", "B", "Select"):
    downs = [n for n in range(1, len(frames) + 1) if b in frames[n - 1] and (n == 1 or b not in frames[n - 2])]
    best, where, j = 0, None, 0
    for i in range(len(downs)):
        while downs[i] - downs[j] >= 60:
            j += 1
        if i - j + 1 > best:
            best, where = i - j + 1, downs[j]
    print(f"button {b}: {len(downs)} presses; most inside one 60-frame window: {best} (from frame {where})")
banned = len(lr) + len(ud) + sum(unknown.values())

if len(sys.argv) > 2:
    tag = sys.argv[2]
    summ = json.loads((FIX / f"core_{tag}.json").read_text())
    R = np.memmap(FIX / f"core_{tag}.ram", dtype=np.uint8, mode="r").reshape(-1, 0x800)
    meta = np.loadtxt(FIX / f"core_{tag}.meta.tsv", dtype=np.int64, delimiter="\t")
    n = len(R) - 1
    print(f"\ncapture {tag}: core {summ['core_info']['core_seen']} (board {summ['core_info']['board']}), inputs {summ['inputs']}, "
          f"{n} frames, sha1 at the end of the list {summ.get('sha1_at_input_end')}")
    same_file = (HERE / summ["inputs"]).resolve() == path.resolve()
    print(f"capture was made from this input file: {same_file}; frames in the list {len(frames)}, captured {n}")
    lv = R[:, 0x10].astype(int)
    anim = R[:, 0x3B5].astype(int)
    landing = next((f for f in range(1, n + 1) if lv[f] == 1 and anim[f - 1] == 5 and anim[f] == 4), None)
    print(f"landing (level byte 1, $3B5 5 -> 4): frame {landing}")
    changes = [(f, lv[f - 1], lv[f]) for f in range(1, n + 1) if lv[f] != lv[f - 1]]
    first_play = [(f, a, b) for f, a, b in changes if b not in (254, 255)]
    print("level byte arrives at a level (frame: from -> to):", ", ".join(f"{f}: {a}->{b}" for f, a, b in first_play))
    cuts = [f for f, a, b in changes if a == 13 and b == 254]
    print("13 -> 254 changes:", cuts, "(first = cut to the Queen's speech, second = cut to Professor T. Bird)")
    hit = None
    for f in range(1, n + 1):
        if lv[f] == 13:
            ids, pids = R[f, 0x3C1:0x3D0], R[f - 1, 0x3C1:0x3D0]
            if any(int(pids[q]) == 0x7E and int(ids[q]) == 0x46 for q in range(2, 15)):
                hit = f
                break
    print(f"Queen's last hit (0x7E -> 0x46): frame {hit}; hit counter $586 there {int(R[hit, 0x586]) if hit else None}; "
          f"toad health there {int(R[hit, 0x51A]) if hit else None}")
    lagt = int(meta[:, 3].sum())
    print(f"lag frames in the capture: {lagt}" + (f"; from the landing to the T. Bird cut: {int(meta[landing:cuts[1] + 1, 3].sum())}" if landing and len(cuts) > 1 else ""))
    pad = R[:, 0x29].astype(int)
    sbit = [f for f in range(1, n + 1) if pad[f] & 0x10]
    print(f"game's pad byte $29 has the Start bit on {len(sbit)} frames: {sbit[:1]}..{sbit[-1:]}")
    p2a = int((R[1:, 0x2A] != 0).sum())
    p2c = int((R[1:, 0x2C] != 0).sum())
    print(f"second-pad bytes: $2C (new presses) nonzero on {p2c} frames; $2A nonzero on {p2a} frames (the game's own forced walks)")
    deaths = [(f, int(R[f - 1, 0x11]), int(R[f, 0x11])) for f in range(1, n + 1) if R[f, 0x11] != R[f - 1, 0x11]]
    print("lives byte $11 changes (frame, from, to):", deaths)
    if landing and len(cuts) > 1:
        t = cuts[1] - landing
        print(f"\nRUN TIME on {summ['core_info']['core_seen']}: T. Bird cut {cuts[1]} - landing {landing} = {t} frames / {NTSC} = "
              f"{t / NTSC:.3f} s = {clock(t)}; record {RECORD_S} s -> {'UNDER' if t / NTSC < RECORD_S else 'NOT under'} the record by "
              f"{RECORD_S - t / NTSC:.2f} s; old (wrong) finish, Queen's speech cut: {cuts[0]}")
    else:
        print("\nNOT FINISHED: no second 13 -> 254 in the capture")
print(f"\nBANNED PRESSES (Left+Right, Up+Down, non-controller-1 tokens): {banned}; Start frames {len(st)} "
      f"({'all on the title screen, before frame 1300' if st and max(st) < 1300 else 'CHECK'})")
