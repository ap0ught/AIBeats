"""Measure the fastest way from power-on to the first controllable frame of stage 1-1 (Start presses only).

    python tools/intro_skip.py

The opening (cinematic script 0, RAM $0300 = script id) is skipped by Start -> script $0D (title, "PUSH START");
Start there -> script $0C (ACT I card); then the stage. For each phase: the earliest frame on which a one-frame
Start press is taken, found by trying every frame from a savestate. Detection: ng.mode TICKS title/act1/csdone. Then: is $0C skippable, and the frame on which
1-1 gameplay starts (first main-loop frame, ng.mode "gm"). Writes logs/intro_fastest.inputs.txt and
knowledge/intro_skip.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, KNOWLEDGE_DIR, LOGS_DIR  # noqa: E402
from ng.inputs import write_inputs  # noqa: E402
from ng.mode import TICKS  # noqa: E402

SCRIPT = 0x300


def earliest(e, want, look=12, limit=1500):
    """From the current emulator position, try Start on the next frame, then the one after, ... Returns
    (rows played = blanks + Start, frame of the press) for the first try after which RAM $0300 == want (or
    gameplay starts, want == 'gm'); the emulator is left right after that press."""
    add = []
    for _ in range(limit):
        sid = e.msave()
        s = e.step(("Start",), 1)
        press_frame = s.frame
        e.trace(True)
        e.run([()] * look)
        tr = e.last_trace
        e.trace(False)
        ok = any(x[want] for x in tr)
        e.mload(sid)
        e.mfree(sid)
        if ok:
            e.step(("Start",), 1)
            return add + [("Start",)], press_frame
        e.step((), 1)
        add.append(())
    return None, None


if __name__ == "__main__":
    out = {}
    e = BizHawk(log_name="intro_skip.log")
    try:
        e.tick(TICKS)
        rows = []
        print("launch framecount", e.state().frame)
        for name, want in (("skip_opening", "title"), ("start_game", "act1"), ("skip_act1_card", "csdone")):
            add, f = earliest(e, want, look=6, limit=1200)
            if add is None:
                print(name, "never within the limit")
                out[name] = None
                continue
            rows += add
            out[name] = {"press_frame": f, "row": len(rows)}
            print(name, "Start on frame", f, "(row", len(rows), ")", flush=True)
        # play on until the first gameplay frame
        e.trace(True)
        n = 0
        while True:
            s = e.step((), 1)
            rows.append(())
            n += 1
            if s.gm or n > 2000:
                break
        e.trace(False)
        out["first_gm_frame"] = s.frame
        out["first_gm_row"] = len(rows)
        print("first gameplay frame", s.frame, s)
        e.save("intro_fastest_end")
        e.screenshot("intro_fastest_end")
        write_inputs(LOGS_DIR / "intro_fastest.inputs.txt", rows, "fastest power-on -> 1-1 (Start presses only), fresh launch")
        p = KNOWLEDGE_DIR / "intro_skip.json"
        p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    finally:
        e.close()
