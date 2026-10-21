"""chain2: the best complete run with the current solvers. Runs the eight stage solvers in order, each from the REAL
state the previous one leaves, and proves every hand-over by a replay from power-on on a fresh emulator.
Carried over from chain1/chain.py (same conventions); new: several named chains side by side (--chain), stage 1 from
any title-screen wait (--wait), rule v2 (check_inputs.py's defaults now include the 600/1,800-frame windows).

    python chain.py --chain A --wait 0          run / resume chain A (stages already verified are skipped)
    python chain.py --chain A --from 4          throw away chain A's stage 4.. results and redo from stage 4
    python chain.py --chain A --to 3            stop after stage 3
    python chain.py --chain A --tag A2          name of this attempt's solver outputs (default c2<chain>)
    python chain.py --chain A --table           print the per-stage table from chain_A.json and exit
    python chain.py --chain A --extra 3 "--emus 2"   more arguments for one stage's solver

Everything lives in this folder (a private snapshot of the project: see SNAPSHOT.md). Per chain X:
    chain_X.json                     what the chain has verified so far (this is what makes it resumable)
    runs/X/through_sK.inputs.txt     power-on up to and including the row that produces stage K+1's first frame
    runs/X/run.inputs.txt            the whole run (stage 8: to the END frame P, plus a 60-row untimed tail)
    states/X/sK_pre.State, sK_start.State   the real state one frame before / on stage K's first frame
    logs/chain/X/                    chain.log and every solver's output
Conventions (as chain1): row i (0-based) of an input list is applied on emulator frame i + 2 of a fresh launch.
Stages 2/4 start ON the stage's first frame, the others one frame BEFORE it and produce that frame's row themselves.
The press history given to a solver is always the real rows before its first own row (whole file; each solver takes
the tail it uses: s2_solve 40 rows, s6/s7 12, s3/s8 ~1,800 rows, s5 all), so the rules hold across every cut;
check_inputs.py (defaults = rule v2) runs on every prefix as well.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from contra import clock  # noqa: E402
from contra.emulator import BizHawk, LOGS_DIR, STATES_DIR, PROJECT  # noqa: E402
from contra.inputs import read_inputs, write_inputs, to_mask  # noqa: E402
from contra.stages.s3s8_lib import Pad  # noqa: E402

assert PROJECT == HERE, f"the snapshot's emulator module must resolve to chain2, got {PROJECT}"

# the record's stage segments in NES frames (knowledge/project_rules.md, from record_events.json, +/- 2 each)
RECORD = {1: 3907, 2: 3716, 3: 3934, 4: 5761, 5: 6125, 6: 4143, 7: 4488, 8: 3273}
RECORD_CUM_END = {1: 3907, 2: 7623, 3: 11558, 4: 17319, 5: 23444, 6: 27587, 7: 32075, 8: 35349}
CHAIN1 = {1: 3900, 2: 3604, 3: 3542, 4: 5269, 5: 6041, 6: 4050, 7: 4831, 8: 3237}

FIELDS = dict(clock.FIELDS)
FIELDS.update({"lives": 0x32, "death": 0xB4, "screen": 0x64, "scroll": 0x65, "weapon": 0xAA, "fc": 0x1A, "rng": 0x34,
               "gameover": 0x38, "loc": 0x40, "pause": 0x25, "x": 0x334, "y": 0x31A})

CHAIN = "A"          # set in main()


def runs_dir() -> Path:
    return HERE / "runs" / CHAIN


def chain_logs() -> Path:
    return LOGS_DIR / "chain" / CHAIN


def state_file() -> Path:
    return HERE / f"chain_{CHAIN}.json"


def log(*a):
    line = time.strftime("%H:%M:%S ") + f"[{CHAIN}] " + " ".join(str(x) for x in a)
    print(line, flush=True)
    chain_logs().mkdir(parents=True, exist_ok=True)
    with open(chain_logs() / "chain.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
    if path.exists():
        try:
            os.replace(path, path.with_name(path.name + ".backup"))
        except OSError:
            pass
    os.replace(tmp, path)


def load_state() -> dict:
    if state_file().exists():
        return json.loads(state_file().read_text(encoding="utf-8"))
    return {"stages": {}}


def rows_sha1(rows) -> str:
    return hashlib.sha1(bytes(to_mask(r) for r in rows)).hexdigest()


def through_path(k: int) -> Path:
    return runs_dir() / f"through_s{k}.inputs.txt"


def legal_filler(prior_rows, n: int = 1):
    """n rows of 'nothing' that are legal after prior_rows (a button pressed on the last row is held one more)."""
    p = Pad.from_rows(prior_rows[-2000:])
    out = []
    for _ in range(n):
        r = p.fix(())
        p.push(r)
        out.append(r)
    return out


def check_inputs(path: Path) -> tuple[bool, str]:
    c = subprocess.run([sys.executable, str(HERE / "check_inputs.py"), str(path)], capture_output=True, text=True)
    lines = c.stdout.strip().splitlines()
    return c.returncode == 0, (lines[-1] if lines else f"exit {c.returncode}")


# ---------------------------------------------------------------------------------------- power-on verification
def stage_firsts(tr):
    """{stage number: index into tr of its first frame ($2C == 4, in game, not the demo)}."""
    out = {}
    for i, s in enumerate(tr):
        if s["groutine"] == 5 and s["demo"] == 0 and s["lroutine"] == 4 and s["level"] < 8 and s["level"] + 1 not in out:
            out[s["level"] + 1] = i
    return out


def find_deaths(tr):
    d = []
    for i in range(1, len(tr)):
        s, p = tr[i], tr[i - 1]
        if s["groutine"] != 5 or s["demo"]:
            continue
        if (s["death"] & 1) and not (p["death"] & 1):
            d.append(s["frame"])
        elif s["pstate"] == 2 and p["pstate"] != 2:
            d.append(s["frame"])
    return d


def _facts(tr, firsts):
    return {"firsts": {str(k): tr[i]["frame"] for k, i in firsts.items()},
            "lag_at_first": {str(k): tr[i]["lag"] for k, i in firsts.items()},
            "weapon_at_first": {str(k): tr[i]["weapon"] for k, i in firsts.items()},
            "lives_at_first": {str(k): tr[i]["lives"] for k, i in firsts.items()},
            "fc_at_first": {str(k): tr[i]["fc"] for k, i in firsts.items()},
            "rng_at_first": {str(k): tr[i]["rng"] for k, i in firsts.items()}}


def verify_prefix(rows, k_next: int, tag: str, save: bool = True) -> dict:
    """Replay rows from power-on on a fresh emulator. Expect stage k_next's first frame exactly on the last row.
    Saves states/<chain>/s<k_next>_pre and s<k_next>_start. Returns facts (ok, why, per-stage first frames, lag, deaths)."""
    t0 = time.time()
    e = BizHawk(log_name=f"chain/{CHAIN}/verify_{tag}_s{k_next}.log", fields=FIELDS)
    try:
        e.trace(True)
        e.run(rows[:-1])
        tr = list(e.last_trace)
        if save:
            e.save(f"{CHAIN}/s{k_next}_pre")
        e.run(rows[-1:])
        tr += list(e.last_trace)
        if save:
            e.save(f"{CHAIN}/s{k_next}_start")
        ram_sha1 = hashlib.sha1(e.ram_all()).hexdigest()
    finally:
        e.close()
    assert tr[0]["frame"] == 2 and tr[-1]["frame"] == len(rows) + 1, (tr[0]["frame"], tr[-1]["frame"], len(rows))
    firsts = stage_firsts(tr)
    deaths = find_deaths(tr)
    last = tr[-1]
    out = {"rows": len(rows), "last_frame": last["frame"], "ram_sha1": ram_sha1, "deaths": deaths, **_facts(tr, firsts),
           "last": {x: last[x] for x in ("level", "lroutine", "weapon", "lives", "fc", "rng", "lag", "groutine")},
           "seconds": round(time.time() - t0)}
    why = []
    if k_next not in firsts:
        why.append(f"stage {k_next}'s first frame never comes (last frame: level {last['level']}, $2C {last['lroutine']}, "
                   f"$18 {last['groutine']}, gameover {last['gameover']})")
    elif tr[firsts[k_next]]["frame"] != last["frame"]:
        why.append(f"stage {k_next}'s first frame is frame {tr[firsts[k_next]]['frame']}, expected the last row's "
                   f"frame {last['frame']}")
    if last["weapon"] != 0x13:
        why.append(f"weapon ${last['weapon']:02x} at the end, expected $13")
    if deaths:
        why.append(f"deaths on frames {deaths[:5]}")
    out["ok"] = not why
    out["why"] = why
    return out


# ---------------------------------------------------------------------------------------- solver adapters
def run_proc(cmd, logname: str, timeout: int = 4 * 3600) -> int:
    chain_logs().mkdir(parents=True, exist_ok=True)
    outp = chain_logs() / logname
    log("   run:", " ".join(str(c) for c in cmd), "->", outp.name)
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    with open(outp, "w", encoding="utf-8") as f:
        p = subprocess.Popen([str(c) for c in cmd], cwd=str(HERE), stdout=f, stderr=subprocess.STDOUT, env=env)
        log(f"   pid {p.pid}")
        try:
            return p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            return -9


def seg_rows(path: Path):
    j = json.loads(path.read_text(encoding="utf-8"))
    return [tuple(x for x in r.split("+") if x) for r in j["rows"]]


def solve_s1(wait: int, tag: str, extra):
    """Stage 1 from power-on. title_wait 0/1/37: the verified rule v2 lists logs/s1/s1_w<k>v3_full.inputs.txt (not
    re-solved). Any other wait: tools/s1_open.py makes the opening and states/s1/pre_w<k>, then contra.stages.s1
    solves the stage; the list = opening (fresh-launch form) + segment, ending ON stage 2's first frame."""
    fixed = LOGS_DIR / "s1" / f"s1_w{wait}v3_full.inputs.txt"
    if wait in (0, 1, 37) and fixed.exists():
        return read_inputs(fixed), {"solver": f"existing verified rule v2 result {fixed.relative_to(HERE)} (not re-solved)"}
    t0 = time.time()
    op = LOGS_DIR / "s1" / f"open_w{wait}.inputs.txt"
    if not (op.exists() and (STATES_DIR / "s1" / f"pre_w{wait}.State").exists()):
        rc = run_proc([sys.executable, "-u", "tools/s1_open.py", str(wait)], f"s1_open_w{wait}.out", timeout=1800)
        if rc != 0 or not op.exists():
            raise RuntimeError(f"stage 1 opening for title_wait {wait} failed (exit {rc})")
    out = f"w{wait}_{tag}"
    seg = LOGS_DIR / "s1" / f"{out}.seg.json"
    if seg.exists():
        os.replace(seg, seg.with_name(seg.name + ".old"))
    rc = run_proc([sys.executable, "-u", "-m", "contra.stages.s1", f"s1/pre_w{wait}", out, "--open", op] + list(extra),
                  f"s1_{tag}_solve.out")
    if rc != 0 or not seg.exists():
        raise RuntimeError(f"stage 1 solver failed (exit {rc}, segment written: {seg.exists()})")
    opening = read_inputs(op)
    assert opening[0] == (), "open_w<k> is the core-reboot form: its first row must be empty"
    rows = seg_rows(seg)                      # rows[0] produces L1, the last one stage 2's first frame
    return list(opening[1:]) + rows, {"solver": f"contra.stages.s1 s1/pre_w{wait} {out}", "solver_frames": len(rows) - 1,
                                      "solver_secs": round(time.time() - t0), "opening_rows": len(opening) - 1}


