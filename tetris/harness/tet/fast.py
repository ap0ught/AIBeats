"""Piece-level model of A-Type play (tier 2), for the planner. Rules and tables come from the ROM (see the
addresses) and every prediction is checked against the ROM-level model (tet/nes.py) by work/check_fast.py.

Scope: constant level 19 (one row of gravity every 2 frames), presses limited to one per button every 2 frames.
Frames are BizHawk frames. S = the frame on which a piece spawns (after it, playState is 1 and the piece sits at
x=5, y=0); the first frame its inputs act on is S+1.

Rows: row 0 is the top visible row, 19 the bottom. A field is a Python int with bit (row*10 + col).

What the game does with a piece on level 19 (routines $89AE shift, $88AB rotate, $8914 drop, in that order
every frame):
  * the piece is on row r during frames S+2r+1 and S+2r+2; gravity moves it down at the end of S+2r+2;
  * a new press of Left/Right shifts it one column, a new press of A/B rotates it, if the new position is free;
  * when gravity cannot move it down, it locks on that frame: L = S + 2*y + 2;
  * holding Down (pressed on an odd frame S+2k+1, nothing else on the pad) adds one drop on S+2k+3 and from
    then on drops come on odd frames, so the lock comes one frame sooner: L = S + 2*y + 1. No shift is
    possible while Down is held.
After the lock ($99A2, $9A6B, $9B58, $988E and the row copying in $94EE/$9725):
  * next spawn S' = L + 2*k + 8, k = ceil((20 - max(Y-2, 0)) / 4)  (Y = the piece's own row when it locked):
    10 frames for the two bottom rows up to 18 frames for rows 0-5;
  * if rows were completed: S' = L + 2*k + 25 + d, where d (0-3) is the wait for the game's frame counter to
    reach a multiple of 4; the LINES counter on screen changes on frame S' - 4.
The next piece is drawn on frame S' ($9907) from the random number of that frame, the spawn count and the
previous piece; the random number advances once per frame and once more for a re-roll.
"""
from __future__ import annotations

from .rom import prg

P = prg()


def _s8(b):
    return b - 256 if b > 127 else b


# orientation table $8A9C: 19 orientations x 4 cells x (dy, tile, dx)
ORIENT = []
TILE = []
for _o in range(19):
    cells = []
    for _c in range(4):
        a = 0x8A9C - 0x8000 + _o * 12 + _c * 3
        cells.append((_s8(P[a + 2]), _s8(P[a])))            # (dx, dy)
    ORIENT.append(tuple(cells))
    TILE.append(P[0x8A9C - 0x8000 + _o * 12 + 1])
# rotation table $88EE: for orientation o, [2o] = after B, [2o+1] = after A
ROT_B = [P[0x88EE - 0x8000 + 2 * o] for o in range(19)]
ROT_A = [P[0x88EE - 0x8000 + 2 * o + 1] for o in range(19)]
TYPE_OF = [P[0x993B - 0x8000 + o] for o in range(19)]         # orientation -> piece type 0..6 (T J Z O S L I)
SPAWN_TABLE = [P[0x994E - 0x8000 + i] for i in range(7)]       # type index -> spawn orientation
SPAWN_OF = [P[0x9956 - 0x8000 + o] for o in range(19)]         # orientation -> its type's spawn orientation
NAMES = "TJZOSLI"
DROP_FRAMES = [P[0x898E - 0x8000 + i] for i in range(29)] + [1] * 227

W, H = 10, 20
FULL_ROW = (1 << W) - 1

# MASK[o][x][y + 2]: bits of the visible cells of orientation o at (x, y), or None when the game's own validity
# test ($948B) fails on the borders: every cell needs 0 <= col <= 9 and -2 <= row <= 19.
MASK = []
for _o in range(19):
    per_x = []
    for _x in range(-2, 12):
        per_y = []
        for _y in range(-2, 22):
            m = 0
            ok = True
            for dx, dy in ORIENT[_o]:
                cx, cy = _x + dx, _y + dy
                if cx < 0 or cx > 9 or cy < -2 or cy > 19:
                    ok = False
                    break
                if cy >= 0:
                    m |= 1 << (cy * 10 + cx)
            per_y.append(m if ok else None)
        per_x.append(per_y)
    MASK.append(per_x)


