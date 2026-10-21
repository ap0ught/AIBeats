"""Exact model of Bill's movement on the Waterfall (stage 3), from the disassembly (bank7.asm handle_jump,
set_vertical_level_frame_scroll, calc_player_x_vel, set_player_landing_y_offset, check_player_ledge) and checked
frame by frame against the emulator (tools/s3_verify_model.py).

Coordinates: X, Y = screen position of the player point ($0334, $031A). A = pixels climbed = screen*240 + offset
($64, $65). sub = $94 (Y sub-pixel, never cleared). v = 16-bit Y velocity ($C6:$C4).
World row of the collision cell under a point (x, y):  q = (y - A) // 16   (rows grow downward, 16 px each);
knowledge/s3_map.json holds the rows ('=' floor). Standing on row q:  Y = A + 16*q - 12.

The ledge-skip mechanism (verified):
  * while rising with Y < $50 the frame's rise is turned into scroll: sub += frac(v); scroll = -(hi(v) + carry)
  * if Bill moves right on that frame (X < $E6) the routine runs a second time: sub += frac(v) again and the
    scroll is recomputed with the SECOND carry only. So right = "double add", anything else = "single add".
  * on the frame Y crosses below $50 while moving right, Y has already moved AND the second call scrolls:
    a whole extra frame of rise.
"""
from __future__ import annotations

import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
V0 = 0xFBF0          # jump velocity
G = 0x23             # gravity per frame
XMAX = 0xE6          # no move right when X >= this
XMIN = 0x1A          # no move left when X < this
TRIG = 7 * 240 + 0xC0   # boss auto-scroll starts when a scroll frame finds A >= this


class Map:
    def __init__(self, path=None):
        j = json.loads(Path(path or PROJECT / "knowledge" / "s3_map.json").read_text())
        self.rows = {}
        for q, s in j["rows"].items():
            m = 0
            for c, ch in enumerate(s):
                if ch != ".":
                    m |= 1 << c
            self.rows[int(q)] = m
        self.qmin = min(self.rows)
        self.qmax = max(self.rows)

    def floor(self, q: int, x: int) -> bool:
        return bool((self.rows.get(q, 0) >> (x >> 4)) & 1)

    def segs(self, q: int):
        """[(x0, x1)] inclusive pixel ranges of floor on row q."""
        m = self.rows.get(q, 0)
        out = []
        c = 0
        while c < 16:
            if (m >> c) & 1:
                c0 = c
                while c < 16 and (m >> c) & 1:
                    c += 1
                out.append((c0 * 16, c * 16 - 1))
            else:
                c += 1
        return out


class St:
    """Player state for the model."""
    __slots__ = ("X", "Y", "sub", "v", "A", "air", "auto")

    def __init__(self, X, Y, sub, A, v=0, air=False, auto=0):
        self.X, self.Y, self.sub, self.A, self.v, self.air, self.auto = X, Y, sub, A, v, air, auto

    def copy(self):
        return St(self.X, self.Y, self.sub, self.A, self.v, self.air, self.auto)

    def key(self):
        return (self.X, self.Y, self.sub, self.A, self.v, self.air)

    def row(self):
        return (self.Y + 16 - self.A) // 16

    def __repr__(self):
        return f"St(X={self.X},Y={self.Y},sub={self.sub:02x},A={self.A},v={self.v:04x},air={self.air},q={self.row()})"


def jump_start(s: St) -> None:
    """The frame A is read on the ground: velocity set, nothing moves (X velocity is 0 on this frame)."""
    s.v = V0
    s.air = True


def air_frame(s: St, d: int, mp: Map) -> bool:
    """One airborne frame. d = effective X direction this frame (-1, 0, +1): the d-pad if L/R is held, else the
    direction latched earlier in this jump. Returns True if Bill landed on this frame."""
    fast = s.v >> 8
    if fast < 0x80:                       # descending (or apex): maybe land
        check = False
        if fast >= 1:
            check = fast >= 4 or ((s.Y - s.A) & 15) < 8
        if check and s.Y + 16 < 0xE0 and mp.floor((s.Y + 16 - s.A) // 16, s.X):
            s.Y = s.Y - ((s.Y - s.A) & 15) + 4
            s.v = 0
            s.air = False
            if d > 0:
                if s.X < XMAX:
                    s.X += 1
            elif d < 0:
                if s.X >= XMIN:
                    s.X -= 1
            if s.auto:
                s.auto -= 1
                s.A += 1
                s.Y += 1
            return True
    s.v = (s.v + G) & 0xFFFF
    fast = s.v >> 8
    fr = s.v & 0xFF
    neg = fast >= 0x80
    scroll = 0
    done = False
    if s.Y < 0x50 and neg and not s.auto:
        if s.A >= TRIG:
            s.auto = 0x40                 # boss reveal starts: no scroll from this call, Y moves instead
        else:
            t = s.sub + fr
            s.sub = t & 0xFF
            scroll = 256 - fast - (t >> 8)
            done = True
    if not done:
        t = s.sub + fr
        s.sub = t & 0xFF
        s.Y = (s.Y + fast + (t >> 8)) & 0xFF
    if d > 0:
        if s.X < XMAX:
            if s.Y < 0x50 and neg and not s.auto:
                if s.A >= TRIG:
                    s.auto = 0x40
                else:
                    t = s.sub + fr
                    s.sub = t & 0xFF
                    scroll = 256 - fast - (t >> 8)
            s.X += 1
    elif d < 0:
        if s.X >= XMIN:
            s.X -= 1
    if s.auto:
        # handle_vertical_scroll: 1 px per frame, and the player is moved down 1 px (auto_scroll_player)
        s.auto -= 1
        s.A += 1
        s.Y += 1
    else:
        s.A += scroll
    return False


def sim_jump(s: St, dirs, mp: Map, maxf: int = 120):
    """A-press frame + airborne frames with the given directions (the last one repeats). Returns (frames used
    including the A-press frame and the landing frame, landed?)."""
    jump_start(s)
    n = 1
    k = 0
    while n < maxf:
        d = dirs[k] if k < len(dirs) else (dirs[-1] if dirs else 0)
        k += 1
        n += 1
        if air_frame(s, d, mp):
            return n, True
        if s.Y >= 0xE8:
            return n, False
    return n, False
