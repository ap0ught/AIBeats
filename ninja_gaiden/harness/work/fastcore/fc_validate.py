"""fastcore validation: find a (small) improvement of a legal stage segment with fastcore, then judge it on NesHawk.

    python work/fastcore/fc_validate.py <power-on inputs> <NesHawk trace csv> <c0> <goal> <tag> [--minutes 6]

c0 = the stage's control frame (rows 1..c0 are history); goal = the frame where $6D changes (stage exit) in the
baseline. Search: "shift earlier" = delete one row i of the baseline segment (later rows come one frame earlier),
kept when the player fields (x, xsub, y, room, scroll) one horizon later equal the baseline's one frame further
on (the candidate is a frame ahead), the whole power-on list stays legal, and the full remainder still reaches the
stage exit earlier. Every accepted step re-runs to the goal on Mesen. Then the result is judged:
  1. check_inputs (judge rules) on history + new rows,
  2. NesHawk open-loop replay from power-on (reset()) of history + new rows, per-frame fields vs Mesen's trace,
  3. NesHawk's DMC pad conflicts inside the new rows are listed; Mesen re-run with NesHawk's effective rows
     (row k := row k-1 on a conflict frame) must equal NesHawk exactly.
Writes logs/fcv_<tag>.inputs.txt (power-on rows through the new goal) and logs/fcv_<tag>.json.
"""
import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

P = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(P))
from ng.fastcore import FastCore, verify_on_neshawk  # noqa: E402
from ng.inputs import read_inputs, to_mask, from_mask, write_inputs  # noqa: E402
from ng.solve import legality as L  # noqa: E402

KEY = ("x", "xsub", "y", "room", "scroll", "scroll_scr", "stage")
CMP = ("x", "xsub", "y", "stage", "room", "hp", "timer", "rng", "bosshp", "pad", "scroll", "anim", "ninpo", "lagged")