def mask(o, x, y):
    return MASK[o][x + 2][y + 2]


def fits(field, o, x, y):
    m = MASK[o][x + 2][y + 2]
    return m is not None and not (field & m)


# ---------------------------------------------------------------------------------------------- random numbers
def _lfsr_seq():
    seq = []
    v = 0x8988
    seen = {}
    while v not in seen:
        seen[v] = len(seq)
        seq.append(v)
        bit = ((v >> 9) ^ (v >> 1)) & 1
        v = (bit << 15) | (v >> 1)
    return seq, seen, seen[v]


RNG_SEQ, RNG_INDEX, _loop_start = _lfsr_seq()
RNG_PERIOD = len(RNG_SEQ) - _loop_start
RNG_HI = [v >> 8 for v in RNG_SEQ]


def rng_next_index(i):
    i += 1
    return i if i < len(RNG_SEQ) else _loop_start


def rng_advance(i, n):
    """Index after n more steps."""
    if i + n < len(RNG_SEQ):
        return i + n
    return _loop_start + (i + n - _loop_start) % RNG_PERIOD


def pick_piece(ridx, spawn_count, spawn_id):
    """$9907: returns (spawn orientation of the new piece, ridx after a possible re-roll, new spawn count)."""
    spawn_count = (spawn_count + 1) & 0xFF
    i = (RNG_HI[ridx] + spawn_count) & 7
    if i != 7:
        o = SPAWN_TABLE[i]
        if o != spawn_id:
            return o, ridx, spawn_count
    ridx = rng_next_index(ridx)
    i = ((RNG_HI[ridx] & 7) + spawn_id) % 7
    return SPAWN_TABLE[i], ridx, spawn_count


