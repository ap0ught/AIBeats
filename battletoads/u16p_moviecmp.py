"""NesHawk port of up16b2: does the hands-off .bk2 playback give the RAM of the bridge replay?

    python u16p_moviecmp.py <movie tag> <capture tag> [lead]

`core_check_toads.py movie <movie tag> <file.bk2> --keep-header` plays a movie with no joypad calls and writes
logs/fix/core_<movie tag>.movie.tsv: an info line (system, board, memory domains = which core really loaded) and, at
every level-byte change and every 600 frames, "movie frame, level byte, lag count, SHA-256 of the 2 KB RAM".
`core_check_toads.py run <capture tag>` keeps the whole RAM of every frame of the bridge replay of the same input list.
The movie has `lead` empty lead-in frames (default 1): movie frame f = replay frame f - lead.
Reads only; prints the comparison.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
mtag, ctag = sys.argv[1], sys.argv[2]
lead = int(sys.argv[3]) if len(sys.argv) > 3 else 1
lines = (FIX / f"core_{mtag}.movie.tsv").read_text().splitlines()
info = dict(p.partition("=")[::2] for p in lines[0].split("\t", 1)[1].split(";"))
domains = info.get("domains", "").split("|")
core = "NesHawk" if "PPU Bus" in domains else "quickerNES"
print(f"movie {mtag}: sys {info.get('sys')}  board {info.get('board')}  config prefers {info.get('pref')}  movie mode {info.get('movie')}  "
      f"movie length {info.get('movielen')}  framecount at start {info.get('framecount')}")
print(f"memory domains: {domains}")
print(f"CORE THAT LOADED (PPU Bus domain present = NesHawk): {core}")
summ = json.loads((FIX / f"core_{ctag}.json").read_text())
R = np.memmap(FIX / f"core_{ctag}.ram", dtype=np.uint8, mode="r").reshape(-1, 0x800)
n = len(R) - 1
print(f"capture {ctag}: core {summ['core_info']['core_seen']}, inputs {summ['inputs']}, {n} frames")
rows = []
for l in lines[1:]:
    fc, lv, lag, h = l.split("\t")
    rows.append((int(fc), int(lv), int(lag), h.strip().lower()))
same = diff = out = 0
first_bad = None
prev_lv = None
cuts = []
shown = []
for fc, lv, lag, h in rows:
    f = fc - lead
    if prev_lv == 13 and lv == 254:
        cuts.append(fc)
    change = lv != prev_lv
    prev_lv = lv
    if f < 0 or f > n:
        out += 1
        continue
    got = hashlib.sha256(R[f].tobytes()).hexdigest()
    ok = got == h and int(R[f, 0x10]) == lv
    same += ok
    diff += not ok
    if not ok and first_bad is None:
        first_bad = (fc, f, lv, int(R[f, 0x10]))
    if change:
        shown.append(f"  movie frame {fc} = replay frame {f}: level byte {lv}  sha256 {h[:12]}  replay {got[:12]}  {'same RAM' if ok else 'DIFFERENT'}")
print(f"marks in the movie log: {len(rows)}; compared {same + diff}; RAM identical at {same}; different at {diff}; outside the capture {out}")
if first_bad:
    print("FIRST DIFFERENCE: movie frame %d (replay frame %d): level byte movie %d, replay %d" % first_bad)
for s in shown[-14:]:
    print(s)
print(f"13 -> 254 in the movie: frames {cuts} (replay frames {[c - lead for c in cuts]}); the second is the cut to Professor T. Bird")
last = rows[-1]
f = last[0] - lead
if 0 <= f <= n:
    print(f"last mark: movie frame {last[0]} = replay frame {f}: {'same RAM as the replay' if hashlib.sha256(R[f].tobytes()).hexdigest() == last[3] else 'DIFFERENT RAM'}"
          f" (replay sha1 {hashlib.sha1(R[f].tobytes()).hexdigest()})")
print("VERDICT:", "MOVIE MATCHES THE REPLAY on " + core if diff == 0 and same > 0 and len(cuts) >= 2 else "MISMATCH or incomplete")