def solve_base(k, prev, tag, extra):
    """Stages 2 and 4. Starts ON the stage's first frame; rows run to the next stage's first frame inclusive."""
    hist = _hist_file(k, prev, tag, upto=len(prev))
    cmd = [sys.executable, "-u", "tools/s2_solve.py", k, f"{CHAIN}/s{k}_start", tag, "--hist", hist, "--states",
           f"{tag}_s{k}"]
    rc = run_proc(cmd + list(extra), f"s{k}_{tag}_solve.out")
    rep = LOGS_DIR / f"s{k}" / f"{tag}_report.json"
    rj = json.loads(rep.read_text(encoding="utf-8")) if rep.exists() else {}
    if rc != 0 or not rj.get("ok"):
        raise RuntimeError(f"stage {k} solver failed (exit {rc}, ok={rj.get('ok')}); see logs/chain/{CHAIN}/s{k}_{tag}_solve.out")
    rows = [tuple(r) for r in json.loads((LOGS_DIR / f"s{k}" / f"{tag}_rows.json").read_text())]
    return prev + rows, {"solver_frames": rj.get("frames"), "solver_secs": rj.get("secs"),
                         "solver_report": {x: rj.get(x) for x in ("frames", "boss", "lag")}}


def _hist_file(k, prev, tag, upto) -> Path:
    p = runs_dir() / f"prior_s{k}_{tag}.inputs.txt"
    write_inputs(p, prev[:upto], f"rows from power-on before the solver's first own row (stage {k})")
    return p


