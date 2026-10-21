"""DEBUG ONLY (RAM pokes; an experiment, never part of a run): does touching the alien guardian with the Barrier
active destroy it?

    python tools/s8_barrier_touch.py [state=s8/best_guardian_spawn]

From the frame the guardian appears: wait for its forced scroll to end, then (a) set the Barrier timer ($B0) and
put Bill inside the guardian's box (X = its X, Y = its Y) for a few frames, (b) the same without the Barrier.
Prints the guardian's HP / routine before and after.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game  # noqa: E402

state = sys.argv[1] if len(sys.argv) > 1 else "s8/best_guardian_spawn"


def guardian(r):
    for (s, t, ro, hp, x, y, st, at) in r.enemies():
        if t == 0x10:
            return s, ro, hp, x, y, st
    return None


with Game(log_name="s8_barrier_touch.log") as g:
    for barrier in (True, False):
        r = g.load(state)
        for _ in range(80):
            g.e.poke(0xAE, 100)            # keep Bill alive while the guardian scrolls in
            r = g.step(("Right",))
        gd = guardian(r)
        print(f"barrier={barrier}: before: guardian slot/routine/hp/x/y/state {gd}; Bill {r.x},{r.y} lives {r.lives}")
        s, ro, hp, gx, gy, st = gd
        for k in range(12):
            g.e.poke(0xAE, 0)
            g.e.poke(0xB0, 0x80 if barrier else 0)
            g.e.poke(0x334, gx)
            g.e.poke(0x31A, gy)
            g.e.poke(0xA0, 0x11)           # jumping pose (the box the code notes quote)
            r = g.step(())
            gd2 = guardian(r)
            if k < 4 or gd2 is None or gd2[2] != hp:
                print(f"   frame {k}: guardian {gd2}; Bill state {r.pstate} dead {r.dead} barrier timer {r.barrier}")
            if gd2 is None or gd2[2] == 0 or r.dead:
                break
