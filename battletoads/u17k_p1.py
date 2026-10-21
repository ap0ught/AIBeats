"""Track K2, phase 1 (snake 1): exhaustive single / double run-length mutations of K6[lo:hi]; goal = snake 1's TAIL gone as
early as possible (the next snake appears the frame after) with the toad standing at (449, 7678).
    python u17k_p1.py <tag> <base json or segment> <lo> <hi> [rounds=2]"""
import json, sys, os
from u17k_sim import *

tag, base, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 2
ins0 = json.load(open(base))["inputs"] if base.endswith(".json") else seg(base)
ins0 = ins0[:420] + [""] * 300
s = Sim(f"u17k_p1_{tag}.log")
logf = open(FIX / f"u17k_p1_{tag}.txt", "a", encoding="utf-8")


def log(*a):
    t = " ".join(str(x) for x in a)
    print(t, flush=True)
    logf.write(t + "\n"); logf.flush()


def evaluate(ins):
    tr = s.run(ins, 620, stop=lambda tr: len(tr["tgone"]) >= 1)
    ok = bool(tr["tgone"]) and tr["toad"][:4] == (449, 7678, 0, 0) and tr["hp_min"] == 47
    return (tr["tgone"][0] if tr["tgone"] else 9999, ok, list(tr["tp"]), list(tr["hp"]), tr["toad"])


def mutations(ins):
    runs = rle(ins[:hi])
    idx = [i for i, (st, b, n) in enumerate(runs) if st + n > lo]
    for i in idx:
        st, b, n = runs[i]
        end = st + n            # boundary between run i and i+1 (index of first input of run i+1)
        if end >= hi or end < lo:
            continue
        nb = ins[end]
        for d in (1, 2, 3):
            # extend run i by d (overwrite the first d inputs of the next run)
            c = list(ins); c[end:end + d] = [b] * d
            yield f"ext {end}:{b or '-'}+{d}", c
            # shrink run i by d (next run's button starts earlier)
            if n > d:
                c = list(ins); c[end - d:end] = [nb] * d
                yield f"shr {end}:{b or '-'}-{d}", c
        for d in (1, 2):
            # insert d idle frames at the boundary (everything later shifts)
            c = ins[:end] + [""] * d + ins[end:]
            yield f"ins {end}+{d}", c
            c = ins[:end] + [b] * d + ins[end:]
            yield f"dup {end}:{b or '-'}+{d}", c
            if n > d:
                c = ins[:end - d] + ins[end:]
                yield f"del {end}:{b or '-'}-{d}", c


cur = list(ins0)
s.set_base(cur, 420, every=5)
best = evaluate(cur)
log(f"base: tail gone {best[0]} ok {best[1]} tail pauses {best[2]} head pauses {best[3]} toad {best[4]}")
for r in range(rounds):
    res = []
    for name, c in mutations(cur):
        c = c[:len(cur)]
        v = evaluate(c)
        res.append((v[0], name, v, c))
        if v[1] and v[0] < best[0]:
            log(f"  {name}: tail gone {v[0]} tail pauses {v[2]} head pauses {v[3]}")
    good = [x for x in res if x[2][1]]
    good.sort(key=lambda x: (x[0], len(x[2][3])))
    log(f"round {r}: {len(res)} mutations, {len(good)} valid; best {[(x[0], x[1]) for x in good[:8]]}")
    if not good or good[0][0] >= best[0]:
        break
    best = good[0][2]
    cur = good[0][3]
    json.dump({"inputs": cur[:420], "tail_gone": best[0], "tail_pauses": best[2], "head_pauses": best[3], "name": good[0][1]},
              open(FIX / f"u17k_p1_{tag}_best.json", "w"))
    s.set_base(cur, 420, every=5)
    if best[0] <= 576:
        break
log(f"final: tail gone {best[0]} tail pauses {best[2]} head pauses {best[3]}  rle {rle_str(cur[:420])}")
s.close()
