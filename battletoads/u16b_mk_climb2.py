"""u16b: generate u16b_climb2.py from u16b_climb.py (adds the refinement pass).  One-off helper; run once."""
import os

s = open('u16b_climb.py', encoding='utf-8').read()

# 1. docstring addition
tail_doc = 'No memory writes.  Nothing here is a route segment; u16b_build.py makes B8 from the result.\n"""'
assert tail_doc in s
s = s.replace(tail_doc, '''No memory writes.  Nothing here is a route segment; u16b_build.py makes B8 from the result.

u16b_climb2.py (this file) = u16b_climb.py + REFINEMENT: the random moves come from a coarse grid (waits 0/1/2/4/8/16/32,
runs 0/2/4/8/12/16/24/32/48/64, A held 4..32), which costs a frame or two on every floor.  After the random tries the best
kids of a node (the climbing ones first) are polished: every neighbour move (wait, run length, A hold a frame or two
shorter or longer, dash on/off) is tried, and one that stands in the same spot sooner replaces it, until nothing improves.
    env U16B_REFINE (kids polished per node, 6)  U16B_ROUNDS (3)
"""''')

# 2. replace candidate() by sample() + neighbours() + run_move()
a = s.index('def candidate(e, s0, rng, base):')
b = s.index('def main():')
new = '''def sample(rng):
    """one random move: ("stand", wait) | ("walk", w, d, n, dash) | ("jump", w, d, n, dash, h, da, da2)"""
    if rng.random() < P_STAND:                               # just stand: the flier columns need a spark to pass first
        return ("stand", rng.choice([6, 12, 24, 40]))
    w = rng.choice([0, 0, 0, 0, 1, 2, 4, 8, 16, 32])
    d = rng.choice(["Right", "Left", None, None])
    walk = rng.random() < 0.2
    if walk and d is None:
        d = rng.choice(["Right", "Left"])
    n = rng.choice([0, 0, 2, 4, 8, 12, 16, 24, 32, 48, 64]) if d else 0
    if walk:
        n = rng.choice([4, 8, 16, 24, 32, 48])
    h = 0 if walk else rng.choice([4, 8, 10, 11, 12, 13, 14, 16, 20, 26, 32])
    da = rng.choice([d, d, "Right", "Left", None])
    da2 = rng.choice(["Right", "Left", None]) if rng.random() < 0.25 else da     # the air direction after A is let go
    dash = n >= 10 and rng.random() < 0.6
    if walk:
        return ("walk", w, d, n, dash)
    return ("jump", w, d, n, dash, h, da, da2)


def neighbours(mv):
    """the moves one or two frames away from mv (same directions)"""
    out = []
    if mv[0] == "stand":
        out = [("stand", mv[1] - k) for k in (1, 2, 4) if mv[1] - k >= 1]
    elif mv[0] == "walk":
        _, w, d, n, dash = mv
        out += [("walk", w - k, d, n, dash) for k in (1, 2, 4) if w - k >= 0]
        out += [("walk", w, d, n + k, dash) for k in (-4, -2, -1, 1, 2) if n + k >= 1]
        out += [("walk", w, d, n, not dash)] if n >= 4 else []
    else:
        _, w, d, n, dash, h, da, da2 = mv
        out += [("jump", w - k, d, n, dash, h, da, da2) for k in (1, 2, 4) if w - k >= 0]
        out += [("jump", w + 1, d, n, dash, h, da, da2)]
        if d:
            out += [("jump", w, d, n + k, dash, h, da, da2) for k in (-4, -2, -1, 1, 2) if n + k >= 0]
            out += [("jump", w, d, n, not dash, h, da, da2)] if n >= 3 else []
        out += [("jump", w, d, n, dash, h + k, da, da2) for k in (-2, -1, 1, 2) if 2 <= h + k <= 34]
    return out


def run_move(e, s0, mv, base):
    """play one move from a standing toad -> (inputs, state) when it stands again unhurt and not lower, ("END", ...) when the
    arrival cutscene started during it, None otherwise"""
    H0 = Hof(s0)
    near_top = H0 - base >= 3900
    if mv[0] == "stand":
        ins, s = [], s0
        for _ in range(mv[1]):
            s = e.step((), 1)
            ins.append("")
            if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
                return None
            if near_top and s.anim == 50:
                return finish(e, ins, s, s0.lives)
        return (ins, s) if (s.z == 0 and Hof(s) - H0 >= -4) else None
    walk = mv[0] == "walk"
    if walk:
        _, w, d, n, dash = mv
        h, da, da2 = 0, None, None
    else:
        _, w, d, n, dash, h, da, da2 = mv
    seq = [()] * w
    if d and n:
        seq += ([(d,), ()] if dash else []) + [(d,)] * n
    seq += [tuple(x for x in (da, "A") if x)] * h
    ins, s, air = [], s0, False
    for j in range(125):
        inp = seq[j] if j < len(seq) else ((da2,) if (da2 and not walk) else ())
        s = e.step(inp, 1)
        ins.append("+".join(inp))
        if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
            return None
        if near_top and s.anim == 50:
            return finish(e, ins, s, s0.lives)
        H = Hof(s)
        if walk:
            if j >= len(seq) + 1:
                return (ins, s) if (s.z == 0 and 1 <= s.anim <= 8 and H - H0 >= -4) else None
            if s.z != 0 and H < H0 - 6:
                return None                                    # walked off an edge
        elif j >= len(seq) - h:
            if s.z != 0:
                air = True
                if H < H0 - 6 and j >= len(seq):
                    return None                                # falling below where it started: it cannot stand "not lower" any more
            elif air and 1 <= s.anim <= 8:
                return (ins, s) if H - H0 >= -4 else None
        elif s.z != 0 and H < H0 - 6:
            return None                                        # ran off an edge before the jump
    return None


'''
s = s[:a] + new + s[b:]

