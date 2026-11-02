"""Round 5: a Mesen (fastcore) beam for RUN rooms: hold the run direction, choose jump (A) / slash (B) / stop timings
chunk by chunk; score = progress along the direction (world x) - hp penalty; dedup on Ryu's state.
Results are CANDIDATES: replay them on NesHawk (work/r4/finstage.py or work/r5/nhcheck.py) before they count.

    python work/r5/runbeam.py <start.mst> <prefix rows|-> <dir R|L> <goal> <out> [--hist rows] [--W 24] [--C 8]
        [--steps 400] [--hpw 12] [--minhp 1] [--ymax 999] [--vars std|wide]
start.mst: states/mesen/r5/<name>.mst (its frame = the frame after the prefix rows; the prefix rows are only used
  for the Enforcer history and are written in front of the found rows).
goal: room:<r>  (room byte becomes r, or the stage changes)
      x:<room>:<le|ge>:<wpos>[:<ylo>:<yhi>]  (standing or not, in that room past wpos)
Writes logs/r5/<out>.inputs.txt (prefix + rows) and logs/r5/<out>.json; prints 'RESULT'."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

P = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(P / "ng" / "stages"))
sys.path.insert(0, str(P))
import a56_common as C  # noqa: E402
from ng import fastcore as F  # noqa: E402
from ng.inputs import read_inputs, write_inputs  # noqa: E402


def rows_file(n):
    for c in (n, f"logs/r5/{n}.inputs.txt", f"logs/r4/{n}.inputs.txt", f"logs/{n}.inputs.txt", f"logs/a34/{n}.inputs.txt"):
        if (P / c).exists():
            return P / c
    raise FileNotFoundError(n)


def wpos(s):
    sc = s["scroll_scr"]
    sc = sc - 256 if sc >= 128 else sc
    return sc * 256 + s["scroll"] + s["x"]


THROW = 0


def refpen(e):
    if not REF:
        return 0.0
    x = wpos(e)
    for dx in range(0, 12):
        for xx in (x - dx, x + dx):
            y = REF.get((e["room"], xx))
            if y is not None:
                return abs(e["y"] - y) + 2 * dx
    return 40.0


def variants(D, O, Cn, kind):
    """wanted rows (lists of button tuples) for one chunk."""
    d = (D,)
    V = {}
    V["D"] = [d] * Cn
    V["DA"] = [d + ("A",)] * 2 + [d] * (Cn - 2)
    V["DB"] = [d + ("B",)] * 2 + [d] * (Cn - 2)
    V["DB4"] = [d] * 4 + [d + ("B",)] * 2 + [d] * (Cn - 6)
    V["DA4"] = [d] * 4 + [d + ("A",)] * 2 + [d] * (Cn - 6)
    V["N"] = [()] * Cn
    V["DAB"] = [d + ("A",)] * 2 + [d] * 2 + [d + ("B",)] * 2 + [d] * (Cn - 6)
    V["CL"] = [(O, "A")] * 2 + [d] * (Cn - 2)
    if THROW:
        V["DT"] = [d + ("Up", "B")] * 2 + [d] * (Cn - 2)
        V["DAT"] = [d + ("A",)] * 2 + [d] * 2 + [d + ("Up", "B")] * 2 + [d] * (Cn - 6)
    if kind == "wide":
        V["O"] = [(O,)] * Cn
        V["NB"] = [("B",)] * 2 + [()] * (Cn - 2)
        V["OA"] = [(O, "A")] * 2 + [(O,)] * (Cn - 2)
        V["NA"] = [("A",)] * 2 + [()] * (Cn - 2)
        V["D4N"] = [d] * 4 + [()] * (Cn - 4)
        V["N4D"] = [()] * 4 + [d] * (Cn - 4)
    return V


def main():
    a = sys.argv[1:]

    def opt(n, dflt):
        if n in a:
            i = a.index(n)
            v = a[i + 1]
            del a[i:i + 2]
            return type(dflt)(v)
        return dflt
    hist = opt("--hist", "")
    W = opt("--W", 24)
    Cn = opt("--C", 8)
    steps = opt("--steps", 400)
    hpw = opt("--hpw", 12.0)
    minhp = opt("--minhp", 1)
    kind = opt("--vars", "std")
    ymax = opt("--ymax", 999)
    global YDEAD
    YDEAD = opt("--ydead", 241)
    global YW, BUCK
    YW = opt("--yw", 0.0)
    BUCK = opt("--buck", 1)
    global THROW
    THROW = opt("--throw", 0)
    global REFW, REF
    REFW = opt("--refw", 0.0)
    ref = opt("--ref", "")
    REF = {}
    if ref:
        import csv
        k0, k1 = map(int, ref.split(":"))
        for r in csv.DictReader(open(P / "logs/tas4751.trace.csv")):
            f = int(r["frame"])
            if k0 <= f <= k1:
                d = {k: int(r[k]) for k in ("scroll_scr", "scroll", "x", "y", "room")}
                REF.setdefault((d["room"], wpos(d)), d["y"])
    start, pref, D, goal, out = a[:5]
    O = "Left" if D == "Right" or D == "R" else "Right"
    D = "Right" if D in ("R", "Right") else "Left"
    sgn = 1 if D == "Right" else -1
    prefix = list(read_inputs(rows_file(pref))) if pref != "-" else []
    h = (list(read_inputs(rows_file(hist))) if hist else []) + prefix
    g = goal.split(":")

    def is_goal(s, stage0):
        if s["stage"] != stage0:
            return True
        if g[0] == "room":
            return s["room"] == int(g[1])
        if s["room"] != int(g[1]):
            return False
        x = wpos(s)
        ok = x <= int(g[3]) if g[2] == "le" else x >= int(g[3])
        if len(g) >= 6:
            ok = ok and int(g[4]) <= s["y"] <= int(g[5])
        return ok

    fc = F.FastCore(log_name=f"r5_runbeam_{out}.log")
    t0 = time.time()
    try:
        fr0 = fc.load_file(P / start if not str(start).startswith("states") else P / start, "root")
        r = fc.ram()
        s0 = {k: r[ad] for k, ad in fc.fields.items() if ad < 0x800}
        stage0, hp0 = s0["stage"], s0["hp"]
        print("start frame", fr0, "room", s0["room"], "wpos", wpos(s0), "y", s0["y"], "hp", hp0, flush=True)
        V = variants(D, O, Cn, kind)
        # beam member: (score, rows, enforcer, slot, last state)
        en0 = C.Enforcer(h[-1900:])
        beam = [(0.0, [], en0, "root", s0)]
        found = None
        nslot = 0
        for step in range(steps):
            cand = []
            for bi, (sc, rows, en, slot, s) in enumerate(beam):
                legal, ens = [], []
                for name, want in V.items():
                    e2 = en.copy()
                    legal.append([e2.emit(w, retry=0) for w in want])
                    ens.append((name, e2))
                # distinct legal variants only
                uniq = {}
                for (name, e2), L in zip(ens, legal):
                    uniq.setdefault(tuple(L), (name, e2))
                ls = [list(k) for k in uniq]
                res = fc.run_batch(slot, ls, record="all", keep=True, prefix=f"s{step}_{bi}_")
                for L, rr in zip(ls, res):
                    name, e2 = uniq[tuple(L)]
                    sts = rr.states
                    dead = False
                    gi = None
                    php = s["hp"]
                    for i, x in enumerate(sts):
                        if x["hp"] == 0 or (x["dead"] & 0x80) or x["y"] >= YDEAD or x["hp"] > php                                 or x["room"] != s["room"] and not is_goal(x, stage0):
                            dead = True
                            break
                        php = x["hp"]
                        if is_goal(x, stage0):
                            gi = i
                            break
                    if dead:
                        continue
                    if gi is not None:
                        rows2 = rows + L[:gi + 1]
                        key = (len(rows2), -sts[gi]["hp"])
                        if found is None or key < found[0]:
                            found = (key, rows2, sts[gi])
                            print(f"  GOAL step {step} frame {fr0 + len(rows2)} hp {sts[gi]['hp']} via {name}", flush=True)
                        continue
                    e = sts[-1]
                    if e["hp"] < minhp or e["y"] > ymax:
                        continue
                    if e["stage"] != stage0:
                        continue
                    score = sgn * wpos(e) - hpw * (hp0 - e["hp"]) - YW * e["y"] - REFW * refpen(e)
                    cand.append((score, rows + L, e2, rr.slot, e, name))
            if found is not None:
                break
            cand.sort(key=lambda c: -c[0])
            seen = set()
            nb = []
            for c in cand:
                e = c[4]
                k = (e["room"], wpos(e) // BUCK, e["y"] // BUCK, e["rflags"] & 0x44, e["hp"]) if BUCK > 1 else (e["room"], wpos(e), e["y"], e["rflags"] & 0x44, e["vy"], e["hp"], e["anim"])
                if k in seen:
                    continue
                seen.add(k)
                nb.append(c)
                if len(nb) >= W:
                    break
            if not nb:
                print("beam died at step", step, flush=True)
                break
            # copy survivors to stable slots, drop the rest
            newbeam = []
            for i, c in enumerate(nb):
                sl = f"b{(step % 2)}_{i}"
                fc.put(sl, fc.get(c[3]))
                newbeam.append((c[0], c[1], c[2], sl, c[4]))
            fc.drop_prefix(f"s{step}_")
            beam = newbeam
            b = beam[0]
            if step % 5 == 0:
                write_inputs(P / "logs" / "r5" / f"{out}_part.inputs.txt", prefix + b[1],
                             f"runbeam partial best: frame {fr0 + len(b[1])} wpos {wpos(b[4])} y {b[4]['y']} hp {b[4]['hp']}")
                print(f"step {step} frame {fr0 + len(b[1])} best wpos {wpos(b[4])} y {b[4]['y']} hp {b[4]['hp']} room "
                      f"{b[4]['room']} n {len(cand)} {time.time() - t0:.0f}s last {nb[0][5]}", flush=True)
        if found is None:
            b = beam[0]
            rows2 = b[1]
            print(f"NO GOAL; best partial frame {fr0 + len(rows2)} wpos {wpos(b[4])} y {b[4]['y']} hp {b[4]['hp']}",
                  flush=True)
            endf, ends, ok = fr0 + len(rows2), b[4], False
        else:
            rows2 = found[1]
            endf, ends, ok = fr0 + len(rows2), found[2], True
        (P / "logs" / "r5").mkdir(parents=True, exist_ok=True)
        fc.load_file(P / start, "root")
        fc.step(rows2)
        fc.save("end")
        fc.save_file("end", P / "states/mesen/r5" / f"{out}.mst", endf)
        write_inputs(P / "logs" / "r5" / f"{out}.inputs.txt", prefix + rows2,
                     f"{pref} + runbeam {D} to {goal} from {start}: Mesen frame {endf} ({'goal' if ok else 'partial'}); "
                     f"VERIFY ON NESHAWK")
        json.dump({"start": start, "prefix": pref, "goal": goal, "ok": ok, "end_frame": endf, "rows": len(prefix + rows2),
                   "hp": ends["hp"], "room": ends["room"], "wpos": wpos(ends), "y": ends["y"]},
                  open(P / "logs" / "r5" / f"{out}.json", "w"), indent=1)
        print(f"RESULT {out} ok={ok} frame {endf} room {ends['room']} wpos {wpos(ends)} y {ends['y']} hp {ends['hp']} "
              f"rows {len(prefix + rows2)} {time.time() - t0:.0f}s", flush=True)
    finally:
        fc.close()


if __name__ == "__main__":
    main()
