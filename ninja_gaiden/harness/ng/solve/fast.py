"""ng.solve.fast - the Mesen search backend (ng/fastcore.py, docs knowledge/fastcore.md) folded into the toolkit.

Mesen runs ~2x NesHawk per process (FastPool(2) ~4x one EmuHawk) and is frame-identical to NesHawk EXCEPT NesHawk's
DMC controller-read conflicts (~1 per 700 frames of legal play): a Mesen result is only a CANDIDATE; the result is
always the NesHawk open-loop replay + the judge (`ng.solve.verify finish` / `verify_on_neshawk` + check_inputs).
Limits: <= 2 Mesen processes per agent, free RAM >= 2.5 GB (FastCore checks), 1 while a HOLD_FARMS exists.

    boot(history_rows, trace_csv=None) -> FastCore      power-on replay of the history; with NesHawk's own pad bytes
        (trace_csv = a NesHawk trace of that history: `python tools/trace_run.py <inputs> <name>` -> logs/<name>.trace.csv)
        the booted state equals NesHawk's exactly; without, it differs after NesHawk's first conflict in the history.
    pool(history_rows, trace_csv=None, n=2) -> FastPool
    legal_cands(wanted_list, history_rows) -> [rows]    every wanted candidate through the a56 Enforcer
    search(core, slot, history_rows, wanted_list, goal, stops=...) -> sorted [(score, i, result)]
        goal(states) -> (frame index reaching the goal or None, score tuple); runs everything in one run_batch.

    python -m ng.solve.fast slash <history file> <prefix rows file> N <out> <room,le|ge,gx,ylo,yhi>
        [--dir Left] [--H 160] [--stop 8-24:2] [--t1 0-4:2] [--t2 none,20-80:3] [--ta 30-56:2] [--trace csv]
        = work/tk/slashsearch.py on Mesen (FastPool(2)): hold dir (released between `stop` and the jump `ta`), B at t1
        (and t2), A at ta; the earliest goal with the most HP wins; writes prefix + best rows to <out>. Verify the
        result on NesHawk (`python -m ng.solve.verify finish ...` or a compare/snap replay) before using it.
"""
from __future__ import annotations

import itertools
import sys
import time

from . import common as C
from . import legality as L
from ng import fastcore as F  # noqa: E402

FastCore, FastPool, verify_on_neshawk, neshawk_pads = F.FastCore, F.FastPool, F.verify_on_neshawk, F.neshawk_pads


def _boot_rows(history_rows, trace_csv=None, extra=()):
    """history as NesHawk's own pad bytes (when a NesHawk trace of it is given) + extra rows as plain masks."""
    if trace_csv:
        return bytes(F.neshawk_pads(trace_csv, len(history_rows))) + bytes(F.masks_of(list(extra)))
    return list(history_rows) + list(extra)


def boot(history_rows, trace_csv=None, extra=()) -> "F.FastCore":
    return F.FastCore(boot_rows=_boot_rows(history_rows, trace_csv, extra))


def pool(history_rows, trace_csv=None, n=2, extra=()) -> "F.FastPool":
    return F.FastPool(n, boot_rows=_boot_rows(history_rows, trace_csv, extra))


def run_chunked(P, slot, cands, chunk=24, budget_s=None, log=print, reboot=None, **kw):
    """P.run_batch over `cands` in chunks of `chunk` (per pool), printing progress; stops early (remaining results
    None) once `budget_s` seconds are used. Big single batches (e.g. 128 x 160 rows) block for minutes inside one
    Mesen callback and got killed by the caller's command timeout: keep each call short and run long searches in
    the background (`run_in_background` / jobq), with per-candidate `stops` so dead / finished candidates end early.
    reboot: callable -> a fresh pool with `slot` loaded (used when a Mesen process dies; run_chunked.pool = the pool
    in use afterwards)."""
    out = [None] * len(cands)
    t0 = time.time()
    for i in range(0, len(cands), chunk):
        if budget_s is not None and time.time() - t0 > budget_s:
            log(f"run_chunked: budget {budget_s}s used after {i}/{len(cands)} candidates")
            break
        for attempt in range(3):
            try:
                res = P.run_batch(slot, cands[i:i + chunk], **kw)
                break
            except (OSError, F.FastCoreError) as e:          # a Mesen process died: restart the pool, retry
                if reboot is None or attempt == 2:
                    raise
                log(f"run_chunked: worker error {e!r}; restarting the pool")
                try:
                    P.close()
                except Exception:      # noqa: BLE001
                    pass
                P = reboot()
        out[i:i + len(res)] = res
        log(f"run_chunked: {min(i + chunk, len(cands))}/{len(cands)} in {time.time() - t0:.0f}s")
    run_chunked.pool = P          # the (possibly restarted) pool
    return out