def legal(hist, seg):
    return L.check([from_mask(m) for m in hist + seg]).get("pass")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs"); ap.add_argument("trace"); ap.add_argument("c0", type=int); ap.add_argument("goal", type=int)
    ap.add_argument("tag"); ap.add_argument("--minutes", type=float, default=6.0)
    ap.add_argument("--horizon", type=int, default=45); ap.add_argument("--every", type=int, default=30)
    a = ap.parse_args()
    rows = [to_mask(r) for r in read_inputs(a.inputs)]
    pads = {}
    with open(a.trace) as f:
        for r in csv.DictReader(f):
            pads[int(r["row"])] = int(r["pad"])
    hist = rows[:a.c0]
    boot = bytes(pads[k] for k in range(1, a.c0 + 1))          # NesHawk's effective pads: exact start state
    base = rows[a.c0:a.goal + 40]                               # segment + slack after the exit
    report = {"tag": a.tag, "c0": a.c0, "goal_base": a.goal}
    t_start = time.time()
    with FastCore(boot_rows=boot, log_name="fcv.log") as fc:
        fc.save("s")
        stop = [(0x6D, "changed", 0)]

        def to_goal(seg):
            r = fc.run_batch("s", [seg], record="last", stops=stop)[0]
            return r.rows_played if r.status == 1 else None

        g0 = to_goal(base)
        print(f"[{a.tag}] baseline reaches the exit after {g0} rows (frame {a.c0 + g0})", flush=True)
        report["base_rows"] = g0
        cur, cur_g = list(base), g0
        accepted = []
        frames_sim = 0
        i = 1
        while time.time() - t_start < a.minutes * 60 and i < cur_g - a.horizon:
            # checkpoints along the current baseline (every `every` rows), and its trace
            fc.load("s")
            _, btr, _ = fc.step(cur[:cur_g], record="all")
            frames_sim += cur_g
            ck = {}
            fc.load("s")
            for c in range(0, cur_g, a.every):
                if c:
                    fc.step(cur[c - a.every:c])
                    frames_sim += a.every
                fc.save(f"c{c}")
                ck[c] = f"c{c}"
            improved = False
            batch, meta = [], []
            for j in range(i, cur_g - a.horizon):
                cand_seg = cur[:j] + cur[j + 1:]
                c = (j // a.every) * a.every
                part = cand_seg[c:j + a.horizon]
                batch.append(part)
                meta.append((j, c))
                if len(batch) == 64 or j == cur_g - a.horizon - 1:
                    # group by checkpoint: run_batch needs one start slot -> run per checkpoint group
                    groups = {}
                    for p, (jj, cc) in zip(batch, meta):
                        groups.setdefault(cc, []).append((jj, p))
                    hits = []
                    for cc, items in groups.items():
                        res = fc.run_batch(ck[cc], [p for _, p in items], record="last")
                        frames_sim += sum(len(p) for _, p in items)
                        for (jj, p), r in zip(items, res):
                            # candidate played rows cc+1 .. jj+horizon of cand_seg == baseline position jj+horizon+1
                            want = btr[jj + a.horizon]          # baseline record after row jj+horizon+1
                            got = r.states[-1]
                            if all(got[k] == want[k] for k in KEY):
                                hits.append(jj)
                    batch, meta = [], []
                    for jj in sorted(hits):
                        cand_seg = cur[:jj] + cur[jj + 1:]
                        if not legal(hist, cand_seg[:cur_g + 10]):
                            continue
                        g = to_goal(cand_seg)
                        frames_sim += cur_g
                        if g is not None and g < cur_g:
                            print(f"[{a.tag}] accept delete row {jj} (frame {a.c0 + jj + 1}): exit after {g} rows "
                                  f"({cur_g - g} better)", flush=True)
                            accepted.append((jj, a.c0 + jj + 1, g))
                            cur, cur_g = cand_seg, g
                            i = jj
                            improved = True
                            break
                    if improved:
                        break
                if time.time() - t_start > a.minutes * 60:
                    break
            if not improved:
                break
        dt = time.time() - t_start
        report.update(accepted=accepted, new_rows=cur_g, gain=g0 - cur_g, search_s=round(dt, 1),
                      frames_simulated=frames_sim, fps=round(frames_sim / dt, 1))
        print(f"[{a.tag}] search done: {g0} -> {cur_g} rows, {len(accepted)} deletions, {frames_sim} frames in "
              f"{dt:.0f}s ({frames_sim / dt:.0f} f/s)", flush=True)
        seg = cur[:cur_g + 10]                                  # through the exit + 10 rows
        fc.load("s")
        _, mtr, _ = fc.step(seg, record="all")
    # 1. judge
    out = P / "logs" / f"fcv_{a.tag}.inputs.txt"
    write_inputs(out, [from_mask(m) for m in hist + seg], f"fastcore validation {a.tag}: rows 1..{a.c0} = "
                 f"{Path(a.inputs).name}, then the fastcore stage rows; play after reset()")
    j = subprocess.run([sys.executable, str(P / "check_inputs.py"), str(out), "--period", "5", "--hold", "2",
                        "--release", "2", "--windows", "600:109,1800:246"], capture_output=True, text=True)
    report["check_inputs"] = "PASS" if j.returncode == 0 else "FAIL"
    report["check_tail"] = j.stdout.strip().splitlines()[-1:] if j.stdout else j.stderr[-300:]
    print(f"[{a.tag}] check_inputs: {report['check_inputs']} {report['check_tail']}", flush=True)
    # 2. NesHawk open loop
    t = time.time()
    first, ntr, conflicts = verify_on_neshawk(hist, seg, mtr, fields=CMP)
    report["neshawk_s"] = round(time.time() - t, 1)
    report["neshawk_first_diff"] = first
    report["neshawk_conflicts"] = conflicts
    exit_n = next((s["frame"] for s in ntr if s["stage"] != ntr[0]["stage"]), None)
    report["neshawk_exit_frame"] = exit_n
    report["mesen_exit_frame"] = a.c0 + cur_g
    print(f"[{a.tag}] NesHawk: first differing frame {first}, pad conflicts {conflicts}, exit frame {exit_n} "
          f"(Mesen {a.c0 + cur_g})", flush=True)
    # 3. with NesHawk's conflicts applied (effective rows), Mesen must equal NesHawk exactly
    if conflicts:
        eff = list(seg)
        for fr in conflicts:
            k = fr - a.c0 - 1
            eff[k] = eff[k - 1] if k > 0 else hist[-1]
        with FastCore(boot_rows=boot) as fc:
            _, etr, _ = fc.step(eff, record="all")
        d = next((ntr[i]["frame"] for i in range(len(ntr)) if any(ntr[i].get(k) != etr[i].get(k) for k in CMP)), None)
        report["mesen_with_conflicts_first_diff"] = d
        print(f"[{a.tag}] Mesen with NesHawk's conflict frames applied: first difference {d}", flush=True)
    (P / "logs" / f"fcv_{a.tag}.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
