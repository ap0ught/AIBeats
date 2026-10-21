"""DEBUG ONLY: stage 5 start states for different start conditions (never part of a run).

    python tools/s5_mkstates.py <title_wait,title_wait,...> [stage]

Same method as tools/mk_stage_state.py (the stage number is written into RAM on the frame the game clears its
variables, the weapon $13 one frame before the stage's first frame), but after stage 1's legal opening with
`title_wait` extra frames on the title screen, so the frame counter and the random number the stage starts with
differ. Saves states/s5/pre_w<k>.State = one frame before the stage's first frame.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s1_common import Game, Pad, log  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from s1_open import opening  # noqa: E402

waits = [int(x) for x in sys.argv[1].split(",")]
stage = int(sys.argv[2]) if len(sys.argv) > 2 else 5
g = Game(name="s5_mk")
try:
    for w in waits:
        g.e.cmd("reset")
        g.pad, g.rows = Pad(), []
        g.sync()
        g.run_raw(opening("sel_start", w))
        while not (g.r.groutine == 5 and g.r.lr == 0):
            g.step(())
            assert len(g.rows) < 900
        g.e.poke(0x30, stage - 1)
        last = None
        while True:
            tok = g.snap()
            r = g.step(())
            if r.lr == 4:
                break
            if last:
                g.free(last)
            last = tok
            assert len(g.rows) < 3000
        g.restore(tok)
        g.e.poke(0xAA, 0x13)
        g.sync()
        name = f"s{stage}/pre_w{w}"
        g.save_file(name)
        r = g.step(())
        log(f"title_wait {w}: states/{name}.State at frame {r.frame - 1}; L = {r.frame}, level {r.level}, lr {r.lr}, "
            f"weapon ${r.weapon:02x}, fc {r.fc}, rng {r.rng}, lives {r.lives}")
finally:
    g.close()
