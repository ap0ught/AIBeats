"""chain2: the proof and the report for the chosen run (as chain1's finish.py).

    python finish.py --chain X [--skip-shots]

0. copies runs/X/run.inputs.txt (the chain's verified whole run) to run_chain2.inputs.txt.
1. assemble.py (the snapshot's copy, unchanged): two fresh-launch replays from power-on in two emulators, RAM sha1 and
   per-frame trace sha1 must MATCH; START / END / RUN TIME by contra/clock.py; per-stage frames and lag.
2. check_inputs.py at its defaults (rule v2: 5-frame rule + 600:109 / 1,800:246 windows) on the full list.
3. clock_shots.py: screenshots and sprite memory around START and END (shots/clock/).
4. run_chain2.report.json + table.md: per stage against the record's segments and chain1; lag; pauses; B presses;
   the highest press counts of every button in any 60 / 600 / 1,800 frames.
Exit code 0 only if the replays match, check_inputs passes, the run finishes with no death and both clock events
are seen on the frame after their RAM frame.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chain  # noqa: E402
from chain import RECORD, RECORD_CUM_END, CHAIN1, write_json  # noqa: E402
from contra.inputs import read_inputs  # noqa: E402

RUN = HERE / "run_chain2.inputs.txt"
FPS = 60.0988
CHAIN1_CUM_START = {1: 0, 2: 3900, 3: 7504, 4: 11046, 5: 16315, 6: 22356, 7: 26406, 8: 31237}
BUTTONS = ("Up", "Down", "Left", "Right", "Select", "Start", "B", "A")


def fmt(sec):
    return f"{int(sec // 60)}:{sec % 60:06.3f}"


def press_starts(rows, b):
    out = []
    prev = False
    for i, r in enumerate(rows):
        h = b in r
        if h and not prev:
            out.append(i)
        prev = h
    return out


def max_in_window(starts, w):
    best, j = 0, 0
    for i in range(len(starts)):
        while starts[i] - starts[j] >= w:
            j += 1
        best = max(best, i - j + 1)
    return best


def main():
    a = sys.argv[1:]
    skip_shots = "--skip-shots" in a
    name = a[a.index("--chain") + 1] if "--chain" in a else "A"
    chain.CHAIN = name
    st = chain.load_state()
    src = chain.runs_dir() / "run.inputs.txt"
    assert st["stages"].get("8", {}).get("status") == "verified", f"chain {name} is not complete"
    assert chain.rows_sha1(read_inputs(src)) == st["stages"]["8"]["through_sha1"], "run file changed on disk"
    shutil.copyfile(src, RUN)
    rows = read_inputs(RUN)
    out = {"when": time.strftime("%Y-%m-%d %H:%M:%S"), "inputs": RUN.name, "chain": name, "title_wait": st.get("wait"),
           "source": str(src.relative_to(HERE))}
    t0 = time.time()
    a_ = subprocess.run([sys.executable, "assemble.py", "run_chain2", str(RUN)], cwd=str(HERE), capture_output=True, text=True)
    print(a_.stdout)
    print(a_.stderr[-2000:])
    out["assemble_exit_code"] = a_.returncode
    out["assemble_stdout"] = a_.stdout.strip().splitlines()
    out["assemble_seconds"] = round(time.time() - t0)
    rep = json.loads((HERE / "logs" / "run_chain2.report.json").read_text(encoding="utf-8"))
    out["replays_match"] = rep["replays_match"]
    for k in ("ram_sha1_a", "ram_sha1_b", "trace_sha1_a", "trace_sha1_b", "input_frames", "core", "deaths",
              "controller_ignored_frames", "lag_total", "start", "end", "finished", "time", "seconds", "frames_timed"):
        out[k] = rep.get(k)
    c = subprocess.run([sys.executable, "check_inputs.py", str(RUN), "--json", str(HERE / "run_chain2.check_inputs.json")],
                       cwd=str(HERE), capture_output=True, text=True)
    print(c.stdout)
    out["check_inputs_exit_code"] = c.returncode
    out["check_inputs_last_line"] = (c.stdout.strip().splitlines() or ["?"])[-1]
    out["check_inputs_stdout"] = c.stdout.strip().splitlines()
    if not skip_shots:
        s = subprocess.run([sys.executable, "clock_shots.py", str(RUN)], cwd=str(HERE), capture_output=True, text=True)
        print(s.stdout[-3000:])
        print(s.stderr[-2000:])
        out["clock_shots_exit_code"] = s.returncode
    ev = HERE / "clock_evidence.json"
    if ev.exists():
        out["clock_evidence_summary"] = json.loads(ev.read_text(encoding="utf-8"))["summary"]
    # presses: whole run, and in play (from START N); windows
    N = rep["start"]["ram"] if rep.get("start") else None
    P = rep["end"]["ram"] if rep.get("end") else None
    presses = {}
    for b in BUTTONS:
        s_ = press_starts(rows, b)
        presses[b] = {"presses": len(s_), "max_in_60": max_in_window(s_, 60), "max_in_600": max_in_window(s_, 600),
                      "max_in_1800": max_in_window(s_, 1800)}
    out["presses"] = presses
    # Start presses after START = pauses (each press pauses or unpauses); frame of row i = i + 2
    starts_in_play = [i + 2 for i in press_starts(rows, "Start") if N is not None and i + 2 > N]
    out["start_presses_in_play_frames"] = starts_in_play
    # per stage
    stage_rows = []
    lines = ["| stage | first frame | cumulative at its start (frames after START) | record's | ahead of the record at "
             "its start | segment, ours | record | ours - record | chain1 | ours - chain1 | lag frames | Start presses "
             "(pause / unpause) | B presses | $1A / $34 / lives at the first frame | solver wall time (s) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    firsts = {s["stage"]: s["first_frame"] for s in rep["stages"]}
    for s in rep["stages"]:
        k = s["stage"]
        cum = s["first_frame"] - N
        rc = RECORD_CUM_END[k - 1] if k > 1 else 0
        cs = st["stages"].get(str(k), {})
        secs = cs.get("info", {}).get("solve_wall_secs")
        f0 = s["first_frame"]
        f1 = firsts.get(k + 1, P)
        brs = [i for i in press_starts(rows, "B") if f0 <= i + 2 < f1]
        sps = [f for f in starts_in_play if f0 <= f < f1]
        r = {"stage": k, "first_frame": f0, "cum_start": cum, "record_cum_start": rc, "ahead_at_start": rc - cum,
             "segment": s["frames"], "record": RECORD[k], "diff": s["frames"] - RECORD[k], "chain1": CHAIN1[k],
             "diff_chain1": s["frames"] - CHAIN1[k], "lag": s["lag_frames"], "measured": s["measured"],
             "start_presses": len(sps), "b_presses": len(brs), "solver_wall_secs": secs, "chain_segment": cs.get("segment"),
             "weapon_at_start": s["weapon_at_start"], "fc": cs.get("fc"), "rng": cs.get("rng"), "lives": cs.get("lives")}
        stage_rows.append(r)
        lines.append(f"| {k} | {f0} | {cum} | {rc} | {rc - cum:+d} | {r['segment']} | {RECORD[k]} | {r['diff']:+d} | "
                     f"{CHAIN1[k]} | {r['diff_chain1']:+d} | {r['lag']} | {len(sps)} | {len(brs)} | "
                     f"{r['fc']} / {r['rng']} / {r['lives']} | {secs if secs is not None else '-'} |")
    if rep.get("finished"):
        tot = rep["frames_timed"]
        lines.append(f"| END | {rep['end']['ram']} (RAM), seen {rep['end']['seen']} | {tot} | {RECORD_CUM_END[8]} | "
                     f"{RECORD_CUM_END[8] - tot:+d} | **{tot}** | {RECORD_CUM_END[8]} | {tot - RECORD_CUM_END[8]:+d} | "
                     f"34474 | {tot - 34474:+d} | {rep['lag_total']} from power-on | {len(starts_in_play)} | "
                     f"{presses['B']['presses']} (whole list) | | |")
        out["run_frames"] = tot
        out["run_time"] = fmt(tot / FPS)
        out["record_board_9_48_183_frames"] = round(588.183 * FPS)
        out["time_to_clear_9_46_717_frames"] = 35261
        out["chain1_frames"] = 34474
    lines += ["", "Highest press counts of each button (whole list; a press = a row where the button is held and was "
              "not on the row before):", "", "| button | presses | most in any 60 frames | 600 (limit 109) | "
              "1,800 (limit 246) |", "|---|---|---|---|---|"]
    for b in BUTTONS:
        p = presses[b]
        lines.append(f"| {b} | {p['presses']} | {p['max_in_60']} | {p['max_in_600']} | {p['max_in_1800']} |")
    out["table"] = stage_rows
    out["chain_state"] = st
    (HERE / "table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    ok = (a_.returncode == 0 and rep["replays_match"] and rep.get("finished") and rep["deaths"] == 0 and c.returncode == 0
          and (skip_shots or (out.get("clock_evidence_summary", {}).get("start_ok")
                              and out.get("clock_evidence_summary", {}).get("end_ok"))))
    out["ALL_OK"] = bool(ok)
    write_json(HERE / "run_chain2.report.json", out)
    print("ALL_OK" if ok else "NOT OK", out.get("run_time"), out.get("run_frames"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
