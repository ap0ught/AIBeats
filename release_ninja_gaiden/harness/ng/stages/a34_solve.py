"""Acts 3-4 stage solver: exact TAS sync as far as it goes -> TAS-guided legal beam to the stage end (bosses: to the
kill) -> finish (tally, earliest Start skip) -> open-loop verification -> check_inputs. Owned by the Acts 3-4 agent.

    python ng/stages/a34_solve.py <stage> [--start <state>] [--hist <inputs file>] [--tag name] [--W 10]
                                  [--no-sync] [--prefix <a34 rows name>]

Output: logs/a34/<stage>_<tag>.inputs.txt = our rows from the start state's next frame up to and including the
next stage's load frame; logs/a34/<stage>_<tag>.json = frames, verification, legality; the end state is saved as
states/tmp/a34_end/<stage>_<tag>.State (= the next stage's load frame).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a34_core as K  # noqa: E402
import a34_beam as BM  # noqa: E402
import a34_follow as FW  # noqa: E402
from a34_finish import finish  # noqa: E402
from ng.inputs import read_inputs, write_inputs  # noqa: E402

BOSS = {7, 11}


def solve(name, start=None, hist_file="", tag="v1", W=10, sync=True, prefix_name="", log=print, c=6.0,
          max_steps=100000, rollout=0, c2=0.0, sync_only=False):
    st = K.BY_NAME[name]
    _, c0, c1, tstate = K.STAGES[st]
    start = start or tstate
    hist = read_inputs(hist_file) if hist_file else []
    e = K.open_emu(f"a34_solve_{name}_{tag}.log")
    res = {"stage": name, "start": start, "hist": hist_file, "tag": tag}
    try:
        s = e.load(start)
        f0 = s.frame
        res["frame0"] = f0
        rows = []
        rows = []
        # a chained start (the next-stage load frame): wait for control (first play-loop frame) with no input
        from ng.mode import TICKS
        e.tick(TICKS)
        n = 0
        while n < 400:
            s1 = e.step((), 1)
            n += 1
            if s1.get("gm", 0) > 0:
                break
        e.tick(None)
        if n > 1:
            rows = [()] * n
            log(f"waited {n} frames for control (frame {s1.frame})")
        else:
            e.load(start)
        if prefix_name:
            pre = K.load_rows(prefix_name)
            rows += pre
            e.run(pre)
        elif sync:
            # exact TAS sync from a TAS state only (a chained state never equals the TAS RAM)
            r0 = K.ram_np(e.ram_all())
            d0 = K.diff(r0, K.ref_at(f0), K.STRICT & ~FW.SHIFTX)
            if len(d0) == 0:
                fo = FW.Follower(e, f0, 0, hist, maxextra=0, log=log)
                fo.follow(c1 - 152)
                rows = list(fo.out)
                e.mload(fo.ring[fo.t][0])
                log(f"exact sync to frame {f0 + len(rows)} ({len(fo.repairs)} repairs)")
                K.save_rows(f"sync_{name}", rows, f"exact TAS sync from {start} frame {f0} to {f0 + len(rows)}")
                if sync_only:
                    return {"sync_to": f0 + len(rows)}
            else:
                log(f"start differs from the TAS RAM in {len(d0)} bytes: no sync phase")
        t = time.time()
        s = e.state()
        if s.stage == st and not (st in BOSS and e.byte(0x497) == 0 and e.byte(0x66) < 16):
            path = BM.TasPath(c0, c1)
            if st in BOSS:
                bm = BM.BossBeam(e, st, s.frame, hist + rows, path, W=W, c=c, log=log, rollout=rollout, c2=c2)
            else:
                bm = BM.Beam(e, st, s.frame, hist + rows, path, W=W, log=log)
            r = bm.run(max_steps)
            if r is None:
                bp = getattr(bm, "best_partial", None)
                if bp is not None:
                    K.save_rows(f"{name}_{tag}_partial", rows + BM.node_rows(bp),
                                f"PARTIAL (beam died) from {start}; last node t={bp.t} room={bp.s.room}")
                raise RuntimeError("beam found nothing")
            tend, brows = r
            rows += brows
            res["beam_secs"] = round(time.time() - t)
            res["beam_end"] = tend
            e.load(start)
            e.run(rows)
        Lc = K.Legal(hist + rows)
        need = tuple(b for b in K.BTNS if Lc.held[b] and Lc.run[b] < Lc.HOLD)
        if need:                       # a press still too short at the hand-over: hold it one more frame
            e.step(need)
            rows.append(need)
        tail, load = finish(e, st)
        rows += tail
        res["load"] = load
        res["tas_load"] = K.TAS_LOAD[st]
        res["vs_tas"] = load - K.TAS_LOAD[st]
        # open-loop verification from the start state
        e.load(start)
        tr_s = e.run(rows)
        ok = tr_s.stage != st and tr_s.frame == load
        # the frame before must still be in the stage
        res["verified_open_loop"] = bool(ok)
        out = f"{name}_{tag}"
        K.save_rows(out, rows, f"start={start} frame0={f0} load={load} hist={hist_file}")
        endp = Path("tmp/a34_end") / out
        e.save(str(endp))
        res["end_state"] = f"states/{endp.as_posix()}.State"
        # legality: alone, and after the history
        p = K.OUT_DIR / f"{out}.inputs.txt"
        chk = subprocess.run([sys.executable, str(K.PROJECT / "check_inputs.py"), str(p)], capture_output=True, text=True)
        res["check_alone"] = chk.stdout.strip().splitlines()[-1]
        if hist:
            ph = K.OUT_DIR / f"{out}.withhist.inputs.txt"
            write_inputs(ph, hist + rows, "history + stage rows")
            chk2 = subprocess.run([sys.executable, str(K.PROJECT / "check_inputs.py"), str(ph)], capture_output=True,
                                  text=True)
            res["check_with_history"] = chk2.stdout.strip().splitlines()[-1]
        (K.OUT_DIR / f"{out}.json").write_text(json.dumps(res, indent=1))
        log(json.dumps(res))
        return res
    finally:
        e.close()


def main():
    args = sys.argv[1:]
    opt = BM.stage_from_args(args)
    start = opt("--start", "")
    hist = opt("--hist", "")
    tag = opt("--tag", "v1")
    W = opt("--W", 10)
    prefix = opt("--prefix", "")
    c = opt("--c", 6.0)
    rollout = opt("--rollout", 0)
    c2 = opt("--c2", 0.0)
    max_steps = opt("--max-steps", 100000)
    sync = "--no-sync" not in args
    solve(args[0], start or None, hist, tag, W, sync, prefix, log=lambda m: print(m, flush=True), c=c, rollout=rollout, c2=c2,
          sync_only="--sync-only" in args, max_steps=max_steps)


if __name__ == "__main__":
    main()