def _prior_file(k, prev, tag) -> Path:
    """The real rows before the solver's first own row (pre-state solvers replace the row that produces L)."""
    return _hist_file(k, prev, tag, upto=len(prev) - 1)


def solve_s3(k, prev, tag, extra):
    prior = _prior_file(k, prev, tag)
    rc = run_proc([sys.executable, "-u", "-m", "contra.stages.s3", f"{CHAIN}/s3_pre", "--out", f"s3/{tag}", "--prior", prior]
                  + list(extra), f"s3_{tag}_solve.out")
    seg = LOGS_DIR / "s3" / f"{tag}.seg.json"
    rep = LOGS_DIR / "s3" / f"{tag}.report.json"
    if rc != 0 or not seg.exists() or not rep.exists():
        raise RuntimeError(f"stage 3 solver failed (exit {rc}); see logs/chain/{CHAIN}/s3_{tag}_solve.out")
    rj = json.loads(rep.read_text(encoding="utf-8"))
    if seg.stat().st_mtime < prior.stat().st_mtime:
        raise RuntimeError("stage 3: the segment file is older than this attempt")
    rows = seg_rows(seg)
    base = prev[:-1] + rows                       # rows[0] produces L3, the last one the frame before L4
    return base + legal_filler(base), {"solver_frames": len(rows), "solver_secs": rj.get("wall_seconds"),
                                       "solver_report": {x: rj.get(x) for x in ("events", "deaths", "weapon_out",
                                                                                "next_first_frame_ok",
                                                                                "input_rule_violations")}}


