"""Exact search of the abstract "hose" problem (third pass): one wall target that every press can hit, 10 slots,
a press fires min(5, free) pellets, the one that hits frees its slot 27 frames after the press, the others 28;
presses at least CAP frames apart. With `double` (two targets side by side, both in reach) a press of >= kd pellets
scores two hits (two slots free at 27).

    python tools/s4t_hose.py <hits> [double kd]

Prints the earliest press time of the last needed press (first press at 0) and one optimal schedule.
"""
import sys

CAP = 5


def solve(need, per_press=1, kd=2, tmax=400, miss_ok=True, hit_free=27, miss_free=28):
    # state: (cd, slots) -> (hits, back); slots = sorted tuple of frames until free (0 = free)
    states = {(CAP, (0,) * 10): (0, None)}
    for t in range(tmax):
        nxt = {}
        best_done = None
        for (cd, slots), (h, back) in states.items():
            # no press
            ns = tuple(max(0, f - 1) for f in slots)
            key = (min(CAP, cd + 1), ns)
            o = nxt.get(key)
            if o is None or o[0] < h:
                nxt[key] = (h, back)
            free = slots.count(0)
            if cd >= CAP and free:
                k = min(5, free)
                opts = [1] if per_press == 1 else ([2, 1] if k >= kd else [1])
                if miss_ok:
                    opts.append(0)
                for nh in opts:
                    new = sorted(slots[k:] + (hit_free,) * nh + (miss_free,) * (k - nh))
                    ns2 = tuple(max(0, f - 1) for f in new)
                    h2 = h + nh
                    b2 = (t, k, nh, back)
                    if h2 >= need:
                        if best_done is None:
                            best_done = b2
                        continue
                    key = (1, ns2)
                    o = nxt.get(key)
                    if o is None or o[0] < h2:
                        nxt[key] = (h2, b2)
        if best_done is not None:
            seq = []
            b = best_done
            while b is not None:
                seq.append(b[:3])
                b = b[3]
            seq.reverse()
            return t, seq
        # dominance pruning: drop states that are far behind the best hit count
        mx = max(v[0] for v in nxt.values())
        states = {k: v for k, v in nxt.items() if v[0] >= mx - 6}
    return None, None


if __name__ == "__main__":
    need = int(sys.argv[1])
    if len(sys.argv) > 2:
        t, seq = solve(need, per_press=2, kd=int(sys.argv[3]))
    else:
        t, seq = solve(need)
    print("last press at", t, "-> last hit", t + 20, "after the first press; presses:", len(seq))
    print(seq)
