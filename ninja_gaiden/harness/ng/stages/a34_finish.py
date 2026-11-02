"""Acts 3-4: finish a stage after its last play input: wait out the tally / exit, skip a cutscene with the earliest
legal Start (held 2 frames), stop on the next stage's load frame (first frame with the new $6D).

    from a34_finish import finish
    rows, load_frame = finish(e, stage)       # e positioned after the last play frame; rows = what to append
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402
from ng.mode import TICKS  # noqa: E402


def finish(e, stage, max_frames=1500):
    e.tick(TICKS)
    try:
        base = e.msave()
        t0 = e.state().frame
        rows = []
        # walk with no input until the stage changes or the cinematic engine runs
        e.trace(True)
        cs_at = None
        n = 0
        while n < max_frames:
            s = e.step((), 1)
            n += 1
            rows.append(())
            if s.stage != stage:
                e.trace(False)
                return rows, s.frame
            if s.get("cs", 0) > 0:
                cs_at = n
                break
        e.trace(False)
        if cs_at is None:
            raise RuntimeError("no stage change and no cutscene")
        best = None
        for off in range(-2, 12):
            k = cs_at + off
            if k < 1:
                continue
            e.mload(base)
            pre = [()] * (k - 1) + [("Start",), ("Start",)]
            e.run(pre)
            m, s = e.until(0x6D, "ne", stage, 900)
            if s.stage != stage:
                load = s.frame
                if best is None or load < best[0]:
                    best = (load, pre + [()] * m)
        if best is None:
            raise RuntimeError("Start never skipped the cutscene")
        e.mload(base)
        e.run(best[1])
        e.mfree(base)
        return best[1], best[0]
    finally:
        e.tick(None)
