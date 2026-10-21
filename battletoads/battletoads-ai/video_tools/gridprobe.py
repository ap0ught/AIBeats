"""Find input perturbations that crash/kill, for the emulator-grid shot. Headless, no recording.
python yt/gridprobe.py <inputs.txt> <capname> <start> <len> <n_variants> <seed>"""
import sys, random, json
sys.path.insert(0, ".")
from toads.emulator import BizHawk
src, cap, S, L, N, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
lines = [l for l in open(src).read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name=f"gridprobe_{cap}_{S}.log")
k0 = S // 1000 * 1000
e.load(f"{cap}_f{k0}")
for i in range(k0, S):
    e.step(bt(lines[i]), 1)
base = e.msave()
rng = random.Random(seed)
seg = lines[S:S + L]
special = [i for i in range(1, L - 1) if seg[i] != seg[i - 1]]
out = []
def play(ins):
    e.mload(base)
    lives0 = e.ram(0x11)[0]
    for j, l in enumerate(ins):
        e.step(bt(l), 1)
        if e.ram(0x11)[0] != lives0:
            return j
    return None
print("baseline", play(seg), flush=True)
for v in range(N):
    ins = list(seg)
    kind = rng.choice(["shift", "drop", "hold"])
    p = rng.choice(special) if special else rng.randrange(L)
    if kind == "shift":
        d = rng.choice([-6, -4, -3, -2, 2, 3, 4, 6, 8])
        blk = seg[p:p + 12]
        q = max(0, p + d)
        ins[p:p + 12] = ["Left"] * len(blk)
        ins[q:q + len(blk)] = blk
        ins = ins[:L]
    elif kind == "drop":
        for j in range(p, min(L, p + 10)):
            ins[j] = "Left"
    else:
        b = rng.choice(["Left,Up", "Left,Down", "Left,A"])
        for j in range(p, min(L, p + rng.choice([4, 8, 14]))):
            ins[j] = b
    died = play(ins)
    out.append(dict(v=v, kind=kind, p=p, died=died, ins=ins))
    print(v, kind, p, died, flush=True)
json.dump(dict(src=src, cap=cap, S=S, L=L, variants=out), open(f"yt/gridprobe_{cap}_{S}.json", "w"))
e.close()
