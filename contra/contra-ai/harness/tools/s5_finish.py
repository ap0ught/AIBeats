"""Stage 5: replay a solved segment open-loop from its start state on a fresh emulator, check it, time its parts.

    python tools/s5_finish.py <start state> <seg name under logs/s5, e.g. d0> [--keep]

Writes logs/s5/<name>.inputs.txt (the segment alone: its first row is stage 5's first frame) and runs
check_inputs on it. With --keep saves states/s5/s5_first.State (stage 5's first frame), s5_tank1 / s5_tank2 (the
frame each tank is created), s5_boss (auto-scroll start), s5_ufo (the UFO exists), s6_pre_dbg / s6_start_dbg.
The start state is a DEBUG state (stage and weapon written to RAM), so nothing here is part of a run.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import LOGS_DIR, PROJECT  # noqa: E402
from contra.inputs import write_inputs  # noqa: E402
from contra.stages import s5  # noqa: E402
from contra.stages.s1_common import Game, log  # noqa: E402

state, name = sys.argv[1], sys.argv[2]
keep = "--keep" in sys.argv
seg = json.loads((LOGS_DIR / "s5" / f"{name}.seg.json").read_text())
rows = [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
out = LOGS_DIR / "s5" / f"{name}.inputs.txt"
write_inputs(out, rows, f"stage 5 segment from {state} (debug state); row 1 = stage 5's first frame")
g = Game(name="s5_finish")
ev = {"lag": [], "weapons": [], "deaths": [], "ignored": 0}
try:
    g.load_file(state)
    prev = g.r
    ntank = 0
    tank_alive = False
    for i, row in enumerate(rows):
        if keep and i == len(rows) - 1:
            g.save_file("s5/s6_pre_dbg")
        r = g.step_raw(row)
        t = i                                           # frames after stage 5's first frame (row 0 -> L)
        if i == 0:
            ev["L"] = r.frame
            ev["fc_L"], ev["rng_L"] = r.fc, r.rng
            assert r.lr == 4 and r.level == 4, r.summary()
            if keep:
                g.save_file("s5/s5_first")
        if r.level == 4:
            if r.fc == prev.fc and r.lr in (4, 8, 9) and i > 0:
                ev["lag"].append(t)
            st = s5.tank_state(r)[0]
            if st == "drive" and not tank_alive:
                ntank += 1
                tank_alive = True
                ev[f"tank{ntank}_created"] = t
                if keep:
                    g.save_file(f"s5/s5_tank{ntank}")
            if tank_alive and st == "stopped" and f"tank{ntank}_stopped" not in ev:
                ev[f"tank{ntank}_stopped"] = t
            if tank_alive and st in ("dead", "none"):
                tank_alive = False
                ev[f"tank{ntank}_dead"] = t
            if r.auto and "auto" not in ev:
                ev["auto"] = t
                if keep:
                    g.save_file("s5/s5_boss")
            e = s5.ufo(r)
            if e is not None and "ufo_created" not in ev:
                ev["ufo_created"] = t
                if keep:
                    g.save_file("s5/s5_ufo")
            if e is not None and "ufo_x" not in ev and e[4] != 240:
                ev["ufo_x"] = e[4]
            if e is not None and not (e[6] & 0x80) and "ufo_hittable" not in ev:
                ev["ufo_hittable"] = t
            if e is not None and e[3] == 0 and "ufo_dead" not in ev:
                ev["ufo_dead"] = t
            if r.bossdef == 1 and "bossdef" not in ev:
                ev["bossdef"] = t
            if r.lr == 9 and "lost" not in ev:
                ev["lost"] = t
            if r.bossdef == 2 and "hidden" not in ev:
                ev["hidden"] = t
            if r.weapon != prev.weapon:
                ev["weapons"].append((t, f"${r.weapon:02x}"))
            if r.dead and not prev.dead:
                ev["deaths"].append(t)
        elif "level" not in ev:
            ev["level"] = t
        if r.level == 5 and r.lr == 4 and "L6" not in ev:
            ev["L6"] = t
            ev["weapon_L6"], ev["lives_L6"], ev["fc_L6"], ev["rng_L6"] = r.weapon, r.lives, r.fc, r.rng
            if keep:
                g.save_file("s5/s6_start_dbg")
        prev = r
finally:
    g.close()
log(f"{name}: {ev}")
log(f"   STAGE 5 = {ev.get('L6')} frames (rows {len(rows)}; ends on stage 6's first frame: {ev.get('L6') == len(rows) - 1}); "
    f"weapon ${ev.get('weapon_L6', 0):02x}; deaths {ev['deaths']}; lag frames in play {len(ev['lag'])}")
(LOGS_DIR / "s5" / f"{name}.report.json").write_text(json.dumps(ev, indent=1, default=str), encoding="utf-8")
rc = subprocess.call([sys.executable, str(PROJECT / "check_inputs.py"), str(out)])
log("check_inputs exit code", rc)
