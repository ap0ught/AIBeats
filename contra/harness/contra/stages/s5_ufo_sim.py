"""Offline model of the stage 5 UFO fight (Bill jumping straight up under it, firing Spread + Rapid upward), used
to plan the B presses and the jumps; the emulator then replays and judges the plans (contra/stages/s5.py).

What is modelled, per frame, in the game's order (knowledge/code_player_mechanics.md section 0, checked against
RAM dumps made with tools/s5b_cal.py):
  1. fire: a new B press creates up to five pellets in the lowest free slots 0..9, at the muzzle (X, Y - 16 in a
     jump; X + 5, Y - 27 standing, facing right), with the slot's left-over sub-pixel and the velocity of pellet
     number i (centre, +1, -1, +2, -2); a pellet does not move on the frame it is created;
  2. Bill: a jump starts on a new A press on the ground (velocity -1040/256, no move on that frame), then
     velocity += 35/256 and Y += velocity each frame; he lands when a falling frame starts at Y >= 160;
  3. pellets move; one that leaves the screen frees its slot at once; one that hit frees it after 6 more frames;
  4. the UFO (from the frame it can be hit) takes ONE pellet inside its box per frame, highest slot first.
  5. the UFO's bombs (created 32, 64, 96 frames after it opens, at its X, 12 px above its centre, falling) and
     small saucers (48, 80, 112 frames after, 20 px to the left / right, same height): each has 1 HP and takes
     the first pellet inside its own box (-11..+10) AFTER the UFO has taken its one, then is gone.
Not modelled: lag frames, frames on which the game ignores the controller, the bombs hitting Bill.
"""
from __future__ import annotations

VEL_UP = ((0, -892), (171, -878), (-171, -878), (339, -826), (-339, -826))    # pellet i, aim straight up, 1/256 px
GROUND_Y = 164
BOMB_DY = (0, 0, 0, 1, 2, 3, 4, 5, 7, 8, 10, 12, 14, 16, 18, 21, 23, 26, 29, 32)   # fall of a bomb, frames 0..19
EXTRAS = ((32, 0), (48, -20), (64, 0), (80, 20), (96, 0), (112, -20))            # (frames after it opens, dx)


def extra_pos(ux, uy, dx, i):
    """Centre of a bomb (dx 0) / small saucer i frames after it was created."""
    if dx == 0:
        return ux, uy - 12 + (BOMB_DY[i] if i < 20 else int(0.089 * i * i + 0.5))
    return ux + dx + int((-1.5 if dx < 0 else 1.5) * max(0, i - 16)), uy - 12


class Sim:
    __slots__ = ("k", "y16", "v", "air", "sl", "acc", "hp", "since", "th", "x", "box", "hits", "P", "J", "pend",
                 "sinceA", "gdx", "ex", "u")

    def __init__(self, k, y16, x, acc, hp, th, ux, uy, gdx=5):
        self.gdx = gdx                        # standing muzzle X offset: +5 facing right, -5 facing left
        self.k, self.y16, self.v, self.air = k, y16, 0, False
        self.sl = [None] * 10                 # None | [routine, x16, y16, vx, vy, timer, new]
        self.acc = list(acc)                  # per slot (x sub-pixel, y sub-pixel) left by its last bullet
        self.hp, self.th, self.x = hp, th, x
        self.box = (ux - 16, ux + 17, uy - 16, uy + 17)
        self.u = (ux, uy)
        self.ex = 0                           # bit i set: extra i (EXTRAS) is gone
        self.since = 99
        self.sinceA = 99
        self.hits = 0
        self.P, self.J = (), ()
        self.pend = 0

    def copy(self):
        o = Sim.__new__(Sim)
        o.k, o.y16, o.v, o.air = self.k, self.y16, self.v, self.air
        o.sl = [None if b is None else list(b) for b in self.sl]
        o.acc = list(self.acc)
        o.hp, o.th, o.x, o.box, o.gdx, o.ex, o.u = self.hp, self.th, self.x, self.box, self.gdx, self.ex, self.u
        o.since, o.sinceA, o.hits, o.P, o.J, o.pend = self.since, self.sinceA, self.hits, self.P, self.J, self.pend
        return o

    def can_press(self):
        return self.since >= 5

    def step(self, press_b: bool, press_a: bool):
        """Advance one frame; press_b / press_a = a NEW press starts on this frame."""
        self.k += 1
        k = self.k
        self.since += 1
        self.sinceA += 1
        sl = self.sl
        y = self.y16 >> 8
        if press_b:
            self.since = 0
            self.P = self.P + (k,)
            mx, my = (self.x, y - 16) if self.air else (self.x + self.gdx, y - 27)
            i = 0
            for s in range(10):
                if sl[s] is None:
                    ax, ay = self.acc[s]
                    vx, vy = VEL_UP[i]
                    sl[s] = [1, mx * 256 + ax, my * 256 + ay, vx, vy, 0, 1]
                    i += 1
                    if i == 5:
                        break
        # Bill
        if self.air:
            f = self.v >> 8
            if self.v > 0 and f >= 1 and (f >= 4 or (y & 15) < 8) and y >= GROUND_Y - 4:
                self.air = False
                self.y16 = GROUND_Y * 256 + (self.y16 & 255)
                self.v = 0
            else:
                self.v += 35
                self.y16 += self.v
        elif press_a:
            self.air = True
            self.v = -1040
            self.sinceA = 0
            self.J = self.J + (k,)
        # pellets
        for s in range(10):
            b = sl[s]
            if b is None:
                continue
            if b[0] == 1:
                if b[6]:
                    b[6] = 0
                else:
                    b[1] += b[3]
                    b[2] += b[4]
                    px, py = b[1] >> 8, b[2] >> 8
                    if px < 5 or px >= 251 or py < 5 or py >= 232:
                        self.acc[s] = (b[1] & 255, b[2] & 255)
                        sl[s] = None
            else:
                b[5] -= 1
                if b[5] <= 0:
                    self.acc[s] = (b[1] & 255, b[2] & 255)
                    sl[s] = None
        # the UFO
        hit = False
        if k >= self.th and self.hp > 0:
            x0, x1, y0, y1 = self.box
            for s in range(9, -1, -1):
                b = sl[s]
                if b is not None and b[0] == 1 and x0 <= (b[1] >> 8) <= x1 and y0 <= (b[2] >> 8) <= y1:
                    b[0], b[5] = 2, 6
                    self.hp -= 1
                    self.hits += 1
                    hit = True
                    break
        d = k - self.th
        if d >= 32:
            for i, (t0, dx) in enumerate(EXTRAS):
                if d < t0:
                    break
                if self.ex & (1 << i):
                    continue
                cx, cy = extra_pos(self.u[0], self.u[1], dx, d - t0)
                if cy > 200 or cx < 8 or cx > 248:
                    self.ex |= 1 << i
                    continue
                for s in range(9, -1, -1):
                    b = sl[s]
                    if b is not None and b[0] == 1 and cx - 11 <= (b[1] >> 8) <= cx + 10 and cy - 11 <= (b[2] >> 8) <= cy + 10:
                        b[0], b[5] = 2, 6
                        self.ex |= 1 << i
                        break
        return hit

    def pending(self, horizon=60):
        """Hits the pellets now in flight will still score if nothing else is fired, and the frame of the last."""
        x0, x1, y0, y1 = self.box
        bl = [[s, b[1], b[2], b[3], b[4], b[6]] for s, b in enumerate(self.sl) if b is not None and b[0] == 1]
        n, last = 0, 0
        k = self.k
        for t in range(1, horizon):
            if not bl:
                break
            keep = []
            for b in bl:
                if b[5]:
                    b[5] = 0
                else:
                    b[1] += b[3]
                    b[2] += b[4]
                px, py = b[1] >> 8, b[2] >> 8
                if not (px < 5 or px >= 251 or py < 5 or py >= 232):
                    keep.append(b)
            bl = keep
            if k + t >= self.th:
                for b in reversed(bl):
                    if x0 <= (b[1] >> 8) <= x1 and y0 <= (b[2] >> 8) <= y1:
                        bl.remove(b)
                        n += 1
                        last = t
                        break
        return n, last

    def key(self):
        return (self.hp, self.y16, self.v, self.since, self.ex,
                tuple(None if b is None else (b[0], b[1] >> 8, b[2] >> 8, b[5]) for b in self.sl))