# ---------------------------------------------------------------------------------------------- timing
def entry_frames(y_lock):
    """Frames from the lock frame to the next spawn when no row is completed."""
    v0 = y_lock - 2 if y_lock > 2 else 0
    return 2 * ((20 - v0 + 3) // 4) + 8


ENTRY = [entry_frames(y) for y in range(20)]


# ---------------------------------------------------------------------------------------------- placements
def reach(field, o0, x0=5, y0=0):
    """Every way the piece can lock, with presses on odd frames only (shift, then rotate, on the first frame
    of a row). Returns {(x, o, y): path}; path = tuple of (row, dx, rot) with dx in (-1, 0, 1) and rot in
    ('', 'A', 'B'); rows are ascending. Of several paths to the same resting place the one whose last press
    comes earliest is kept (it leaves the most room for the Down trick)."""
    if not fits(field, o0, x0, y0):
        return {}
    arrive = {(x0, o0): ()}
    out = {}
    y = y0
    while arrive:
        nxt = {}
        for (x, o), path in arrive.items():
            # positions on this row after at most one shift and one rotation (shift first)
            cand = [(x, o, path)]
            for dx in (-1, 1):
                if fits(field, o, x + dx, y):
                    cand.append((x + dx, o, path + ((y, dx, ''),)))
            for k in range(len(cand)):
                cx, co, cp = cand[k]
                ra, rb = ROT_A[co], ROT_B[co]
                if ra != co and fits(field, ra, cx, y):
                    if cp and cp[-1][0] == y:
                        cand.append((cx, ra, cp[:-1] + ((y, cp[-1][1], 'A'),)))
                    else:
                        cand.append((cx, ra, cp + ((y, 0, 'A'),)))
                if rb != co and rb != ra and fits(field, rb, cx, y):
                    if cp and cp[-1][0] == y:
                        cand.append((cx, rb, cp[:-1] + ((y, cp[-1][1], 'B'),)))
                    else:
                        cand.append((cx, rb, cp + ((y, 0, 'B'),)))
            for cx, co, cp in cand:
                if fits(field, co, cx, y + 1):
                    key = (cx, co)
                    old = nxt.get(key)
                    if old is None or _last_row(cp) < _last_row(old):
                        nxt[key] = cp
                else:
                    key = (cx, co, y)
                    old = out.get(key)
                    if old is None or _last_row(cp) < _last_row(old):
                        out[key] = cp
        arrive = nxt
        y += 1
    return out


def _last_row(path):
    return path[-1][0] if path else -1


def can_soft(path, y):
    """Is the one-frame-sooner lock available? Down goes down on the first frame of row k = (last press row) + 1
    at the earliest, and must still buy a drop: k <= y - 1. A rotation may share that frame, a shift may not."""
    k = 0
    for row, dx, rot in path:
        if dx:
            k = max(k, row + 1)
        else:
            k = max(k, row)
    return k <= y - 1, k


def lock(field, o, x, y):
    """Field after the piece locks at (x, y) and completed rows are removed. Returns (field, rows cleared)."""
    field |= MASK[o][x + 2][y + 2]
    top = y - 2 if y > 2 else 0
    n = 0
    for r in range(top, min(top + 4, 20)):
        if (field >> (r * 10)) & FULL_ROW == FULL_ROW:
            below = field >> ((r + 1) * 10) << ((r + 1) * 10)
            above = field & ((1 << (r * 10)) - 1)
            field = below | (above << 10)
            n += 1
    return field, n


class State:
    """What the planner needs at a spawn: the piece now at (5, 0), the one in the preview, and the clock."""
    __slots__ = ("field", "cur", "nxt", "frame", "ridx", "spawn_count", "spawn_id", "lines", "fc0")

    def __init__(self, field, cur, nxt, frame, ridx, spawn_count, spawn_id, lines, fc0):
        self.field = field          # bitboard without the active piece
        self.cur = cur              # spawn orientation of the active piece
        self.nxt = nxt              # spawn orientation of the preview piece
        self.frame = frame          # S: the spawn frame of cur
        self.ridx = ridx            # index in RNG_SEQ of the random number the game holds after frame S
        self.spawn_count = spawn_count
        self.spawn_id = spawn_id
        self.lines = lines
        self.fc0 = fc0              # (frame counter after frame f) = (fc0 + f) & 0xFFFF

    def copy(self):
        return State(self.field, self.cur, self.nxt, self.frame, self.ridx, self.spawn_count, self.spawn_id,
                     self.lines, self.fc0)

    def key(self):
        return (self.field, self.cur, self.nxt, self.frame, self.ridx, self.spawn_count, self.spawn_id)


def place(s: State, x, o, y, soft=False):
    """The state at the next spawn after locking the active piece at (x, o, y). Returns (state, info) or
    (None, info) when the next piece cannot spawn (top-out). info: lock frame, rows cleared, frame the LINES
    counter changes on (or None)."""
    L = s.frame + 2 * y + (1 if soft else 2)
    field, n = lock(s.field, o, x, y)
    v0 = y - 2 if y > 2 else 0
    k = (20 - v0 + 3) // 4
    shown = None
    if n:
        c = L + 2 * k + 3
        d = (-(s.fc0 + c)) & 3
        S2 = L + 2 * k + 25 + d
        shown = S2 - 4
    else:
        S2 = L + 2 * k + 8
    ridx = rng_advance(s.ridx, S2 - s.frame)
    nn, ridx, sc = pick_piece(ridx, s.spawn_count, s.spawn_id)
    t = State(field, s.nxt, nn, S2, ridx, sc, nn, s.lines + n, s.fc0)
    info = (L, n, shown)
    if not fits(field, s.nxt, 5, 0):
        return None, info
    return t, info


def show(field, piece=None):
    """Text picture of a field (and optionally a piece (o, x, y) drawn with o)."""
    pm = mask(*piece) if piece else 0
    rows = []
    for r in range(20):
        rows.append("".join("o" if (pm >> (r * 10 + c)) & 1 else ("#" if (field >> (r * 10 + c)) & 1 else ".")
                            for c in range(10)))
    return "\n".join(rows)
