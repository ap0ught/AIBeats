"""u16b: generate u16b_climb3.py from u16b_climb2.py (adds ducking: Down).  One-off helper; run once."""
import os

s = open('u16b_climb2.py', encoding='utf-8').read()

tail_doc = '    env U16B_REFINE (kids polished per node, 6)  U16B_ROUNDS (3)\n"""'
assert tail_doc in s
s = s.replace(tail_doc, '''    env U16B_REFINE (kids polished per node, 6)  U16B_ROUNDS (3)

u16b_climb3.py (this file) = u16b_climb2.py + DUCKING.  The flier floors (1,900-2,600 px up, again near the top) shoot
sparks 22 px above the floor; up14 passes them by holding Down (animation 75: the toad ducks and slides, sparks pass
overhead), and a jump pressed straight out of a duck leaves at sprint speed (192).  The earlier families had no Down
at all and stalled at 2,496 px.  Moves now: ("stand", frames, ducked) | ("walk", w, ducked wait, d, n, dash, k) |
("jump", w, ducked wait, d, n, dash, k, h, da, da2), k = frames of Down between the run and the jump.  A ducking toad
(animation 75) counts as standing.
"""''')

a = s.index('def sample(rng):')
b = s.index('def main():')
new = '''DUCK = float(os.environ.get("U16B_PDUCK", 0.3))


def standing(s):
    return s.z == 0 and (1 <= s.anim <= 8 or s.anim == 75)


def sample(rng):
    """one random move: ("stand", wait, ducked) | ("walk", w, wd, d, n, dash, k) | ("jump", w, wd, d, n, dash, k, h, da, da2)"""
    if rng.random() < P_STAND:                               # just stand (or duck): the flier columns need a spark to pass first
        return ("stand", rng.choice([4, 6, 12, 24, 40]), rng.random() < 0.45)
    w = rng.choice([0, 0, 0, 0, 1, 2, 4, 8, 16, 32])
    wd = w > 0 and rng.random() < DUCK
    d = rng.choice(["Right", "Left", None, None])
    walk = rng.random() < 0.2
    if walk and d is None:
        d = rng.choice(["Right", "Left"])
    n = rng.choice([0, 0, 2, 4, 8, 12, 16, 24, 32, 48, 64]) if d else 0
    if walk:
        n = rng.choice([4, 8, 16, 24, 32, 48])
    k = rng.choice([1, 2, 4, 8, 12, 16, 24]) if rng.random() < DUCK * 0.8 else 0
    h = 0 if walk else rng.choice([4, 8, 10, 11, 12, 13, 14, 16, 20, 26, 32])
    da = rng.choice([d, d, "Right", "Left", None])
    da2 = rng.choice(["Right", "Left", None]) if rng.random() < 0.25 else da     # the air direction after A is let go
    dash = n >= 10 and rng.random() < 0.6
    if walk:
        return ("walk", w, wd, d, n, dash, k)
    return ("jump", w, wd, d, n, dash, k, h, da, da2)


def neighbours(mv):
    """the moves one or two frames away from mv (same directions)"""
    out = []
    if mv[0] == "stand":
        out = [("stand", mv[1] - q, mv[2]) for q in (1, 2, 4) if mv[1] - q >= 1]
    elif mv[0] == "walk":
        _, w, wd, d, n, dash, k = mv
        out += [("walk", w - q, wd, d, n, dash, k) for q in (1, 2, 4) if w - q >= 0]
        out += [("walk", w, wd, d, n + q, dash, k) for q in (-4, -2, -1, 1, 2) if n + q >= 1]
        out += [("walk", w, wd, d, n, not dash, k)] if n >= 4 else []
        out += [("walk", w, wd, d, n, dash, k + q) for q in (-4, -2, -1, 1, 2) if k and k + q >= 0]
    else:
        _, w, wd, d, n, dash, k, h, da, da2 = mv
        out += [("jump", w - q, wd and w - q > 0, d, n, dash, k, h, da, da2) for q in (1, 2, 4) if w - q >= 0]
        out += [("jump", w + 1, wd, d, n, dash, k, h, da, da2)]
        if d:
            out += [("jump", w, wd, d, n + q, dash, k, h, da, da2) for q in (-4, -2, -1, 1, 2) if n + q >= 0]
            out += [("jump", w, wd, d, n, not dash, k, h, da, da2)] if n >= 3 else []
        out += [("jump", w, wd, d, n, dash, k + q, h, da, da2) for q in (-4, -2, -1, 1, 2) if k and k + q >= 0]
        out += [("jump", w, wd, d, n, dash, k, h + q, da, da2) for q in (-2, -1, 1, 2) if 2 <= h + q <= 34]
    return out


def run_move(e, s0, mv, base):
    """play one move from a standing toad -> (inputs, state) when it stands again unhurt and not lower, ("END", ...) when the
    arrival cutscene started during it, None otherwise"""
    H0 = Hof(s0)
    near_top = H0 - base >= 3900
    if mv[0] == "stand":
        ins, s = [], s0
        inp = ("Down",) if mv[2] else ()
        for _ in range(mv[1]):
            s = e.step(inp, 1)
            ins.append("+".join(inp))
            if s.hp < s0.hp or s.lives < s0.lives or s.level != 7:
                return None
            if near_top and s.anim == 50:
                return finish(e, ins, s, s0.lives)
        return (ins, s) if (s.z == 0 and Hof(s) - H0 >= -4) else None
    walk = mv[0] == "walk"
    if walk:
        _, w, wd, d, n, dash, k = mv
        h, da, da2 = 0, None, None
    else:
        _, w, wd, d, n, dash, k, h, da, da2 = mv
    seq = [("Down",) if wd else ()] * w
    if d and n:
        seq += ([(d,), ()] if dash else []) + [(d,)] * n
    seq += [("Down",)] * k
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
            if j >= len(seq) - 1:                              # the last frame of the sequence: a ducking toad may stay ducked
                return (ins, s) if (standing(s) and H - H0 >= -4) else None
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
a2 = 'print(f"u16b_climb2 {tag}: refine'
assert a2 in s
s = s.replace(a2, 'print(f"u16b_climb3 {tag}: duck {DUCK}, refine')
a3 = 'k = ((Hof(cs) - base) // 16, cs.x // 12, len(ci) // 24 if mv[0] == "stand" else -1)'
assert a3 in s
s = s.replace(a3, 'k = ((Hof(cs) - base) // 16, cs.x // 12, (len(ci) // 24, mv[2]) if mv[0] == "stand" else -1)')
a4 = "assert s.hp == 47 and s.lives == lives0 and s.z == 0, s"
assert a4 in s
open('u16b_climb3.py.tmp', 'w', encoding='utf-8').write(s)
os.replace('u16b_climb3.py.tmp', 'u16b_climb3.py')
print('written u16b_climb3.py')
