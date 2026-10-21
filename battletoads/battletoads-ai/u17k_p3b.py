"""Track K2, phase 3 stage 2: behind a stage-1 line (jump shift k at `cut`, Right hold), the boarding of the head on the top
run (idle to b, Left x2, A x a) and the dash jump (Right, idle, Right+A x54) at j: earliest capture in the exit hole.
    python u17k_p3b.py <tag> <cut> <k> <hold> [b offsets from the corner, default 15..27] [a list]"""
import sys, json
from u17k_sim import *
k6 = seg("K6")
tag, cut, k, hold = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
boffs = [int(v) for v in sys.argv[5].split(",")] if len(sys.argv) > 5 else list(range(15, 28))
alist = [int(v) for v in sys.argv[6].split(",")] if len(sys.argv) > 6 else [8]
pre = k6[:cut] + k6[cut + k:1508] if k >= 0 else k6[:cut] + [""] * (-k) + k6[cut:1508]
head = pre + ["Right+A"] * 20 + ["Right"] * hold
s = Sim(f"u17k_p3b_{tag}.log")
base = head + [""] * 500
turn = [None]


def stop(tr):
    if turn[0] is None and tr["head"] and tr["head"][0] == 112 and tr["head"][1] < 7984 and tr["n"] > 1600:
        turn[0] = tr["n"]
    return False


tr = s.set_base(base, 1500, every=20)
tr = s.run(base, 1716, stop=stop)
corner = turn[0]
print(f"{tag}: jump at {len(pre)}, corner at {corner} (K6 1709), head pauses {[p for p in tr['hp'] if p > 1500]}", flush=True)
s.set_base(base, corner, every=5)
logf = open(FIX / f"u17k_p3b_{tag}.txt", "a")
best = None
for b in boffs:
    for a in alist:
        ins = base[:corner + b] + ["Left"] * 2 + ["A"] * a + [""] * 400
        # ride: when does the toad stand on the head (z 0, H 8062)?
        st = {"stand": None, "topturn": None}

        def stop2(tr):
            if st["topturn"] is None and tr["head"] and tr["head"][1] == 8048:
                st["topturn"] = tr["n"]
            if st["stand"] is None and tr["toad"][1] == 8062 and tr["toad"][2] == 0 and tr["n"] > corner + b + 10:
                st["stand"] = (tr["n"], tr["toad"][0], tr["head"])
            return False
        tr = s.run(ins, corner + b + 2 + a + 40, stop=stop2)
        if not st["stand"]:
            line = f"b +{b} a {a}: never stands on the head (toad {tr['toad']}, head {tr['head']})"
            print(line, flush=True); logf.write(line + "\n")
            continue
        # dash jump sweep: the tap when the head is at about x 190..206
        res = []
        sbase = ins
        n_top = st["topturn"]
        for j in range(n_top + 42, n_top + 56):
            c = sbase[:j] + ["Right", "", ] + ["Right+A"] * 54 + [""] * 200
            cap = {"cap": None, "headx": None}

            def stop3(tr):
                if tr["n"] == j:
                    cap["headx"] = tr["head"]
                    cap["toad"] = tr["toad"][:3]
                    cap["hp"] = [p for p in tr["hp"] if p > 1500]
                if cap["cap"] is None and tr["toad"][0] >= 360 and tr["toad"][1] >= 8090 and tr["toad"][2] == 0:
                    cap["cap"] = tr["n"]
                return cap["cap"] is not None or tr["hp_min"] < 47
            tr = s.run(c, j + 90, stop=stop3)
            res.append((j, cap["cap"], cap["headx"], cap.get("toad"), tr["hp_min"], cap.get("hp")))
        good = [r for r in res if r[1] and r[4] == 47]
        line = (f"b +{b} a {a}: stands {st['stand']} top turn {n_top} (K6 1750); dash taps -> capture: "
                f"{[(r[0], r[1], r[2][0] if r[2] else None) for r in res]}; head pauses at the first good tap {good[0][5] if good else None}")
        print(line, flush=True); logf.write(line + "\n")
        if good:
            g = min(good, key=lambda r: r[1])
            if best is None or g[1] < best[0]:
                best = (g[1], b, a, g[0], g)
                json.dump({"inputs": (ins[:g[0]] + ["Right", ""] + ["Right+A"] * 54), "capture": g[1], "corner": corner, "b": b, "a": a, "tap": g[0],
                           "cut": cut, "k": k, "hold": hold}, open(FIX / f"u17k_p3b_{tag}_best.json", "w"))
print("best", best, "(K6: capture 1858, tap 1801)")
logf.write(f"best {best}\n")
s.close()