def plan(k0, y16, x, acc, th, ux, uy, k_a, width=600, hp=32, max_k=None, rejump_gap=0, gdx=5):
    """Beam search over the B presses from frame k0 (state: standing, no bullets). A is pressed on frame k_a and
    again `rejump_gap` frames after every landing. Returns (kill frame, press frames, jump frames) or None."""
    root = Sim(k0, y16, x, acc, hp, th, ux, uy, gdx)
    nodes = [root]
    max_k = max_k or th + 110
    land_k = {}
    while nodes:
        k = nodes[0].k + 1
        if k > max_k:
            return None
        nxt = {}
        done = []
        for nd in nodes:
            press_a = (not nd.air) and k >= k_a and nd.sinceA >= 5 and (not nd.J or k >= nd.J[-1] + 59 + rejump_gap)
            opts = (False, True) if nd.can_press() else (False,)
            for pb in opts:
                c = nd.copy() if (pb or len(opts) > 1) else nd
                if pb and press_a:
                    continue                      # keep B off the A frame (standing muzzle, one frame only)
                hit = c.step(pb, press_a)
                if pb:
                    c.pend = c.pending()[0]
                elif hit:
                    c.pend = max(0, c.pend - 1)
                if c.hp <= 0:
                    done.append(c)
                    continue
                key = c.key()
                o = nxt.get(key)
                if o is None:
                    nxt[key] = c
        if done:
            best = done[0]
            return best.k, list(best.P), list(best.J)
        cand = list(nxt.values())
        # fewer HP left after what is already flying; then more free slots; then an earlier chance to press
        cand.sort(key=lambda c: (c.hp - c.pend, sum(1 for b in c.sl if b is not None), -c.since))
        nodes = cand[:width]
    return None


def plan_job(a):
    """For a process pool: a = (k0, y16, x, acc, th, ux, uy, k_a, width, gdx)."""
    k0, y16, x, acc, th, ux, uy, k_a, width, gdx = a
    return plan(k0, y16, x, acc, th, ux, uy, k_a, width=width, gdx=gdx)


def replay(k0, y16, x, acc, th, ux, uy, P, J, n, hp=32):
    """Play a schedule in the model; returns [(k, Bill Y, UFO HP)] for comparison with the emulator."""
    s = Sim(k0, y16, x, acc, hp, th, ux, uy)
    P, J = set(P), set(J)
    out = []
    while s.k < n:
        s.step((s.k + 1) in P, (s.k + 1) in J)
        out.append((s.k, s.y16 >> 8, s.hp))
    return out


if __name__ == "__main__":
    # worker for contra/stages/s5.py: python -m contra.stages.s5_ufo_sim <jobs.json> -> one JSON line of results
    # (a separate interpreter per worker: no multiprocessing, so it works whatever the caller's main module is)
    import json
    import sys
    from pathlib import Path
    jobs_ = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out_ = []
    for j_ in jobs_:
        j_[3] = [tuple(a_) for a_ in j_[3]]
        out_.append(plan_job(tuple(j_)))
    print(json.dumps(out_))