def legal_cands(wanted_list, history_rows):
    out = []
    base = L.Enforcer(list(history_rows)[-1900:])
    for want in wanted_list:
        en = base.copy()
        out.append([en.emit(w) for w in want])
    return out


def _rng(s):
    out = []
    for part in s.split(","):
        if part == "none":
            out.append(None)
        elif "-" in part:
            lo, hi = part.split("-")
            st = 1
            if ":" in hi:
                hi, st = hi.split(":")
            out += list(range(int(lo), int(hi) + 1, int(st)))
        else:
            out.append(int(part))
    return out


def slash(a):
    def opt(n, d):
        if n in a:
            i = a.index(n)
            v = a[i + 1]
            del a[i:i + 2]
            return v
        return d
    D = opt("--dir", "Left")
    H = int(opt("--H", 160))
    T1, T2 = _rng(opt("--t1", "0-40")), _rng(opt("--t2", "none"))
    TA, SS = _rng(opt("--ta", "none")), _rng(opt("--stop", "none"))
    trace = opt("--trace", None)
    hf, rf, N, out, goal = a[0], a[1], int(a[2]), a[3], a[4]
    g = goal.split(",")
    groom, gcmp, gx, ylo, yhi = int(g[0]), g[1], int(g[2]), int(g[3]), int(g[4])
    hist = C.rows_of(hf)
    pre = C.rows_of(rf)[:N]
    wanted, keys = [], []
    for t1, t2, ta, ss in itertools.product(T1, T2, TA, SS):
        if t2 is not None and t2 <= t1 + 4:
            continue
        w = []
        for i in range(H):
            r = {D} if (D != "-" and (ss is None or i < ss or (ta is not None and i >= ta))) else set()
            if i in (t1, t1 + 1) or (t2 is not None and i in (t2, t2 + 1)):
                r.add("B")
            if ta is not None and i in (ta, ta + 1):
                r.add("A")
            w.append(tuple(r))
        wanted.append(w)
        keys.append((t1, t2, ta, ss))
    cands = legal_cands(wanted, hist + pre)
    uniq = {}
    for k, c in zip(keys, cands):
        uniq.setdefault(tuple(c), k)
    cl = [list(c) for c in uniq]
    print(f"{len(cl)} distinct legal candidates", flush=True)
    t0 = time.time()
    with pool(hist, trace, extra=pre) as P:
        P.save_all("s")
        res = run_chunked(P, "s", cl, chunk=32, record="all", stops=[(0x6D, "changed", 0), (0x65, "==", 0)])
    print(f"ran in {time.time() - t0:.0f}s", flush=True)
    best = None
    for c, r in zip(cl, res):
        if r is None:
            continue
        sts = r.states
        hit = None
        for i, s in enumerate(sts):
            x = C.abs_x(s)
            if s["room"] == groom and (x <= gx if gcmp == "le" else x >= gx) and ylo <= s["y"] <= yhi \
                    and not (s["rflags"] & 4):
                hit = i
                break
        if hit is None:
            continue
        hp = min(s["hp"] for s in sts[:hit + 1])
        key = (-hp, hit)
        if best is None or key < best[0]:
            best = (key, c[:hit + 1], uniq[tuple(c)])
    if best is None:
        print("no candidate reached the goal")
        return 1
    (nhp, hit), rows, k = best
    print(f"BEST frame {len(hist) + N + hit + 1} (Mesen) hp {-nhp} t1/t2/ta/stop {k}", flush=True)
    C.write_inputs(out, pre + rows, f"ng.solve.fast slash {goal}: Mesen frame {len(hist) + N + hit + 1} hp {-nhp} "
                                    f"{k}; VERIFY ON NESHAWK")
    return 0


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "slash":
        sys.exit(slash(rest))
