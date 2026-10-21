"""Offline test of base_fight3.repair_lost on the Eye phase of the second pass's runs (logs/s2t/eye_caps.pkl):
pretend the pad is not read on every frame on which the buttons change, and count how often the repair works."""
import pickle
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages import base_bsim as bs, base_bplan as bp, base_fight3 as f3  # noqa: E402

caps = pickle.load(open(ROOT / "logs" / "s2t" / "eye_caps.pkl", "rb"))
goal = lambda s: s.bossdef  # noqa: E731
for tag, c in caps.items():
    sim0 = bs.Sim.from_ram(c["ram"])
    pad0 = bp.pad_from_rows(c["rows"])
    acts = [bp.act_of_row(tuple(r)) for r in c["rest"]]
    prev0 = bp.act_of_row(c["rows"][-1])
    bs.HZ_MARGIN = 0
    base = f3.bf.model_outcome(sim0, pad0, acts, goal)
    ok = fail = 0
    worst = 0.0
    ks = []
    for i in range(len(acts)):
        prev = acts[i - 1] if i else prev0
        if acts[i] == prev:
            continue
        s, pad = bp.play(sim0, pad0, acts[:i])
        t = time.time()
        rep = f3.repair_lost(s, pad, prev, acts[i:], goal)
        worst = max(worst, time.time() - t)
        if rep is None:
            fail += 1
        else:
            ok += 1
            ks.append(rep[1])
    print(f"{tag}: the executed rows reach the flag in the model after {base} frames (run: {len(acts)}); frames with "
          f"a button change: {ok + fail}; repaired {ok}, not {fail}; dropped-frame index k: {sorted(ks)[:12]}... "
          f"slowest repair search {worst:.2f} s")
