"""Build the calibration input files (played from power-on) with the ROM-level model in the loop for the menus.

    python work/make_cal_inputs.py            # writes logs/cal1.inputs.txt and logs/cal2.inputs.txt

cal1: default menus (A-Type, level 0), then ~4500 frames of seeded pseudo-random pad input, with Start presses
      late in the file (pause, and getting out of the game-over screens).
cal2: B-Type, level 19 (level 9 + A held with Start), height 5, then seeded pseudo-random input.
The files are only test patterns for comparing the model with BizHawk; they are not runs and ignore the
human-input limits (they contain 1-frame presses on purpose).
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tet.inputs import from_mask, write_inputs
from tet.nes import Machine

A, B, SEL, START, UP, DOWN, LEFT, RIGHT = 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01
LOGS = Path(__file__).resolve().parent.parent / "logs"


class Rec:
    def __init__(self):
        self.m = Machine()
        self.masks = []

    def f(self, mask=0, n=1):
        for _ in range(n):
            self.m.frame(mask)
            self.masks.append(mask)

    def until(self, cond, mask=0, limit=2000):
        k = 0
        while not cond(self.m.ram):
            self.f(mask)
            k += 1
            if k > limit:
                raise RuntimeError("condition never met")
        return k

    def tap(self, mask, hold=2, gap=12):
        self.f(mask, hold)
        self.f(0, gap)

    def save(self, name):
        p = write_inputs(LOGS / f"{name}.inputs.txt", [from_mask(b) for b in self.masks], "calibration pattern")
        print(p, len(self.masks), "frames; model ends in mode", self.m.ram[0xC0], "state", self.m.ram[0xA7],
              "playState", self.m.ram[0x68], "lines", "%02X%02X" % (self.m.ram[0x71], self.m.ram[0x70]),
              "level", self.m.ram[0x64], "gameType", self.m.ram[0xC1])


def random_play(r: Rec, rng: random.Random, frames: int, start_every: int = 0):
    combos = [0, 0, LEFT, RIGHT, DOWN, DOWN, A, B, LEFT | A, RIGHT | B, LEFT | B, RIGHT | A, DOWN | A, UP, A | B]
    t = 0
    while t < frames:
        c = rng.choice(combos)
        n = rng.choice((1, 1, 2, 2, 3, 4, 6, 9, 14, 20))
        if c == DOWN:
            n = rng.choice((3, 8, 15, 30, 45))
        if start_every and (t // start_every) != ((t + n) // start_every):
            c, n = START, 2
        r.f(c, n)
        t += n


def cal1():
    r = Rec()
    r.f(0, 300)                                   # legal screen (Start is ignored at first)
    r.until(lambda ram: ram[0xC0] == 1, START)    # title
    r.f(0, 30)
    r.tap(START)
    r.until(lambda ram: ram[0xC0] == 2)
    r.f(0, 30)
    r.tap(START)
    r.until(lambda ram: ram[0xC0] == 3)
    r.f(0, 30)
    r.tap(START)
    r.until(lambda ram: ram[0xC0] == 4 and ram[0x68] == 1)
    rng = random.Random(1989)
    random_play(r, rng, 3000)
    random_play(r, rng, 2500, start_every=180)
    r.save("cal1")


def cal2():
    r = Rec()
    r.f(0, 300)
    r.until(lambda ram: ram[0xC0] == 1, START)
    r.f(0, 25)
    r.tap(START)
    r.until(lambda ram: ram[0xC0] == 2)
    r.f(0, 25)
    r.tap(RIGHT)                                  # B-TYPE
    r.tap(DOWN)                                   # another music
    r.tap(START)
    r.until(lambda ram: ram[0xC0] == 3)
    r.f(0, 25)
    for _ in range(4):
        r.tap(RIGHT, gap=6)                       # level 4
    r.tap(DOWN, gap=6)                            # level 9
    r.tap(A, gap=6)                               # cursor to HEIGHT
    r.tap(RIGHT, gap=6)
    r.tap(RIGHT, gap=6)                           # height 2
    r.tap(DOWN, gap=6)                            # height 5
    r.f(A, 4)
    r.f(A | START, 3)                             # level 9 + A = 19
    r.f(0, 3)
    r.until(lambda ram: ram[0xC0] == 4 and ram[0x68] == 1)
    print("cal2 game: level", r.m.ram[0x64], "height", r.m.ram[0x79], "type", r.m.ram[0xC1])
    rng = random.Random(255)
    random_play(r, rng, 1500)
    random_play(r, rng, 3500, start_every=150)
    r.save("cal2")


if __name__ == "__main__":
    cal1()
    cal2()
