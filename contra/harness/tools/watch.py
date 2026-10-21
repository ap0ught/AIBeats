"""Load a state, play rows of a movie (or nothing), and at chosen frame offsets print the enemy / bullet tables
and save a screenshot.

    python tools/watch.py <state> <movie.inputs.txt|-> <m> <i1,i2,...> [--edits seg.json] [--shots prefix]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import apply_edit  # noqa: E402

args = sys.argv[1:]


def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]
        return v
    return default


edits, shots = opt("--edits", None), opt("--shots", None)
state, mv, m = args[0], args[1], int(args[2])
marks = sorted(int(x) for x in args[3].split(","))
n = marks[-1]
rows = [()] * (n + 60) if mv == "-" else [tuple(r) for r in read_inputs(mv)[m - 1:m - 1 + n + 60]]
if edits:
    for ed in json.loads(Path(edits).read_text())["edits"]:
        rows = apply_edit(rows, tuple(ed))


def dump(e, i):
    r = e.ram_all()
    print(f"--- i={i} emu frame {e.state()['frame']}  level {r[0x30]} screen {r[0x64]}.{r[0x65]} lroutine {r[0x2C]} "
          f"player x={r[0x334]} y={r[0x31A]} state {r[0x90]} seq {r[0xBC]} aim {r[0xC2]} weapon ${r[0xAA]:02x} "
          f"lives {r[0x32]} inv {r[0xAE]} cores {r[0x86]} cleared {r[0x37]} bossdef {r[0x3B]} $2A={r[0x2A]} rng {r[0x34]} fc {r[0x1A]}")
    for s in range(16):
        if r[0x4B8 + s]:
            print(f"    enemy {s:2d}: type ${r[0x528 + s]:02x} routine {r[0x4B8 + s]} hp {r[0x578 + s]:3d} x={r[0x33E + s]:3d} "
                  f"y={r[0x324 + s]:3d} state ${r[0x598 + s]:02x} sprite ${r[0x30A + s]:02x} attr ${r[0x5A8 + s]:02x} "
                  f"delay {r[0x538 + s]} v1 {r[0x5B8 + s]} v2 {r[0x5C8 + s]}")
    for s in range(16):
        if r[0x388 + s]:
            print(f"    bullet {s:2d}: slot {r[0x388 + s]} x={r[0x3C8 + s]:3d} y={r[0x3B8 + s]:3d} routine {r[0x438 + s]} timer {r[0x418 + s]}")


with BizHawk(log_name="watch.log", fields={}) as e:
    e.load(state)
    done = 0
    for i in marks:
        if i > done:
            e.run(rows[done:i])
            done = i
        dump(e, i)
        if shots:
            e.screenshot(f"{shots}_i{i}")
