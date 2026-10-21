"""DEBUG: which starting weapon does a movie's stage segment expect? Plays the segment from a stage state with
the weapon byte ($AA) poked to each value and reports how far each gets.

    python tools/weapon_scan.py <state> <movie.inputs.txt> <m> [frames]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.inputs import read_inputs  # noqa: E402
from contra.resync import Pool, play  # noqa: E402

state, movie, m = sys.argv[1], read_inputs(sys.argv[2]), int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 3500
weapons = [0x00, 0x10, 0x01, 0x11, 0x02, 0x12, 0x03, 0x13, 0x04, 0x14]


def job(emu, w):
    emu.load(state)
    emu.poke(0xAA, w)
    return play(emu, None, movie[m - 1:m - 1 + n], stall=1500)


with Pool(4, name="wscan") as pool:
    res = pool.map(job, weapons)
for w, r in zip(weapons, res):
    print(f"weapon ${w:02x}: {r}")
