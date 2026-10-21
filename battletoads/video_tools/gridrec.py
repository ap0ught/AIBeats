"""Record N perturbed attempts from one state, back to back, into one capture (for the emulator-grid shots).
python yt/gridrec.py <inputs.txt> <capname> <start> <len> <n> <seed> <outname>
-> video/<outname>.mkv and yt/<outname>.json {lead, S, L, variants:[{v, kind, p, died, offset}]}
Variant 0 is the real run (no change). died = frame (within the attempt) where lives changed, if not the real run's."""
import sys, random, json
sys.path.insert(0, ".")
from toads.emulator import BizHawk
src, cap, S, L, N, seed, name = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
lines = [l for l in open(src).read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
e = BizHawk(log_name=f"gridrec_{name}.log", record=name)
k0 = S // 1000 * 1000
e.load(f"{cap}_f{k0}")
steps = 0
for i in range(k0, S):
    e.step(bt(lines[i]), 1); steps += 1
base = e.msave()
rng = random.Random(seed)
seg = lines[S:S + L]
special = [i for i in range(1, L - 1) if seg[i] != seg[i - 1]]
out = []
for v in range(N):
    ins = list(seg)
    kind, p = "real", None
    if v:
        kind = rng.choice(["shift", "drop", "hold"])
        p = rng.choice(special) if special else rng.randrange(L)
        if kind == "shift":
            d = rng.choice([-6, -4, -3, -2, 2, 3, 4, 6, 8]); blk = seg[p:p + 12]; q = max(0, p + d)
            ins[p:p + 12] = [seg[p - 1]] * len(blk); ins[q:q + len(blk)] = blk; ins = ins[:L]
        elif kind == "drop":
            for j in range(p, min(L, p + 10)): ins[j] = seg[p - 1]
        else:
            b = rng.choice(["Left,Up", "Left,Down", "Left,A", "Up", "Down", "A", "B"])
            for j in range(p, min(L, p + rng.choice([4, 8, 14]))): ins[j] = b
    e.mload(base)
    lives0 = e.ram(0x11)[0]
    changes = []
    for j, l in enumerate(ins):
        e.step(bt(l), 1)
        lv = e.ram(0x11)[0]
        if lv != lives0:
            changes.append((j, lv)); lives0 = lv
    out.append(dict(v=v, kind=kind, p=p, changes=changes, offset=steps))
    steps += L
    print(v, kind, p, changes, flush=True)
json.dump(dict(src=src, cap=cap, S=S, L=L, steps=steps, variants=out), open(f"yt/{name}.json", "w"))
e.close()