def solve_s5(k, prev, tag, extra):
    prior = _prior_file(k, prev, tag)
    seg = LOGS_DIR / "s5" / f"{tag}.seg.json"
    if seg.exists():
        os.replace(seg, seg.with_name(seg.name + ".old"))
    t0 = time.time()
    rc = run_proc([sys.executable, "-u", "-m", "contra.stages.s5", f"{CHAIN}/s5_pre", tag, "--history", prior] + list(extra),
                  f"s5_{tag}_solve.out")
    if rc != 0 or not seg.exists():
        raise RuntimeError(f"stage 5 solver failed (exit {rc}, segment written: {seg.exists()}); "
                           f"see logs/chain/{CHAIN}/s5_{tag}_solve.out")
    rows = seg_rows(seg)                          # rows[0] produces L5, the last one L6
    return prev[:-1] + rows, {"solver_frames": len(rows) - 1, "solver_secs": round(time.time() - t0)}


def solve_s67(k, prev, tag, extra):
    prior = _prior_file(k, prev, tag)
    outj = runs_dir() / f"s{k}_{tag}_rows.json"
    if outj.exists():
        os.replace(outj, outj.with_name(outj.name + ".old"))
    rc = run_proc([sys.executable, "-u", "run_s67.py", k, f"{CHAIN}/s{k}_pre", tag, prior, outj] + list(extra),
                  f"s{k}_{tag}_solve.out")
    if rc != 0 or not outj.exists():
        raise RuntimeError(f"stage {k} solver failed (exit {rc}); see logs/chain/{CHAIN}/s{k}_{tag}_solve.out")
    j = json.loads(outj.read_text(encoding="utf-8"))
    if not j.get("ok"):
        raise RuntimeError(f"stage {k} solver did not finish: {j.get('result')}; see logs/chain/{CHAIN}/s{k}_{tag}_solve.out")
    rows = [tuple(r) for r in j["rows"]]          # rows[0] produces L, the last one the frame before the next L
    base = prev[:-1] + rows
    return base + legal_filler(base), {"solver_frames": len(rows), "solver_secs": j.get("seconds"),
                                       "solver_report": {x: j.get(x) for x in ("verified", "lag", "deaths", "trials",
                                                                               "check_inputs", "weapon_out",
                                                                               "lives_out", "start_fc")}}


