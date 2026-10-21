"""One-off patch of contra/resync.py (kept for the record): fence-wait repair, progress scoring, stall detection."""
import os
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "resync.py"
s = p.read_text(encoding="utf-8")
i = s.index("def repair_stage(")
head = s[:i]


def rep(a, b):
    global head
    assert a in head, a[:60]
    head = head.replace(a, b)


rep('''def play(emu: BizHawk, state: str | None, rows, chunk: int = 120, keep_trace: bool = False,
         stop_on_death: bool = True, stop_on_level: bool = True) -> Result:''',
    '''def play(emu: BizHawk, state: str | None, rows, chunk: int = 120, keep_trace: bool = False,
         stop_on_death: bool = True, stop_on_level: bool = True, stall: int = 0) -> Result:''')
rep('''            if s["level"] == lvl0 and s["lroutine"] == 4:
                prog = max(prog, s["screen"] * 256 + s["scroll"])''',
    '''            if s["level"] == lvl0 and s["lroutine"] in (4, 8, 9):
                pg = s["screen"] * 256 + s["scroll"] + (100000 if s["bossdef"] else 0)
                if pg > prog:
                    prog, last_gain = pg, i + j + 1
            if stall and stop_on_death and (i + j + 1) - last_gain > stall:
                reason, stop = "stall", True
                break''')
rep('''    prog = 0
    n = 0''', '''    prog = 0
    last_gain = 0
    n = 0''')
rep('''    return Result(reason, n, last["frame"], dict(last), prog, trace, last["lag"] - lag0)''',
    '''    res = Result(reason, n, last["frame"], dict(last), prog, trace, last["lag"] - lag0)
    res.last_gain = last_gain
    return res''')
rep('''            return (kind, t, rng.choice((2, 2, 3, 3, 4, 5, 6)))''',
    '''            return (kind, t, rng.choice((2, 2, 3, 3, 4, 5, 6, 7, 8, 9)))''')
rep('''    elif kind == "U+":                       # aim up for 3 frames''',
    '''    elif kind == "wait":                     # n frames of nothing before row t (wait for a base fence to drop)
        rows[t:t] = [()] * ed[2]
    elif kind == "U+":                       # aim up for 3 frames''')

