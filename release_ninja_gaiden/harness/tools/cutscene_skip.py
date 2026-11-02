"""Which cutscenes can Start skip, how early, and what it saves. Uses the TAS replay as the vehicle.

    python tools/cutscene_skip.py [route=tas4751]

Needs logs/<route>.inputs.txt (bk2 numbering, played after reset) and logs/<route>.events.json (tools/events.py).
For every cutscene run in the events: the TAS's inputs are replayed up to the cutscene's first frame (savestate
there: states/cs/<route>_<n>.State), then
  natural:  no input until play (the main loop, gm) resumes   -> frames to play
  skipped:  greedy - on every frame try a one-frame Start; keep it if a script ended (csskip) on that frame or
            the next two, else play the
            frame with no input; until play resumes             -> the press frames, the first play frame
Writes knowledge/cutscene_skip.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, KNOWLEDGE_DIR, LOGS_DIR  # noqa: E402
from ng.inputs import read_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402


def until_play(e, limit=6000):
    for n in range(1, limit + 1):
        s = e.step((), 1)
        if s.gm:
            return s.frame, n
    return None, limit


if __name__ == "__main__":
    route = sys.argv[1] if len(sys.argv) > 1 else "tas4751"
    rows = read_inputs(LOGS_DIR / f"{route}.inputs.txt")
    ev = json.loads((LOGS_DIR / f"{route}.events.json").read_text(encoding="utf-8"))
    out = []
    e = BizHawk(log_name="cutscene_skip.log")
    try:
        e.reset()
        e.tick(TICKS)
        done = 0
        for n, c in enumerate(ev["cutscenes"]):
            f0 = c["first"]
            if f0 - 1 > len(rows):
                break
            e.run(rows[done:f0 - 1])          # stop on the frame before the cutscene's first frame
            done = f0 - 1
            base = e.msave()
            e.save(f"cs/{route}_{n:02d}")
            rec = {"n": n, "stage": c["stage"], "first": f0, "last": c["last"], "tas_skipped": c["skipped"]}
            nat_play, nat_n = until_play(e)
            rec["natural_play_frame"] = nat_play
            e.mload(base)
            presses = []
            play = None
            for k in range(0, 6000):            # greedy: the earliest Start that ends a script, again and again
                sid = e.msave()
                s = e.step(("Start",), 1)
                e.trace(True)
                e.run([()] * 2)                 # the script loop may run the end code one or two frames later
                after = e.last_trace
                e.trace(False)
                hit = s.csskip or any(x.csskip for x in after)
                if hit and (nat_play is None or s.frame < nat_play - 5):
                    presses.append(s.frame)
                    e.mfree(sid)
                    s = after[-1]
                    if any(x.gm for x in after):
                        play = next(x.frame for x in after if x.gm)
                        break
                else:
                    e.mload(sid)
                    e.mfree(sid)
                    s = e.step((), 1)
                if s.gm:
                    play = s.frame
                    break
            rec.update({"start_presses": presses, "skipped_play_frame": play,
                        "saved_vs_natural": (nat_play - play) if (nat_play and play) else None})
            print(rec, flush=True)
            out.append(rec)
            e.mload(base)
            e.mfree(base)
    finally:
        e.close()
    (KNOWLEDGE_DIR / "cutscene_skip.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