# 3. the expansion loop
i0 = s.index('        kids, ends = {}, None\n')
i1 = s.index('        for ci, cs, csid in kids.values():\n')
new2 = '''        kids, ends = {}, None

        def offer(mv):
            """play mv from this node; file the result -> the kid key it landed in (None when it failed, "END" when it finished)"""
            nonlocal ends
            e.mload(sid)
            r = run_move(e, st, mv, base)
            if r is None:
                return None
            if r[0] == "END":
                _, ci, cs, cut, cutx, flat = r
                if not flat:
                    cost = frames + len(ci) + max(0, 183 - cs.x) / 3.0
                    if ends is None or cost < ends[0]:
                        ends = (cost, ci, cs, cut, cutx, flat, mv)
                return "END"
            ci, cs = r
            k = ((Hof(cs) - base) // 16, cs.x // 12, len(ci) // 24 if mv[0] == "stand" else -1)   # waits of different length are different moves
            if k not in kids or len(ci) < len(kids[k][0]):
                if k in kids:
                    e.mfree(kids[k][2])
                kids[k] = (ci, cs, e.msave(), mv)
            return k

        for _ in range(tries):
            offer(sample(rng))
        # refinement: polish the best kids (the climbing ones first, highest then soonest) and the best finish
        seen = set()
        for rnd in range(ROUNDS):
            order = sorted(kids.items(), key=lambda kv: (-kv[0][0], len(kv[1][0])))
            todo = [(k, v[3]) for k, v in order if k[2] == -1 and (Hof(v[1]) - base) > dh + 24][:REFINE]
            todo += [(k, v[3]) for k, v in order if k[2] == -1 and (Hof(v[1]) - base) <= dh + 24][:2]
            better = False
            for k, mv in todo:
                n0 = len(kids[k][0])
                for nb in neighbours(mv):
                    if nb in seen:
                        continue
                    seen.add(nb)
                    offer(nb)
                if len(kids[k][0]) < n0:
                    better = True
            if ends is not None:
                c0 = ends[0]
                for nb in neighbours(ends[6]):
                    if nb not in seen:
                        seen.add(nb)
                        offer(nb)
                better = better or ends[0] < c0
            if not better:
                break
        kids = {k: v[:3] for k, v in kids.items()}
        if ends is not None:
            ends = ends[:6]
'''
s = s[:i0] + new2 + s[i1:]
a1 = 'EXTRA = int(os.environ.get("U16B_EXTRA", 300))'
assert a1 in s
s = s.replace(a1, a1 + '\nREFINE = int(os.environ.get("U16B_REFINE", 6))\nROUNDS = int(os.environ.get("U16B_ROUNDS", 3))')
a2 = 'print(f"u16b_climb {tag}: tries'
assert a2 in s
s = s.replace(a2, 'print(f"u16b_climb2 {tag}: refine {REFINE}x{ROUNDS}, tries')
open('u16b_climb2.py.tmp', 'w', encoding='utf-8').write(s)
os.replace('u16b_climb2.py.tmp', 'u16b_climb2.py')
print('written u16b_climb2.py')
