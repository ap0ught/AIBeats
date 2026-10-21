"""Stage 1 opening: power-on -> one frame before stage 1's first frame, with legal inputs.

    python tools/s1_open.py            # compare opening variants, then save states/s1/pre_w<k>.State for k in WAITS

These lists are recorded after a core reboot (bridge command `reset`), where the first row is frame 1. In a
replay from a fresh launch (assemble.py) row k is applied on frame k+1 and frame 1 never has input, so the
power-on version of an opening is the same list without its first (empty) row:
logs/s1/open_w<k>_poweron.inputs.txt. Both reach the same state (checked with assemble.py: same `$1A`, `$34`).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import LOGS_DIR  # noqa: E402
from contra.inputs import write_inputs  # noqa: E402
from contra.stages.s1_common import Game, Pad, log  # noqa: E402


def opening(variant: str, title_wait: int = 0):
    """rows from power-on. title_wait empty frames are added before the first press."""
    rows = [()] * (10 + title_wait)                       # frames 2..11+w get nothing
    if variant == "sel_start":                            # Select 2 frames, Start 2 frames overlapping by one
        rows += [("Select",), ("Select", "Start"), ("Start",)]
    elif variant == "start_start":                        # Start 2 frames, release 3, Start 2 frames
        rows += [("Start",), ("Start",), (), (), (), ("Start",), ("Start",)]
    elif variant == "sel2_start2":
        rows += [("Select",), ("Select",), ("Start",), ("Start",)]
    return rows


def run_open(g, rows, maxf=1200):
    g.e.cmd("reset")
    g.pad, g.rows = Pad(), []
    g.sync()
    g.run_raw(rows)
    ev = []
    prev = g.r
    last = None
    while g.r.lr != 4 or g.r.groutine != 5:
        last = g.snap()
        r = g.step(())
        if r.groutine != prev.groutine:
            ev.append((r.frame, "groutine", r.groutine))
        prev = r
        assert len(g.rows) < maxf, r.summary()
    return last, ev


if __name__ == "__main__":
    waits = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [0, 1, 37]
    g = Game(name="s1_open")
    try:
        for v in ("sel_start", "start_start", "sel2_start2"):
            tok, ev = run_open(g, opening(v))
            r = g.r
            log(f"{v}: L = frame {r.frame}, fc {r.fc}, rng {r.rng}, 2P flag $22={r.m[0x22]} $1D={r.m[0x1D]}, konami $24={r.m[0x24]} "
                f"$3F={r.m[0x3F]}, lives {r.lives}, weapon ${r.weapon:02x}, lag {r.lagc}; events {ev}")
        for w in waits:
            tok, ev = run_open(g, opening("sel_start", w))
            L = g.r
            g.restore(tok)                               # one frame before L
            name = f"s1/pre_w{w}"
            g.save_file(name)
            write_inputs(LOGS_DIR / "s1" / f"open_w{w}.inputs.txt", g.rows, f"stage 1 opening (after a core reboot: row 1 = frame 1), title_wait={w}; next row is stage 1's first frame (frame {L.frame})")
            write_inputs(LOGS_DIR / "s1" / f"open_w{w}_poweron.inputs.txt", g.rows[1:], f"stage 1 opening for a fresh launch (row k = frame k+1), title_wait={w}; next row is stage 1's first frame (frame {L.frame})")
            log(f"title_wait {w}: saved states/{name}.State at frame {g.r.frame} ({len(g.rows)} rows); L = {L.frame}, fc at L {L.fc}, rng at L {L.rng}, "
                f"1P={L.m[0x22] == 0}, konami={L.m[0x24]}")
    finally:
        g.close()
