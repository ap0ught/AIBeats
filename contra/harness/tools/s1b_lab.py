"""Second-pass lab for the stage 1 boss wall: beam variants + refinement from a saved boss-start state.

    python tools/s1b_lab.py boss <state e.g. s1/w0_boss> <seg.json of that run> <run rows> [w,d,j ...] [norefine]
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s1  # noqa: E402
from contra.stages.s1_common import Farm, Pad, log  # noqa: E402

a = sys.argv[1:]
if a[0] == "boss":
    state, seg, nrun = a[1], a[2], int(a[3])
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(seg).read_text())["rows"]]
    rows_boss = rows[:nrun]
    pad_boss = Pad.from_rows(rows_boss[-40:])
    jobs = [tuple(None if v == "None" else int(v) for v in x.split(",")) for x in a[4:] if "," in x]
    jobs = jobs or [(8, 0, 3121), (8, 0, 3113), (8, 0, 3125), (8, 2, 3117), (10, 0, 3121), (8, 3, 3113)]
    with Farm(3, name="s1b_lab") as farm:
        t0 = time.time()

        def variant(gg, job):
            w_, d_, j_ = job
            gg.load_file(state, pad_boss, rows=rows_boss)
            t1 = time.time()
            res_ = s1.boss_fight(gg, width=w_, delay=d_, jump_at=j_)
            log(f"variant {job}: {None if res_ is None else len(gg.rows)} in {time.time() - t1:.0f} s")
            return None if res_ is None else list(gg.rows)
        outs = farm.map(variant, jobs)
        print("kill rows", [(j, None if o is None else len(o)) for j, o in zip(jobs, outs)], f"{time.time() - t0:.0f} s")
        outs = [o for o in outs if o is not None]
        best = min(outs, key=len)
        Path("logs/s1/lab_boss_best.json").write_text(json.dumps(["+".join(r) for r in best]))
        if "norefine" not in a:
            part = best[nrun:]
            better = s1.refine_rows(farm, state, pad_boss, part, s1.door_hp, passes=4, tag="boss refine")
            print("refined", len(part), "->", len(better), "kill row", nrun + len(better), f"{time.time() - t0:.0f} s")
elif a[0] == "refine":
    state, nrun = a[1], int(a[3])
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(a[2]).read_text())]
    pad_boss = Pad.from_rows(rows[:nrun][-40:])
    with Farm(3, name="s1b_lab") as farm:
        t0 = time.time()
        part = rows[nrun:]
        better = s1.refine_rows(farm, state, pad_boss, part, s1.door_hp, passes=int(a[4]) if len(a) > 4 else 4, tag="boss refine")
        Path("logs/s1/lab_boss_refined.json").write_text(json.dumps(["+".join(r) for r in rows[:nrun] + better]))
        print("refined", len(part), "->", len(better), "kill row", nrun + len(better), f"{time.time() - t0:.0f} s")
elif a[0] == "script":
    state, nrun = a[1], int(a[3])
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(a[2]).read_text())["rows"]]
    rows_boss = rows[:nrun]
    pad_boss = Pad.from_rows(rows_boss[-40:])
    with Farm(3, name="s1b_lab") as farm:
        t0 = time.time()
        best = s1.boss_fight2(farm, farm.g0, state, pad_boss, rows_boss)
        print("kill row", None if best is None else len(best), f"{time.time() - t0:.0f} s")
        if best is not None:
            Path("logs/s1/lab_boss_script.json").write_text(json.dumps(["+".join(r) for r in best]))
            if "refine" in a:
                better = s1.refine_rows(farm, state, pad_boss, best[nrun:], s1.door_hp, passes=2, tag="boss refine", max_moves=150)
                print("refined", len(best) - nrun, "->", len(better), "kill row", nrun + len(better), f"{time.time() - t0:.0f} s")
elif a[0] == "air":
    # python tools/s1b_lab.py air <state> <seg.json> <run rows> "d,j,pre:n1.n2.n3" ...
    state, nrun = a[1], int(a[3])
    rows = [tuple(x for x in r.split("+") if x) for r in json.loads(Path(a[2]).read_text())["rows"]]
    rows_boss = rows[:nrun]
    pad_boss = Pad.from_rows(rows_boss[-40:])
    jobs = []
    for x in a[4:]:
        head, plan = x.split(":")
        d, j, pre = [int(v) for v in head.split(",")]
        jobs.append((d, j, bool(pre), tuple(int(v) for v in plan.split(".") if v)))
    with Farm(3, name="s1b_lab") as farm:
        def variant(gg, job):
            d_, j_, pre_, plan_ = job
            gg.load_file(state, pad_boss, rows=rows_boss)
            t1 = time.time()
            res_ = s1.boss_fight(gg, width=8, delay=d_, jump_at=j_, air_plan=plan_, pre_fire=pre_)
            hp_land = None
            log(f"variant {job}: kill row {None if res_ is None else len(gg.rows)} in {time.time() - t1:.0f} s")
            return None if res_ is None else list(gg.rows)
        outs = farm.map(variant, jobs)
        print("kill rows", [(j, None if o is None else len(o)) for j, o in zip(jobs, outs)])
        outs = [o for o in outs if o is not None]
        if outs:
            Path("logs/s1/lab_boss_air.json").write_text(json.dumps(["+".join(r) for r in min(outs, key=len)]))
