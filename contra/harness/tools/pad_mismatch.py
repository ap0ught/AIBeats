"""Count frames on which the game's controller byte ($F1) differs from the input sent (NesHawk: DMC conflicts).

    python tools/pad_mismatch.py <state> <movie.inputs.txt> <m> <frames>
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk
from contra.inputs import read_inputs, to_mask
state, movie, m, n = sys.argv[1], read_inputs(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
rows = movie[m - 1:m - 1 + n]
F = {"pad": 0xF1, "lroutine": 0x2C, "pause": 0x25, "death": 0xB4, "fc": 0x1A}
with BizHawk(log_name="padmis.log", fields=F) as e:
    e.load(state); e.trace(True); e.run(rows); tr = e.last_trace
mis = [(i, to_mask(rows[i]), s["pad"]) for i, s in enumerate(tr) if not s["lagged"] and s["lroutine"] == 4 and s["pad"] != to_mask(rows[i])]
lostB = [i for i, a, b in mis if a & 0x40 and not b & 0x40]
print(f"{len(tr)} frames, lag {sum(s['lagged'] for s in tr)}, mismatches {len(mis)}; B presses sent {sum(1 for r in rows if 'B' in r)}, B presses the game did not see {len(lostB)}")
print("mismatch rows (i, sent, seen):", mis[:60])
print("lost B at:", lostB[:80])
