"""Verifier's offline analysis of the per-frame RAM captures written by u16v_replay.py.

    python u16v_analyze.py <inputs file> <tagA> <tagB>
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
inp, ta, tb = sys.argv[1], sys.argv[2], sys.argv[3]
A = (FIX / f"u16v_{ta}.ram").read_bytes()
B = (FIX / f"u16v_{tb}.ram").read_bytes()
N = len(A) // 2048
print(f"capture {ta}: {len(A)} bytes = {N} frames; capture {tb}: {len(B)} bytes; byte-identical: {A == B}")
print(f"sha1 of the whole capture: {ta} {hashlib.sha1(A).hexdigest()}  {tb} {hashlib.sha1(B).hexdigest()}")
print(f"sha1 of the last frame's RAM: {hashlib.sha1(A[-2048:]).hexdigest()}")


def r(f, addr):                      # RAM byte after frame f (1-based)
    return A[(f - 1) * 2048 + addr]


rows = Path(inp).read_text(encoding="utf-8").split("\n")
if rows[-1] == "":
    rows = rows[:-1]
ins = [frozenset(t for t in x.replace("+", ",").split(",") if t) for x in rows[1:]]
assert len(ins) == N

LEVEL, LIVES, ANIM, HP = 0x10, 0x11, 0x3B5, 0x51A
NAMES = {1: "Level 1 Ragnarok's Canyon", 3: "Level 3 Turbo Tunnel", 4: "Level 4 Arctic Caverns", 8: "Level 6 Karnath's Lair",
         7: "Level 8 Intruder Excluder", 11: "Level 9 Terra Tubes", 9: "Level 10 Rat Race", 10: "Level 11 Clinger-Winger",
         5: "Level 12 The Revolution", 13: "Level 13 Armageddon (the Dark Queen's tower)"}
out = {}
print("\n== every change of the level byte $10 ==")
changes = []
for f in range(2, N + 1):
    a, b = r(f - 1, LEVEL), r(f, LEVEL)
    if a != b:
        changes.append((f, a, b))
        print(f"  frame {f:6d}: {a:3d} -> {b:3d}   lives {r(f, LIVES)} hp {r(f, HP)}")
out["level_changes"] = changes
real = [(f, b) for f, a, b in changes if b not in (0, 254, 255)]
print("\n== levels entered (level byte not 0/254/255), in order ==")
seq = []
for k, (f, b) in enumerate(real):
    end = real[k + 1][0] if k + 1 < len(real) else N
    print(f"  frame {f:6d}: level byte {b:2d} = {NAMES.get(b, '?')}")
    seq.append(b)
out["level_sequence"] = seq
cuts = [f for f, a, b in changes if a == 13 and b == 254]
print("\n13 -> 254 changes:", cuts)
print("254/255 -> 13 changes:", [f for f, a, b in changes if b == 13])

print("\n== landing in Level 1: $3B5 5 -> 4 with level byte 1 ==")
land = [f for f in range(2, N + 1) if r(f, LEVEL) == 1 and r(f - 1, ANIM) == 5 and r(f, ANIM) == 4]
print("  frames:", land)
landing = land[0]
print("  frame  $3B5 anim  x($3FD) y($41B) z/depth($493) height($439) state($4B1) hp  pad($29)  input")
for f in range(landing - 16, landing + 8):
    print(f"  {f:6d}  {r(f, ANIM):3d}       {r(f, 0x3FD):3d}    {r(f, 0x41B):3d}     {r(f, 0x493):3d}        {r(f, 0x439):3d}       {r(f, 0x4B1):3d}    {r(f, HP):3d}  {r(f, 0x29):08b}  {','.join(sorted(ins[f - 1]))}")
# first frame the toad can be moved after landing: first frame its x changes
x0 = r(landing, 0x3FD)
mv = next((f for f in range(landing, landing + 400) if r(f, 0x3FD) != x0), None)
print(f"  first frame after the landing on which the toad's x changes: {mv}")

print("\n== lives $11 ==")
lv = []
for f in range(2, N + 1):
    a, b = r(f - 1, LIVES), r(f, LIVES)
    if a != b:
        lv.append((f, a, b, r(f, LEVEL)))
        print(f"  frame {f:6d}: {a} -> {b}  (level byte {r(f, LEVEL)}, hp {r(f, HP)})")
out["lives_changes"] = lv
g = [r(f, LIVES) for f in range(1190, N + 1)]
print(f"  lives from frame 1190 to the end: min {min(g)} max {max(g)}")

print("\n== health $51A: every change while a level is loaded ==")
hpchg = []
for f in range(2, N + 1):
    a, b = r(f - 1, HP), r(f, HP)
    if a != b:
        hpchg.append((f, a, b, r(f, LEVEL)))
        print(f"  frame {f:6d}: {a:3d} -> {b:3d}  (level byte {r(f, LEVEL)}, lives {r(f, LIVES)})")
out["hp_changes"] = hpchg

print("\n== health and lives when each level is left (frame before the level byte leaves it) and entered ==")
for f, a, b in changes:
    if a not in (0, 254, 255):
        print(f"  leaving {a:2d} at frame {f}: hp {r(f - 1, HP)} lives {r(f - 1, LIVES)}  score digits $5F4-$5F9 {[r(f - 1, 0x5F4 + i) for i in range(6)]}")
    if b not in (0, 254, 255):
        g = next((k for k in range(f, min(N, f + 600)) if r(k, HP) > 0), None)
        print(f"  entering {b:2d} at frame {f}: hp {r(f, HP)} lives {r(f, LIVES)}; first frame with hp > 0: {g} (hp {r(g, HP) if g else None})")

print("\n== the pad bytes the game itself read ==")
BIT = {"A": 0x80, "B": 0x40, "Select": 0x20, "Start": 0x10, "Up": 0x08, "Down": 0x04, "Left": 0x02, "Right": 0x01}
for addr in (0x29, 0x2A, 0x2B, 0x2C):
    vals = {}
    for f in range(1, N + 1):
        v = r(f, addr)
        vals[v] = vals.get(v, 0) + 1
    print(f"  ${addr:02X}: {len(vals)} distinct values; nonzero on {N - vals.get(0, 0)} frames")
# does $29 equal the input mask (allowing lag frames where the game did not poll)?
match = same_prev = other = 0
bad = []
for f in range(2, N + 1):
    m = 0
    for b in ins[f - 1]:
        m |= BIT[b]
    v = r(f, 0x29)
    if v == m:
        match += 1
    elif v == r(f - 1, 0x29):
        same_prev += 1
    else:
        other += 1
        if len(bad) < 10:
            bad.append((f, v, m))
print(f"  $29 == this frame's input mask on {match} frames; unchanged from the previous frame (no poll) on {same_prev}; neither: {other} {bad}")
st = [f for f in range(1, N + 1) if r(f, 0x29) & 0x10]
print(f"  frames where the game's own pad byte $29 has the Start bit: {st}")
for addr in (0x2A, 0x2C):
    nz = [f for f in range(1, N + 1) if r(f, addr)]
    print(f"  ${addr:02X} nonzero frames: {len(nz)} {nz[:12]}")

print("\n== the Queen ==")
ID3 = 0x3C4
lh = [f for f in range(2, N + 1) if r(f, LEVEL) == 13 and r(f - 1, ID3) == 0x7E and r(f, ID3) == 0x46]
print("  slot-3 id 0x7e -> 0x46 frames:", lh)
q = []
for f in range(2, N + 1):
    if r(f, LEVEL) == 13 and r(f, 0x586) != r(f - 1, 0x586) and r(f - 1, LEVEL) == 13:
        q.append((f, r(f - 1, 0x586), r(f, 0x586)))
print("  hit counter $586 changes (frame, from, to):", q[:40])
for c in cuts:
    print(f"  at cut frame {c}: hp {r(c, HP)} lives {r(c, LIVES)} toad x {r(c, 0x3FD)} anim {r(c, ANIM)} $F4 {r(c, 0xF4)}")
    print(f"     hp over the 700 frames before it: min {min(r(f, HP) for f in range(c - 700, c + 1))}")
l13 = [f for f in range(1, N + 1) if r(f, LEVEL) == 13]
print(f"  level 13 frames {l13[0]}..{l13[-1]}: toad hp min {min(r(f, HP) for f in l13 if f > l13[0] + 300)} (from 300 frames in)")

landing = land[0]
if len(cuts) >= 2:
    t = (cuts[1] - landing) / 60.0988
    print(f"\nRUN: landing {landing}, T. Bird cut (second 13->254) {cuts[1]}: {cuts[1] - landing} frames / 60.0988 = {t:.3f} s = {int(t // 60)}:{t % 60:06.3f}")
    print(f"record 749.25 s: difference {749.25 - t:.3f} s ({'UNDER' if t < 749.25 else 'NOT under'}); "
          f"record in frames at 60.0988: {749.25 * 60.0988:.1f} -> cut would have to be <= {int(landing + 749.25 * 60.0988 - 1e-9)}")
    t1 = (cuts[0] - landing) / 60.0988
    print(f"(first 13->254, the Queen's speech: {cuts[0]} -> {t1:.3f} s = {int(t1 // 60)}:{t1 % 60:06.3f}, NOT the end)")
    out.update(landing=landing, cuts=cuts, frames=cuts[1] - landing, seconds=t)
(FIX / "u16v_analysis.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
