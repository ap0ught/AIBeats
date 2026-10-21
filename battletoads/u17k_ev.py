"""Track K2: head AND tail timeline of room 1 for a script.
    python u17k_ev.py <tag> <base segment> <n0 = prefix length of base> "<n>:<buttons>;..." [frames] [toad every N from F]
-> logs/fix/u17k_ev_<tag>.txt"""
import sys
from u17k_lib import *

tag, base, n0, spec = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
total = int(sys.argv[5]) if len(sys.argv) > 5 else 1500
every = int(sys.argv[6]) if len(sys.argv) > 6 else 0
efrom = int(sys.argv[7]) if len(sys.argv) > 7 else 0
ins = seg(base)[:n0] + parse(spec)
ins += [""] * max(0, total - len(ins))
ins = ins[:total]


def events(e, ins, every=0, efrom=0, n_base=0, stop_on_hurt=True):
    out, prev, pd, run = [], {0x4C: None, 0x4D: None}, {0x4C: None, 0x4D: None}, {0x4C: None, 0x4D: None}
    nm = {0x4C: "head", 0x4D: "tail"}
    for n, b in enumerate(ins, n_base + 1):
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        t = info(m)
        td = f"toad {t['x']},{t['H']} z{t['z']} a{t['an']} s{t['spd']} v{t['vy']:.1f}"
        for oid in (0x4C, 0x4D):
            hs = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == oid]
            h = hs[0] if hs else None
            p = prev[oid]
            paused = bool(h and p and h == p)
            started = pd[oid] is not None
            if run[oid] and not paused:
                if started or oid == 0x4C:
                    out.append(f"{run[oid][0]}..{n - 1}: {nm[oid]} PAUSE x{n - run[oid][0]} at {run[oid][1]} | {run[oid][2]}")
                run[oid] = None
            if paused and not run[oid]:
                run[oid] = (n, h, td)
            if h and not p:
                out.append(f"{n}: {nm[oid]} appears {h} | {td}")
                pd[oid] = None
            if p and not h:
                out.append(f"{n}: {nm[oid]} gone (last {p}) | {td}")
            if h and p and not paused:
                d = (h[0] - p[0], h[1] - p[1])
                if d != pd[oid]:
                    out.append(f"{n}: {nm[oid]} {pd[oid]} -> {d} at {p} | {td}")
                    pd[oid] = d
            prev[oid] = h
        if every and n % every == 0 and n >= efrom:
            out.append(f"   {n} [{b}] {td} f{t['face']} head {prev[0x4C]} tail {prev[0x4D]}")
        if stop_on_hurt and (t["hp"] < 47 or t["lvl"] != 8):
            out.append(f"{n}: STOP hp {t['hp']} level {t['lvl']} toad {t['x']},{t['H']}")
            break
    return out


if __name__ == "__main__":
    e = BizHawk(log_name=f"u17k_ev_{tag}.log")
    e.load("B4_end0")
    out = events(e, ins, every, efrom)
    open(FIX / f"u17k_ev_{tag}.txt", "w").write("\n".join(out) + "\n")
    print("\n".join(out))
    e.close()