def solve_s8(k, prev, tag, extra):
    prior = _prior_file(k, prev, tag)
    rc = run_proc([sys.executable, "-u", "-m", "contra.stages.s8", f"{CHAIN}/s8_pre", "--out", f"s8/{tag}", "--prior", prior]
                  + list(extra), f"s8_{tag}_solve.out")
    seg = LOGS_DIR / "s8" / f"{tag}.seg.json"
    rep = LOGS_DIR / "s8" / f"{tag}.report.json"
    if rc != 0 or not seg.exists() or not rep.exists() or seg.stat().st_mtime < prior.stat().st_mtime:
        raise RuntimeError(f"stage 8 solver failed (exit {rc}); see logs/chain/{CHAIN}/s8_{tag}_solve.out")
    rj = json.loads(rep.read_text(encoding="utf-8"))
    rows = seg_rows(seg)                          # rows[0] produces L8, the last one the END frame P
    base = prev[:-1] + rows
    # tail: keep Down two more frames, then nothing (the END is seen on P + 1; the tail is not timed)
    p = Pad.from_rows(base[-2000:])
    tail = []
    for n in range(60):
        r = p.fix(("Down",) if n < 2 and "Down" in base[-1] else ())
        p.push(r)
        tail.append(r)
    return base + tail, {"solver_frames": len(rows) - 1, "solver_secs": rj.get("wall_seconds"), "tail_rows": len(tail),
                         "solver_report": {x: rj.get(x) for x in ("events", "frames_L_to_END", "verify",
                                                                  "up_or_down_held_at_A", "input_rule_violations")}}


ADAPTERS = {2: solve_base, 3: solve_s3, 4: solve_base, 5: solve_s5, 6: solve_s67, 7: solve_s67, 8: solve_s8}


# ---------------------------------------------------------------------------------------- the end of the run
def verify_end(rows, tag: str) -> dict:
    """Replay the whole run from power-on on a fresh emulator: START / END by contra/clock.py, deaths, stages."""
    t0 = time.time()
    e = BizHawk(log_name=f"chain/{CHAIN}/verify_{tag}_end.log", fields=FIELDS)
    try:
        e.trace(True)
        e.run(rows)
        tr = list(e.last_trace)
        ram_sha1 = hashlib.sha1(e.ram_all()).hexdigest()
    finally:
        e.close()
    m = clock.measure(tr)
    firsts = stage_firsts(tr)
    deaths = find_deaths(tr)
    out = {"rows": len(rows), "ram_sha1": ram_sha1, "deaths": deaths, "clock": m, **_facts(tr, firsts),
           "seconds": round(time.time() - t0)}
    why = []
    if not m.get("finished"):
        why.append(f"the END event never comes (clock: start {m.get('start')}, end {m.get('end')}); last frame "
                   f"level {tr[-1]['level']} $2C {tr[-1]['lroutine']}")
    else:
        P = m["end"]["ram"]
        out["lag_at_end"] = next(s["lag"] for s in tr if s["frame"] == P)
        if not m["end"]["up_or_down_held"]:
            why.append("Up/Down was not held when control was lost")
        if m["end"]["ram"] != m["end"]["control_lost"] + 1:
            why.append(f"END P = {m['end']['ram']} is not A + 1 (A = {m['end']['control_lost']}): Bill was airborne")
    if deaths:
        why.append(f"deaths on frames {deaths[:5]}")
    out["ok"] = not why
    out["why"] = why
    return out


