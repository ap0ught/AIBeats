"""Beam-search planner for 100 Lines (A-Type, level 19, 30 presses/s), first version.

    python work/plan100.py [--width 300] [--wait 0] [--lines 100] [--out logs/plan_x]
Start state: ROM-level model from power-on to the second spawn (first piece dropped straight, for now).
Search: plies = pieces; children = every reachable resting place x {natural, one-frame-sooner} timing;
ranking f = frames since Start + estimate of the frames still needed (see estimate()).
Writes the input file from power-on and verifies it in the ROM-level model.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tet import fast
from tet.inputs import from_mask, write_inputs
from work.check_fast import Game, A, B, DOWN, LEFT, RIGHT

LOGS = Path(__file__).resolve().parent.parent / "logs"
COL = [sum(1 << (r * 10 + c) for r in range(20)) for c in range(10)]
T_ROW = [2 * y + 2 + fast.ENTRY[y] for y in range(20)] + [2 * 19 + 2 + fast.ENTRY[19]]
ALL = (1 << 200) - 1
MIN_TOP = 4         # the stack should stay under this row
REACH_ROW = [5, 4, 3, 2, 1, 0, 1, 2, 3, 4]   # highest row on which a column can still be supplied, roughly
W_REACH = 200.0     # frames per cell a lagging column still needs above the row it can be reached on
W_BUMP = 12.0       # frames per unit of surface roughness outside the well
W_WELL = 90.0       # frames per cell of depth of a second well
TETRIS_ONLY = False # refuse every clear of fewer than 4 rows
W_EVENT = 0.0       # extra ranking cost of a clear of fewer than 4 rows (full for a single)
W_BAND = 150.0     # frames per row the live stack is taller than 5
BAND_FREE = 5       # rows of live stack that cost nothing
MIN_FLOOR = 9       # the written-off part may not come higher than this row


def estimate(field, lines_left):
    """Frames still needed: pieces still to place x the spawn-to-spawn time at the present surface, plus the
    line-clear waits. Rows at or under the highest covered hole are written off (their cells do not count)."""
    dead = 20
    tops = []
    for c in range(10):
        b = field & COL[c]
        if b:
            top = ((b & -b).bit_length() - 1) // 10
            holes = ~b & COL[c] & ~((1 << (top * 10)) - 1)
            if holes:
                hr = ((holes & -holes).bit_length() - 1) // 10
                if hr < dead:
                    dead = hr
        else:
            top = 20
        tops.append(top)
    hh = [t if t < dead else dead for t in tops]        # surface, with the written-off rows as the floor
    high = min(hh)
    well = max(range(10), key=lambda c: (hh[c], -abs(c - 5)))
    tsum = 0
    bump = 0
    prev = None
    for c in range(10):
        if c == well:
            continue
        tsum += T_ROW[hh[c] - 1 if hh[c] > 0 else 0]
        if prev is not None:
            bump += abs(hh[c] - prev)
        prev = hh[c]
    live = (field & ((1 << (dead * 10)) - 1)).bit_count()
    need = (10 * lines_left - live) / 4.0
    if need < 0:
        need = 0
    est = need * (tsum / 9.0) + ((lines_left + 3) // 4) * 18.5 + W_BUMP * bump
    if high < MIN_TOP:
        est += (MIN_TOP - high) * 500
    for c in range(10):
        # a column cannot be filled above the row a piece can reach it on (one column per row from x=5)
        lim = REACH_ROW[c]
        if c != well and hh[c] > high and high < lim:
            est += W_REACH * ((hh[c] if hh[c] < lim else lim) - high)
    for c in range(10):
        # a second well (a column 2+ under both neighbours) needs a long bar of its own
        if c == well:
            continue
        left = hh[c - 1] if c > 0 else 0
        right = hh[c + 1] if c < 9 else 0
        depth = hh[c] - (left if left > right else right)
        if depth >= 2:
            est += W_WELL * (depth - 1)
    band = dead - high
    if band > BAND_FREE:
        est += (band - BAND_FREE) * W_BAND
    if dead < MIN_FLOOR:
        est += (MIN_FLOOR - dead) * 600
    return est, high


def search(s0, t0, width, goal):
    beam = [(0.0, s0, None, None, 20, 0.0)]
    best = None
    ply = 0
    t_start = time.time()
    while beam:
        ply += 1
        kids = {}
        for node in beam:
            s = node[1]
            opts = fast.reach(s.field, s.cur)
            for (x, o, y), path in opts.items():
                ok, k_soft = fast.can_soft(path, y)
                for soft in ((False, True) if ok else (False,)):
                    t, info = fast.place(s, x, o, y, soft)
                    if t is None or (TETRIS_ONLY and info[1] and info[1] != 4):
                        continue
                    mv = (x, o, y, soft, k_soft, path, info[0])
                    if t.lines >= goal:
                        total = info[2] - t0
                        if best is None or total < best[0]:
                            best = (total, (0, t, node, mv))
                        continue
                    e, hi = estimate(t.field, goal - t.lines)
                    pen = node[5] + (W_EVENT * (4 - info[1]) / 3.0 if info[1] else 0.0)
                    f = (t.frame - t0) + e + pen
                    key = (t.field, t.cur, t.nxt, t.ridx, t.spawn_count)
                    old = kids.get(key)
                    if old is None or f < old[0]:
                        kids[key] = (f, t, node, mv, hi, pen)
        if best is not None:
            # keep only nodes that can still beat the best finished run
            kids = {k: v for k, v in kids.items() if v[1].frame - t0 + 20 < best[0]}
        prev = beam
        ranked = sorted(kids.values(), key=lambda n: n[0])
        beam = ranked[:width // 2]
        seen = set(id(n) for n in beam)
        quota = {}
        for n in ranked[width // 2:]:
            # the other half: the best nodes of every stack height, so that low stacks survive
            q = quota.get(n[4], 0)
            if q < width // 16:
                quota[n[4]] = q + 1
                beam.append(n)
        if not beam and best is None:
            print(f"beam died at ply {ply}; best node before:")
            print(fast.show(prev[0][1].field), prev[0][1].lines, fast.NAMES[fast.TYPE_OF[prev[0][1].cur]])
        if beam and ply % 25 == 0:
            b = beam[0][1]
            print(f"ply {ply}: best f {beam[0][0]:.0f} frame+{b.frame - t0} lines {b.lines} "
                  f"({time.time() - t_start:.0f} s)", flush=True)
    return best


def moves_of(node):
    out = []
    while node[2] is not None:
        out.append((node[2][1], node[3]))
        node = node[2]
    return out[::-1]


def main():
    args = sys.argv[1:]

    def opt(name, default):
        if name in args:
            i = args.index(name)
            return type(default)(args[i + 1])
        return default
    width, wait, goal = opt("--width", 300), opt("--wait", 0), opt("--lines", 100)
    out = opt("--out", "plan100")
    global TETRIS_ONLY, W_EVENT, BAND_FREE, MIN_TOP, MIN_FLOOR, W_BAND, W_BUMP, W_WELL, W_REACH
    MIN_TOP, MIN_FLOOR = opt("--top", MIN_TOP), opt("--floor", MIN_FLOOR)
    W_BAND, W_BUMP, W_WELL, W_REACH = opt("--wband", W_BAND), opt("--wbump", W_BUMP), opt("--wwell", W_WELL), opt("--wreach", W_REACH)
    TETRIS_ONLY = "--tetris-only" in args
    W_EVENT, BAND_FREE = opt("--wevent", W_EVENT), opt("--bandfree", BAND_FREE)
    print(f"params wevent={W_EVENT} bandfree={BAND_FREE} width={width} wait={wait} top={MIN_TOP} floor={MIN_FLOOR} wband={W_BAND} wbump={W_BUMP} wwell={W_WELL} wreach={W_REACH}")
    g = Game()
    g.to_level_menu()
    t0 = g.start_game(wait)
    g.f(DOWN, 1)
    g.until(lambda r: r[0x68] != 1)
    g.until(lambda r: r[0x68] == 1)
    s0 = g.state()
    print(f"Start held on frame {t0}; second piece spawns on frame {s0.frame}; pieces {fast.NAMES[fast.TYPE_OF[s0.cur]]} "
          f"{fast.NAMES[fast.TYPE_OF[s0.nxt]]}")
    best = search(s0, t0, width, goal)
    if best is None:
        print("no finished run")
        return
    total, node = best
    mv = moves_of(node)
    print(f"PLAN: {total} frames = {total / 60.0988:.2f} s for {goal} lines, {len(mv) + 1} pieces "
          f"(record 9828 frames = 163.54 s)")
    ys, clears, softs, prev_lines = {}, {}, 0, s0.lines
    seq = [m[0] for m in mv] + [node[1]]
    for i, (s, m) in enumerate(mv):
        ys[m[2]] = ys.get(m[2], 0) + 1
        softs += m[3]
        d = seq[i + 1].lines - s.lines
        if d:
            clears[d] = clears.get(d, 0) + 1
    print("lock rows", dict(sorted(ys.items())), "| clears by size", dict(sorted(clears.items())), "| one-frame-sooner locks", softs)
    for i in (20, 40, 80, 160):
        if i < len(mv):
            print(f"field before piece {i} (frame +{mv[i][0].frame - t0}, lines {mv[i][0].lines}):")
            print(fast.show(mv[i][0].field))
    # replay in the ROM-level model
    for s, (x, o, y, soft, k_soft, path, L) in mv:
        g.play(s, path, soft, k_soft, L)
    g.f(0, 8)
    r = g.m.ram
    lines = (r[0x71] & 15) * 100 + (r[0x70] >> 4) * 10 + (r[0x70] & 15)
    print(f"ROM-level model after replay: lines {lines}, frame {len(g.masks)}, level {r[0x64]}")
    p = write_inputs(LOGS / f"{out}.inputs.txt", [from_mask(b) for b in g.masks],
                     f"plan100 width={width} wait={wait} start_frame={t0} end_frame={t0 + total} frames={total}")
    print(p)
    print(fast.show(node[1].field))


if __name__ == "__main__":
    main()
