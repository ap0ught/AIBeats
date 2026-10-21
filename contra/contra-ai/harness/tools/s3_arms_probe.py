"""DEBUG ONLY (RAM pokes, never part of a run): does the number of destroyed dragon arms change the mouth's timing?

    python tools/s3_arms_probe.py [climb_end state=s3/p2_v0_climb_end] [seg=s3/p2_v0.seg.json] [top row=1977]

From the top floor: the run's own trigger jump, then Bill stands still, kept alive by poking the new-life timer
($AE). Three runs: counter $85 (BOSS_SCREEN_ENEMIES_DESTROYED) left alone / poked to 1 / poked to 2 from the frame
the boss scroll ends. Prints the rows (after the scroll start) at which the mouth opens and closes, three cycles.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_lib import Game, LOGS_DIR  # noqa: E402

state = sys.argv[1] if len(sys.argv) > 1 else "s3/p2_v0_climb_end"
seg = sys.argv[2] if len(sys.argv) > 2 else "s3/p2_v0.seg.json"
top = int(sys.argv[3]) if len(sys.argv) > 3 else 1977
rows = [tuple(x for x in r.split("+") if x) for r in json.loads((LOGS_DIR / seg).read_text())["rows"]]
with Game(log_name="s3_arms_probe.log") as g:
    for arms in (None, 1, 2):
        r = g.load(state)
        i = 0
        s0 = None
        ev = []
        was = False
        while i < 1700:
            g.e.poke(0xAE, 100)
            if arms is not None and r.autodone:
                g.e.poke(0x85, arms)
            r = g.step(rows[top + i] if i < 22 else ())
            i += 1
            if s0 is None and r.autoscroll:
                s0 = i
            m = r.m
            k = next((s for s in range(16) if m[0x4B8 + s] and m[0x528 + s] == 0x14), None)
            op = k is not None and m[0x578 + k] < 0xF0 and not (m[0x598 + k] & 0x80)
            if op != was:
                ev.append(("open" if op else "closed", i - (s0 or 0)))
                was = op
        print(f"arms counter {arms}: scroll start at +{s0} rows after the top floor; mouth events (rows after the scroll start): {ev}",
              flush=True)
