"""Extra checks on runA trace and the input file: metronomic runs, barrier runs, pause context, lag in span,
heart-death to stand, title screen state. Writes vextra.out.json."""
import json
from pathlib import Path
H = Path(__file__).resolve().parent
T = (H / "runA" / "trace.bin").read_bytes(); REC = 2310; N = len(T) // REC
ram = lambda k: T[(k - 2) * REC + 6:(k - 2) * REC + 6 + 2048]
lag = lambda k: T[(k - 2) * REC + 4]
START, END = 594, 34509
rows = [frozenset(t for t in l.rstrip("\r").split("+") if t) for l in
        (H.parent / "chain2" / "run_chain2.inputs.txt").read_text(encoding="utf-8").split("\n")[1:-1]]
out = {}
for b in ("B", "Down", "Left", "Right", "Up", "A"):
    held = [b in r for r in rows]
    pr = [i + 2 for i in range(len(rows)) if held[i] and (i == 0 or not held[i - 1])]
    best = cur = 1; bs = be = None; s = pr[0] if pr else None
    for j in range(1, len(pr)):
        if pr[j] - pr[j - 1] == 5:
            cur += 1
            if cur > best: best, bs, be = cur, pr[j - cur + 1], pr[j]
        else:
            cur = 1
    sec = {}
    for p in pr:
        if START <= p < END:
            sec[(p - START) // 60] = sec.get((p - START) // 60, 0) + 1
    out[b] = {"presses": len(pr), "longest_run_of_5_frame_gaps_presses": best, "from": bs, "to": be,
              "seconds_with_11_or_12_presses_per_60f": sum(1 for v in sec.values() if v >= 11)}
runs = []; a = None
for k in range(3, N + 2):
    v = ram(k)[0xB0]
    if v and a is None: a = k
    if not v and a is not None: runs.append((a, k - 1, ram(a)[0x30])); a = None
out["barrier_b0_runs(frame_from,to,level)"] = runs
out["lag_in_START_to_END-1"] = sum(lag(k) for k in range(START, END))
out["lag_frames_list_in_span"] = [k for k in range(START, END) if lag(k)]
out["heart_3b_set_frame"] = next(k for k in range(34000, N + 1) if ram(k)[0x3B] == 1 and ram(k - 1)[0x3B] == 0 and ram(k)[0x30] == 7)
out["control_lost_2c_9_frame"] = next(k for k in range(34300, N + 1) if ram(k)[0x2C] == 9 and ram(k - 1)[0x2C] == 8)
out["title_frames_$22_mode"] = sorted({ram(k)[0x22] for k in range(3, 600)})
out["rows"] = len(rows); out["last_input_frame"] = max(i + 2 for i, r in enumerate(rows) if r)
out["paused_frames_by_start"] = [(k, sorted(rows[k - 2])) for k in range(START, END) if "Start" in rows[k - 2] and "Start" not in rows[k - 3]]
(H / "vextra.out.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for k, v in out.items():
    s = json.dumps(v); print(k, "=", s[:600])
