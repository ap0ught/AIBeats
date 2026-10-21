"""DEBUG ONLY: make a savestate at the start of any stage by writing RAM (never part of a run).

    python tools/mk_stage_state.py <stage 1-8> [weapon byte, e.g. 0x13] [lives]

Plays the normal opening from power-on (Select on frame 11, Start on frame 12). On frame 340 the game has just
cleared its variables (game routine 4 -> 5) and has not loaded a level yet: CURRENT_LEVEL ($30) is poked there, so
the game itself loads that stage with its normal code. When the stage's first playable frame is one frame away
(level routine 3 -> 4) the weapon byte ($AA) is poked. Saves states/dbg/s<stage>_pre.State (one frame before the
first playable frame L) and prints L. These states exist to study a stage in isolation; frame counts measured
from them are per-stage facts, not a run.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk, LOGS_DIR  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import F  # noqa: E402

stage = int(sys.argv[1])
weapon = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x13
lives = int(sys.argv[3]) if len(sys.argv) > 3 else None
opening = read_inputs(LOGS_DIR / "open_nh.inputs.txt")
with BizHawk(log_name=f"mkstage{stage}.log", fields=F) as e:
    s = e.run(opening[:339])                      # -> emulator frame 340
    assert s["frame"] == 340 and s["groutine"] == 5 and s["lroutine"] == 0, s
    e.poke(0x30, stage - 1)
    if lives is not None:
        e.poke(0x32, lives)
    n = 0
    sid = None
    while True:
        prev_sid = sid
        sid = e.msave()
        s = e.step((), 1)
        n += 1
        if s["lroutine"] == 4:
            break
        if prev_sid:
            e.mfree(prev_sid)
        assert n < 2000, s
    # sid = state one frame before L
    e.mload(sid)
    e.poke(0xAA, weapon)
    name = f"dbg/s{stage}_pre"
    e.save(name)
    s2 = e.step((), 1)
    print(f"stage {stage}: saved states/{name}.State at frame {s2['frame'] - 1}; L = {s2['frame']} "
          f"(level {s2['level']}, level routine {s2['lroutine']}, weapon ${e.byte(0xAA):02x}, lives {e.byte(0x32)})")
