"""Second pass: replay logs/s1/s1_<w>_full.inputs.txt from a core reboot and save the hand-over states under NEW
names (the first pass's s2_start_legal etc. are in use by the base-stage builder and are not touched).

    python tools/s1b_states.py <w, e.g. w0v2> <suffix, e.g. v2>

Saves states/s1/s2_pre_legal_<suffix>.State (one frame before stage 2's first frame),
s2_start_legal_<suffix>.State (stage 2's first frame), s1_boss_<suffix>.State (auto-scroll start),
s1_kill_<suffix>.State (core HP 0).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from contra.stages.s1_common import Game, Pad, log  # noqa: E402
from contra.stages import s1  # noqa: E402

w, suf = sys.argv[1], sys.argv[2]
full = [()] + [tuple(r) for r in read_inputs(LOGS_DIR / "s1" / f"s1_{w}_full.inputs.txt")]   # reboot: first row = frame 1
g = Game(name="s1b_states")
try:
    g.e.cmd("reset")
    g.pad, g.rows = Pad(), []
    g.sync()
    seen = set()
    for i, row in enumerate(full):
        if i == len(full) - 1:
            g.save_file(f"s1/s2_pre_legal_{suf}")
        r = g.step_raw(row)
        if r.level == 0 and r.lr == 4 and r.auto and "boss" not in seen:
            seen.add("boss")
            g.save_file(f"s1/s1_boss_{suf}")
        if "boss" in seen and "kill" not in seen and s1.door_hp(r) == 0:
            seen.add("kill")
            g.save_file(f"s1/s1_kill_{suf}")
    r = g.r
    ok = r.level == 1 and r.lr == 4
    if ok:
        g.save_file(f"s1/s2_start_legal_{suf}")
    log(f"{w}: after {len(full)} rows from the reboot: frame {r.frame}, level {r.level}, routine {r.lr}, weapon ${r.weapon:02x}, "
        f"lives {r.lives}, fc {r.fc}, rng {r.rng}; stage 2's first frame: {ok}; saved s2_start_legal_{suf} / s2_pre_legal_{suf}")
finally:
    g.close()