# ---------------------------------------------------------------------------------------- table
def table(st: dict) -> str:
    lines = [f"chain {CHAIN}, title_wait {st.get('wait')}",
             "| stage | first frame | ours (frames) | record | ours - record | chain1 | ours - chain1 | lag frames | "
             "cumulative at the stage's start (ours, from START) | record's | ahead (+) / behind (-) | "
             "$1A / $34 / lives at the first frame |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    N = None
    tot = 0
    for k in range(1, 9):
        s = st["stages"].get(str(k))
        if not s or s.get("status") != "verified":
            break
        if k == 1:
            N = s["L"]
        cum = s["L"] - N
        tot += s["segment"]
        rec_cum = RECORD_CUM_END[k - 1] if k > 1 else 0
        lines.append(f"| {k} | {s['L']} | {s['segment']} | {RECORD[k]} | {s['segment'] - RECORD[k]:+d} | {CHAIN1[k]} | "
                     f"{s['segment'] - CHAIN1[k]:+d} | {s['lag']} | {cum} | {rec_cum} | {rec_cum - cum:+d} | "
                     f"{s.get('fc')} / {s.get('rng')} / {s.get('lives')} |")
    lines.append(f"total so far: {tot} frames = {tot / clock.NES_FPS:.3f} s")
    return "\n".join(lines)


# ---------------------------------------------------------------------------------------- main
def main():
    global CHAIN
    a = sys.argv[1:]

    def opt(name, default=None):
        if name in a:
            i = a.index(name)
            v = a[i + 1]
            del a[i:i + 2]
            return v
        return default
    CHAIN = opt("--chain", "A")
    frm = int(opt("--from", 0))
    to = int(opt("--to", 8))
    tag = opt("--tag", f"c2{CHAIN}")
    wait = opt("--wait")
    extra = {}
    while "--extra" in a:
        i = a.index("--extra")
        extra[int(a[i + 1])] = a[i + 2].split()
        del a[i:i + 3]
    st = load_state()
    if "--table" in a:
        print(table(st))
        return
    if wait is None:
        wait = st.get("wait", 0)
    wait = int(wait)
    if st.get("wait") is not None and st["wait"] != wait and str(1) in st["stages"]:
        sys.exit(f"chain {CHAIN} was made with title_wait {st['wait']}; use another --chain name")
    st["wait"] = wait
    runs_dir().mkdir(parents=True, exist_ok=True)
    if frm:
        for k in range(frm, 9):
            if str(k) in st["stages"]:
                st.setdefault("discarded", []).append({"stage": k, "when": time.strftime("%Y-%m-%d %H:%M:%S"),
                                                       "was": st["stages"].pop(str(k))})
    write_json(state_file(), st)
    t_chain = time.time()
    for k in range(1, to + 1):
        cur = st["stages"].get(str(k))
        if cur and cur.get("status") == "verified":
            continue
        log(f"=== stage {k} (tag {tag}, title_wait {wait}) ===")
        t0 = time.time()
        if k == 1:
            prev_sha = "power-on"
        else:
            prev = read_inputs(through_path(k - 1))
            prev_sha = rows_sha1(prev)
            assert prev_sha == st["stages"][str(k - 1)]["through_sha1"], "through file changed on disk"
        solved = runs_dir() / f"s{k}_{tag}.solved.json"
        if solved.exists() and json.loads(solved.read_text())["prev_sha1"] == prev_sha:
            j = json.loads(solved.read_text())
            new, info = [tuple(r) for r in j["rows"]], j["info"]
            log(f"   re-using the finished solve {solved.name}")
        else:
            try:
                if k == 1:
                    new, info = solve_s1(wait, tag, extra.get(1, []))
                else:
                    new, info = ADAPTERS[k](k, prev, tag, extra.get(k, []))
            except Exception as ex:  # noqa: BLE001
                st["stages"][str(k)] = {"status": "solver_failed", "tag": tag, "why": str(ex),
                                        "secs": round(time.time() - t0)}
                write_json(state_file(), st)
                log(f"STAGE {k} SOLVER FAILED: {ex}")
                sys.exit(3)
            info["solve_wall_secs"] = round(time.time() - t0)
            write_json(solved, {"prev_sha1": prev_sha, "rows": [list(r) for r in new], "info": info})
        if k < 8:
            v = verify_prefix(new, k + 1, tag)
        else:
            v = verify_end(new, tag)
        rec = {"tag": tag, "info": info, "verify": v, "secs": round(time.time() - t0)}
        if not v["ok"]:
            rec["status"] = "verify_failed"
            st["stages"][str(k)] = rec
            write_json(state_file(), st)
            write_inputs(runs_dir() / f"FAILED_through_s{k}_{tag}.inputs.txt", new, f"stage {k} attempt {tag}: replay check failed")
            log(f"STAGE {k} REPLAY CHECK FAILED: {v['why']}")
            sys.exit(4)
        L = v["firsts"][str(k)]
        if k < 8:
            Ln = v["firsts"][str(k + 1)]
            lag = v["lag_at_first"][str(k + 1)] - v["lag_at_first"][str(k)]
        else:
            Ln = v["clock"]["end"]["ram"]
            lag = v["lag_at_end"] - v["lag_at_first"][str(k)]
        p = through_path(k) if k < 8 else runs_dir() / "run.inputs.txt"
        write_inputs(p, new, f"chain2 {CHAIN} (title_wait {wait}): power-on through stage {k}; row i (0-based) = "
                             f"emulator frame i + 2 of a fresh launch")
        ok_ci, ci = check_inputs(p)
        rec.update({"status": "verified", "L": L, "L_next": Ln, "segment": Ln - L, "record": RECORD[k],
                    "diff": Ln - L - RECORD[k], "lag": lag, "fc": v["fc_at_first"][str(k)],
                    "rng": v["rng_at_first"][str(k)], "lives": v["lives_at_first"][str(k)],
                    "weapon_in": v["weapon_at_first"][str(k)], "through": str(p.relative_to(HERE)),
                    "through_sha1": rows_sha1(new), "check_inputs": ci, "check_inputs_pass": ok_ci})
        if k < 8:
            rec["next_fc"] = v["fc_at_first"][str(k + 1)]
            rec["next_rng"] = v["rng_at_first"][str(k + 1)]
        st["stages"][str(k)] = rec
        write_json(state_file(), st)
        log(f"stage {k} VERIFIED from power-on: first frame {L}, next event frame {Ln}: segment {Ln - L} "
            f"(record {RECORD[k]}, {Ln - L - RECORD[k]:+d}; chain1 {CHAIN1[k]}), lag {lag}; in: $1A {rec['fc']} $34 "
            f"{rec['rng']} lives {rec['lives']}; next $1A {rec.get('next_fc')}; check_inputs on the prefix: {ci}; "
            f"{rec['secs']} s")
        if not ok_ci:
            log(f"   check_inputs FAILS on the prefix through stage {k}: stopping (find the cause)")
            sys.exit(5)
    log(f"chain pass finished in {time.time() - t_chain:.0f} s")
    print(table(st))


if __name__ == "__main__":
    main()
