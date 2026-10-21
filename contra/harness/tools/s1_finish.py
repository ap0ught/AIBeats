"""Stage 1: join the opening and a solved segment, replay from power-on, check, and save the hand-over states.

    python tools/s1_finish.py <w, e.g. w0> [--keep]      # uses logs/s1/open_<w>.inputs.txt + logs/s1/<w>.seg.json

Writes logs/s1/s1_<w>_full.inputs.txt (power-on -> stage 2's first frame, in the harness's convention: row k is
applied on emulator frame k+1 of a fresh launch, frame 1 never has input; `python assemble.py x <that file>`
replays it) and, with --keep (the run to hand on):
    states/s1/s1_first.State        stage 1's first frame ($2C == 4)
    states/s1/s1_boss.State         the frame the boss auto-scroll starts
    states/s1/s1_kill.State         the frame the core's HP reaches 0
    states/s1/s2_pre_legal.State    one frame before stage 2's first frame
    states/s1/s2_start_legal.State  stage 2's first frame
Prints the stage timeline and runs check_inputs on the whole list.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import LOGS_DIR, PROJECT  # noqa: E402
from contra.inputs import read_inputs, write_inputs  # noqa: E402
from contra.stages.s1_common import Game, Pad, log  # noqa: E402
from contra.stages import s1  # noqa: E402

w = sys.argv[1]
keep = "--keep" in sys.argv
opening = read_inputs(LOGS_DIR / "s1" / f"open_{w}.inputs.txt")
seg = json.loads((LOGS_DIR / "s1" / f"{w}.seg.json").read_text())
rows = [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
# open_<w>.inputs.txt was recorded after a core reboot, where its first (empty) row is frame 1. A fresh launch
# gives the bridge control only after frame 1, so the power-on list starts with the opening's second row.
assert opening[0] == ()
full = list(opening) + rows
out = LOGS_DIR / "s1" / f"s1_{w}_full.inputs.txt"
write_inputs(out, full[1:], f"power-on to stage 2's first frame (row k = frame k+1 of a fresh launch); opening "
             f"{len(opening) - 1} rows (title_wait in the name: {w}) + stage 1 {len(rows)} rows")
g = Game(name="s1_finish")
ev = {}
try:
    g.e.cmd("reset")
    g.pad, g.rows = Pad(), []
    g.sync()
    lag_in = 0
    ignored = 0
    prev = g.r
    for i, row in enumerate(full):
        if keep and i == len(full) - 1:
            g.save_file("s1/s2_pre_legal")
        r = g.step_raw(row)
        if "L" not in ev and r.groutine == 5 and r.lr == 4 and r.level == 0:
            ev["L"] = r.frame
            ev["fc_L"], ev["rng_L"] = r.fc, r.rng
            ev["mode"] = (r.m[0x22], r.m[0x24], r.m[0x3F])
            if keep:
                g.save_file("s1/s1_first")
        if "L" in ev and "L2" not in ev:
            if r.fc == prev.fc and r.lr in (4, 8, 9):
                ev.setdefault("lag_frames", []).append(r.frame - ev["L"])
            if r.auto and "auto" not in ev:
                ev["auto"] = r.frame
                if keep:
                    g.save_file("s1/s1_boss")
            if "kill" not in ev and "auto" in ev and s1.door_hp(r) == 0:
                ev["kill"] = r.frame
                if keep:
                    g.save_file("s1/s1_kill")
            if r.bossdef == 1 and "bossdef" not in ev:
                ev["bossdef"] = r.frame
            if r.lr == 9 and "lost" not in ev:
                ev["lost"] = r.frame
            if r.bossdef == 2 and "hidden" not in ev:
                ev["hidden"] = r.frame
            if r.level == 1 and "level" not in ev:
                ev["level"] = r.frame
            if r.weapon != prev.weapon:
                ev.setdefault("weapons", []).append((r.frame - ev["L"], f"${r.weapon:02x}"))
            if r.dead and not prev.dead:
                ev.setdefault("deaths", []).append(r.frame)
            if r.level == 1 and r.lr == 4:
                ev["L2"] = r.frame
                ev["weapon_L2"], ev["lives_L2"], ev["fc_L2"], ev["rng_L2"] = r.weapon, r.lives, r.fc, r.rng
                ev["lag_total"] = r.lagc
                if keep:
                    g.save_file("s1/s2_start_legal")
        prev = r
finally:
    g.close()
L = ev["L"]
rel = {k: (v - L if isinstance(v, int) and k in ("auto", "kill", "bossdef", "lost", "hidden", "level", "L2") else v) for k, v in ev.items()}
log(f"{w}: L = frame {L} (fc {ev['fc_L']}, rng {ev['rng_L']}; 2P flag/konami/konami progress {ev['mode']})")
log(f"   relative to L: {rel}")
log(f"   STAGE 1 = {ev.get('L2', 0) - L} frames; reaches stage 2's first frame: {'L2' in ev and ev['L2'] == len(full)}; "
    f"weapon ${ev.get('weapon_L2', 0):02x}; deaths {ev.get('deaths', [])}; lag frames in play (relative) {ev.get('lag_frames', [])}")
(LOGS_DIR / "s1" / f"s1_{w}_full.report.json").write_text(json.dumps({"events": ev, "relative": rel}, indent=1, default=str), encoding="utf-8")
rc = subprocess.call([sys.executable, str(PROJECT / "check_inputs.py"), str(out)])
log("check_inputs exit code", rc)
