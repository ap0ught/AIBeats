"""Check the piece-level model (tet/fast.py) against the ROM-level model (tet/nes.py), piece by piece.

    python work/check_fast.py [games=20] [pieces=120] [seed=1]
Each game: power-on, menus, A-Type level 19, a random wait before Start, then random reachable placements
(random soft/natural timing). After every piece the predicted spawn frame, field, pieces, lines and random
number are compared with the ROM-level model's RAM. Also writes logs/fastchk.inputs.txt (last game) for BizHawk.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tet import fast
from tet.inputs import from_mask, write_inputs
from tet.nes import Machine

A, B, SEL, START, UP, DOWN, LEFT, RIGHT = 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01
LOGS = Path(__file__).resolve().parent.parent / "logs"


class Game:
    """ROM-level model with an input log."""

    def __init__(self):
        self.m = Machine()
        self.masks = []

    def f(self, mask=0, n=1):
        for _ in range(n):
            self.m.frame(mask)
            self.masks.append(mask)

    def until(self, cond, mask=0, limit=3000):
        k = 0
        while not cond(self.m.ram):
            self.f(mask)
            k += 1
            if k > limit:
                raise RuntimeError("condition never met")

    def to_level_menu(self):
        self.f(0, 270)
        self.until(lambda r: r[0xC0] == 1, START)
        self.f(0, 4)
        self.f(START, 2)
        self.until(lambda r: r[0xC0] == 2)
        self.f(0, 4)
        self.f(START, 2)
        self.until(lambda r: r[0xC0] == 3)
        self.f(0, 4)
        for _ in range(4):
            self.f(RIGHT, 1)
            self.f(0, 1)
        self.f(DOWN, 1)
        self.f(0, 1)
        assert self.m.ram[0x67] == 9, self.m.ram[0x67]

    def start_game(self, wait):
        """Wait, then A+Start (level 19). Returns the frame on which Start was first held."""
        self.f(0, wait)
        self.f(A, 1)
        t = len(self.masks) + 1
        self.f(A | START, 2)
        self.until(lambda r: r[0xC0] == 4 and r[0x68] == 1)
        return t

    def field(self):
        ram = self.m.ram
        v = 0
        for i in range(200):
            if ram[0x400 + i] != 0xEF:
                v |= 1 << i
        return v

    def state(self):
        """fast.State from RAM; call on a spawn frame."""
        ram = self.m.ram
        f = len(self.masks)
        rng = (ram[0x17] << 8) | ram[0x18]
        fc = ram[0xB1] | (ram[0xB2] << 8)
        lines = (ram[0x71] & 15) * 100 + (ram[0x70] >> 4) * 10 + (ram[0x70] & 15)
        return fast.State(self.field(), ram[0x62], ram[0xBF], f, fast.RNG_INDEX[rng], ram[0x1A], ram[0x19], lines,
                          (fc - f) & 0xFFFF)

    def play(self, s, path, soft, k_soft, lock_frame):
        """Feed the inputs of one piece (spawned on frame s.frame) and run to the frame before the next spawn."""
        S = s.frame
        assert len(self.masks) == S
        taps = {}
        for row, dx, rot in path:
            b = (LEFT if dx < 0 else RIGHT if dx > 0 else 0) | (A if rot == 'A' else B if rot == 'B' else 0)
            taps[S + 2 * row + 1] = b
        f = S + 1
        while self.m.ram[0x68] == 1 or f <= lock_frame:
            b = taps.get(f, 0)
            if soft and f >= S + 2 * k_soft + 1 and f <= lock_frame:
                b |= DOWN
            self.f(b)
            f += 1
            if f > S + 400:
                raise RuntimeError("piece never locked")
        # entry delay: nothing held
        while not (self.m.ram[0x68] == 1) and self.m.ram[0x68] != 10:
            self.f(0)
            if len(self.masks) > S + 400:
                raise RuntimeError("no spawn")


def one_game(rng, pieces, verbose=False):
    g = Game()
    g.to_level_menu()
    g.start_game(rng.randrange(0, 200))
    assert g.m.ram[0x64] == 19
    # first piece: start gravity with a Down tap, let it fall, wait for the second spawn
    g.f(DOWN, 1)
    g.until(lambda r: r[0x68] != 1)
    g.until(lambda r: r[0x68] == 1)
    s = g.state()
    bad = 0
    n = 0
    for n in range(pieces):
        opts = fast.reach(s.field, s.cur)
        if not opts:
            break
        # prefer low placements so games last, with a random pick now and then
        keys = list(opts)
        if rng.random() < 0.85:
            # crude stacker so that rows get completed: most rows cleared, then fewest covered holes, then lowest
            def score(k):
                fld, nl = fast.lock(s.field, k[1], k[0], k[2])
                holes = 0
                for c in range(10):
                    seen = False
                    for r in range(20):
                        bit = (fld >> (r * 10 + c)) & 1
                        if bit:
                            seen = True
                        elif seen:
                            holes += 1
                return (nl, -holes, k[2])
            best = max(score(k) for k in keys)
            keys = [k for k in keys if score(k) == best]
        x, o, y = rng.choice(keys)
        path = opts[(x, o, y)]
        ok, k_soft = fast.can_soft(path, y)
        soft = ok and rng.random() < 0.5
        t, info = fast.place(s, x, o, y, soft)
        g.play(s, path, soft, k_soft, info[0])
        if t is None:
            # the game still "spawns" a blocked piece and only ends at its lock: the next state must be game over
            g.until(lambda r: r[0x68] not in (1, 2), 0, 200)
            if g.m.ram[0x68] != 10:
                bad += 1
                print("  top-out mismatch: rom playState", g.m.ram[0x68])
            break
        r = g.state()
        if r.key() != t.key() or r.lines != t.lines:
            bad += 1
            print(f"  piece {n}: MISMATCH placing {fast.NAMES[fast.TYPE_OF[s.cur]]} at x={x} o={o} y={y} soft={soft} "
                  f"path={path}")
            print(f"    fast: frame {t.frame} cur {t.cur} nxt {t.nxt} ridx {t.ridx} sc {t.spawn_count} id {t.spawn_id} "
                  f"lines {t.lines} field_ok {t.field == r.field}")
            print(f"    rom : frame {r.frame} cur {r.cur} nxt {r.nxt} ridx {r.ridx} sc {r.spawn_count} id {r.spawn_id} "
                  f"lines {r.lines}")
            if bad >= 3:
                break
            s = r
            continue
        s = t
    return bad, n + 1, s.lines, g


def main():
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    pieces = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    tot_bad = tot_p = tot_l = 0
    g = None
    for i in range(games):
        bad, n, lines, g = one_game(rng, pieces)
        tot_bad += bad
        tot_p += n
        tot_l += lines
    print(f"{games} games, {tot_p} pieces, {tot_l} lines cleared, {tot_bad} mismatches")
    if g is not None:
        write_inputs(LOGS / "fastchk.inputs.txt", [from_mask(b) for b in g.masks], "check_fast last game")
    sys.exit(1 if tot_bad else 0)


if __name__ == "__main__":
    main()