new = r'''def edit_cost(ed) -> int:
    """Frames of real time an edit adds."""
    return {"P": ed[2] if len(ed) > 2 else 0, "wait": ed[2] if len(ed) > 2 else 0, "dup": 1, "del": -1}.get(ed[0], 0)


def repair_stage(pool: "Pool", state: str, rows, out: str, W: int = 240, H: int = 900, K: int = 12, seed: int = 1,
                 maxiter: int = 120, edits=None, meta=None, log=print, kinds0=("B+", "B+", "B+", "P", "P", "P"),
                 stall: int = 1800):
    """Play `rows` from savestate `state`; wherever it fails, repair and go on. Returns (done, rows, edits).

    Failures and repairs:
      death  - K random small edits in the W frames before it (see apply_edit); keep the one that gets furthest
               (progress first, then frames survived minus the frames the edit costs)
      elec   - the movie pressed Up at a base fence that is not down yet (the room was cleared later than in the
               movie's own game): insert exactly as many empty frames before that Up as it takes for the fence to drop
      stall  - no progress for `stall` frames: same random search around the place progress stopped
    rows are cut at the frame on which the level byte changes. Progress is saved to logs/<out>.seg.json."""
    rows = [tuple(r) for r in rows]
    edits = [tuple(e) for e in (edits or [])]
    for ed in edits:
        rows = apply_edit(rows, ed)
    rng = random.Random(seed + 1000 * len(edits))
    ck = {0: state}
    t00 = time.time()
    segp = LOGS_DIR / f"{out}.seg.json"
    segp.parent.mkdir(parents=True, exist_ok=True)
    e0 = pool.emus[0]

    def save(done, total):
        tmp = segp.with_name(segp.name + ".tmp")
        j = dict(meta or {})
        j.update({"state": state, "edits": edits, "done": done, "frames": total,
                  "rows": ["+".join(r) for r in (rows[:total] if done else [])]})
        tmp.write_text(json.dumps(j, indent=0), encoding="utf-8")
        tmp.replace(segp)

    def checkpoint(idx):
        if idx in ck:
            return ck[idx]
        base = max(k for k in ck if k <= idx)
        play(e0, ck[base], rows[base:idx], stop_on_death=False, stop_on_level=False)
        name = f"tmp/{out}_ck{idx}"
        e0.save(name)
        ck[idx] = name
        return name

    def drop_ck(after):
        for k in [k for k in ck if k > after]:
            del ck[k]

    fails = 0
    for it in range(maxiter):
        base = max(ck)
        r = play(e0, ck[base], rows[base:], stall=stall)
        D = base + r.frames
        log(f"[{out}] iter {it}: from {base}: {r}  (t+{time.time() - t00:.0f}s)")
        if r.reason in ("level", "end"):
            rows = rows[:D]
            save(True, D)
            log(f"[{out}] DONE: {D} frames from the stage state, {len(edits)} edits: {edits}")
            return True, rows, edits
        if r.reason in ("eof", "gameover"):
            log(f"[{out}] {r.reason} without finishing the stage: {r}")
            save(False, 0)
            return False, rows, edits
        if r.reason == "elec":
            up = D - 1                                   # the row whose Up was read on the frame the stun began
            c0 = max(0, up - 30)
            drop_ck(c0)
            cname = checkpoint(c0)
            x = play(e0, cname, rows[c0:up] + [()] * 400, keep_trace=True, stop_on_death=False, stop_on_level=False)
            j = next((i for i, s in enumerate(x.trace) if i >= up - c0 and s["cleared"]), None)
            if j is not None:
                n = (c0 + j) - up + 1                    # Up must be read on the frame AFTER the flag is set
                ed = ("wait", up, n)
                rows = apply_edit(rows, ed)
                edits.append(ed)
                log(f"[{out}]    fence still up at row {up}: waiting {n} frames")
                save(False, 0)
                fails = 0
                continue
            log(f"[{out}]    fence at row {up}: the room is not cleared within 400 frames -> random search")
        if r.reason == "stall":
            D = min(D, r.last_gain + 450)
        b_prog = r.progress
        w = W * (2 ** min(fails, 3)) * (2 if r.reason != "death" else 1)
        kinds = list(kinds0) + (["dup", "del", "A+", "U+", "B-"] if fails >= 2 else [])
        w0 = max(0, D - w)
        drop_ck(w0)
        cname = checkpoint(w0)
        cands = [rand_edit(rng, rows, w0, max(w0 + 1, D - 6), kinds) for _ in range(K * (1 + min(fails, 2)))]

        def trial(emu, ed):
            rr = apply_edit(rows, ed)
            return play(emu, cname, rr[w0:D + H + 2], stall=stall)
        res = pool.map(trial, cands)
        scored = []
        for ed, x in zip(cands, res):
            surv = w0 + x.frames - edit_cost(ed)
            fin = x.reason in ("level", "end")
            scored.append(((1 if fin else 0, 0 if fin else x.progress, -surv if fin else surv), ed, x))
        scored.sort(key=lambda t: t[0], reverse=True)
        (fin, pg, _), ed, x = scored[0]
        surv = w0 + x.frames - edit_cost(ed)
        log(f"[{out}]    {r.reason} at {D} (progress {b_prog}); window {w0}..{D}; best of {len(cands)}: {ed} -> "
            f"{x.reason} at {w0 + x.frames} progress {x.progress}; others {[(w0 + y.frames, y.progress) for _, _, y in scored[1:5]]}")
        if fin or pg > b_prog or (pg == b_prog and surv > D + 40):
            rows = apply_edit(rows, ed)
            edits.append(ed)
            fails = 0
            save(False, 0)
        else:
            fails += 1
            if fails > 7:
                log(f"[{out}] giving up at {D}")
                save(False, 0)
                return False, rows, edits
    save(False, 0)
    return False, rows, edits
'''
tmp = p.with_name("resync.py.tmp")
tmp.write_text(head + new, encoding="utf-8")
os.replace(p, p.with_name("resync.py.backup2"))
os.replace(tmp, p)
print("patched")
