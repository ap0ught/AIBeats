"""DEBUG states: the start of every stage, made by RAM pokes ("death warp"). NEVER part of a run.

    python tools/mk_dbg_states.py [base state, default intro_fastest_end]     -> states/dbg/stage_<name>.State

From a 1-1 gameplay state: lives := 2, $6D := stage, $6E := its first room, $8B := $80 (Ryu dead). The game's own
death routine ($E3C9) then waits 190 frames and reloads the room in $6E with stage $6D. The state is saved on the
first main-loop frame after the reload. Differences from a real arrival: lives 1, ninpo halved (0 here), score,
timer reset to 150, $BF (global timer) and everything carried over from the poked state.
Boss stages (1-2 is a whole stage; 2-3, 3-3, 4-4, 5-4, 6-4a, 6-4b, 6-5 start in the boss room) are included.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, STATES_DIR  # noqa: E402
from ng.mode import TICKS  # noqa: E402
from ng.stages import FIRST_ROOM, NAMES  # noqa: E402

if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else "intro_fastest_end"
    e = BizHawk(log_name="mk_dbg_states.log")
    out = {}
    try:
        e.tick(TICKS)
        e.load(base)
        sid = e.msave()
        for k, nm in enumerate(NAMES):
            e.mload(sid)
            e.poke(0x76, 2)
            e.poke(0x6D, k)
            e.poke(0x6E, FIRST_ROOM[k])
            e.poke(0x8B, 0x80)
            seen_death = False
            for _ in range(600):
                s = e.step((), 1)
                if s.dw:
                    seen_death = True
                if seen_death and s.gm:
                    break
            p = e.save(f"dbg/stage_{nm}")
            e.screenshot(f"dbg/stage_{nm}")
            out[nm] = {"stage": s.stage, "room": s.room, "frame": s.frame, "x": s.x, "y": s.y, "timer": s.timer,
                       "lives": s.lives, "state": str(p.relative_to(STATES_DIR.parent))}
            print(nm, out[nm], flush=True)
        (STATES_DIR / "dbg" / "index.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    finally:
        e.close()
