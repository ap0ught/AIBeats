"""Search (not an argument) for a legal way to touch the alien guardian with the Barrier active.

    python tools/s8_barrier_search.py [state=s8/dev_g437] [emus=1]

From 80 rows before the guardian appears (Barrier already taken), no firing at all, so any loss of guardian HP is
a touch. Every schedule: first jump on row a (0..150 step 2), every later jump on the
landing row, Right held; variants: Right released for the first k rows of each jump (changes the Y sub-pixel
carry $94 and the X at which the wall is met), and a stop of s rows before the first jump.
Reports, per variant: guardian HP at the end, the smallest Y Bill had while at the wall face (world X >= 610), the
largest world X he had while at Y <= 112 (the height at which the wall's side lets him pass: bank7
check_player_solid_bg_collision tests the column X+8 from Y-11 down 27 px), and the highest landing made at X >= 600.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages.s3s8_engine import Engine, hpos, find_slot  # noqa: E402

state = sys.argv[1] if len(sys.argv) > 1 else "s8/dev_g437"
emus = int(sys.argv[2]) if len(sys.argv) > 2 else 1
N = 262


def rows_for(a, k, s):
    """first jump at row a (A on a, a+1), Right released on the k rows after each A, s rows standing still before a."""
    return a, k, s


with Engine(emus, tag="s8") as eng:
    root = eng.root(state)
    # closed-loop per schedule: build the rows frame by frame from a trace of the previous attempt is not needed:
    # jumps "on landing" are found by simulating once per schedule with A pressed on every row Bill stands.
    jobs = []
    for a in range(0, 151, 2):
        jobs.append((a, 0, 0))
    for a in range(0, 151, 6):
        jobs.append((a, 6, 0))
    for s in (10, 25, 40):
        for a in range(40, 151, 6):
            jobs.append((a, 0, s))

    def make(a, k, s):
        rows = []
        for i in range(N):
            r = ["Right"]
            if a - s <= i < a:
                r = []
            rows.append(r)
        return rows

    best = {"hp": None, "miny": (999, None), "maxx": (0, None), "land": (999, None)}
    kills = []
    out = []

    def run(job):
        a, k, s = job
        rows = make(a, k, s)
        # pass 1: find the landings, jump again on each (A needs a fresh press: rows i, i+1, then released)
        jumps = [a]
        for _ in range(6):
            rr = [list(r) for r in rows]
            for j in jumps:
                for d in (0, 1):
                    if j + d < N:
                        rr[j + d].append("A")
                for d in range(1, k + 1):
                    if j + d < N and "Right" in rr[j + d]:
                        rr[j + d].remove("Right")
            tr = eng.sim(root, [tuple(r) for r in rr])
            nxt = next((i + 1 for i in range(jumps[-1] + 8, N - 2) if not tr[i]["jump"] and not tr[i]["edge"]), None)
            if nxt is None:
                break
            jumps.append(nxt)
        return job, jumps, tr

    res = eng.sims  # noqa
    import threading
    results = [None] * len(jobs)

    def work(i):
        results[i] = run(jobs[i])
    for i0 in range(0, len(jobs), emus):
        th = [threading.Thread(target=work, args=(i,)) for i in range(i0, min(i0 + emus, len(jobs)))]
        for t in th:
            t.start()
        for t in th:
            t.join()
    for job, jumps, tr in results:
        g = [find_slot(z, 0x10) for z in tr]
        hp_end = None
        for z, k_ in zip(tr, g):
            if k_ is not None:
                hp_end = z[f"h{k_}"]
        dead = any(z["death"] & 1 for z in tr)
        miny = min((z["y"] for z in tr if hpos(z) >= 610), default=999)
        maxx = max((hpos(z) for z in tr if z["y"] <= 112 and hpos(z) >= 540), default=0)
        land = min((z["y"] for z in tr if hpos(z) >= 600 and not z["jump"] and not z["edge"]), default=999)
        if hp_end is not None and hp_end < 103:
            kills.append((job, jumps, hp_end))
        if miny < best["miny"][0]:
            best["miny"] = (miny, job)
        if maxx > best["maxx"][0]:
            best["maxx"] = (maxx, job)
        if land < best["land"][0]:
            best["land"] = (land, job)
    print(f"{len(jobs)} schedules (first jump row offset, Right released rows after A, stop before the jump)")
    print("schedules in which the guardian lost HP without a shot:", kills)
    print("smallest Y at the wall face (world X >= 610):", best["miny"], "(needs <= 112 to pass over the wall's side)")
    print("largest world X at Y <= 112:", best["maxx"], "(the wall's side is met at X 616; the guardian's box starts at 643)")
    print("highest standing position at world X >= 600 (Y):", best["land"], "(the wall top would be Y 116)")
