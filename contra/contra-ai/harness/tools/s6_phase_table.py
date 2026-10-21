"""Build knowledge/s6_phase_table.json from the tower-cluster scan and the full solves.

    python tools/s6_phase_table.py

Inputs (all written by the stage 6 tools):
  logs/s6/scan_cluster.json          C(phi): solver frames from the foot of tower 1 (world x 1300) to world x 1900
                                     for every phase phi = $1A & 127 on the frame Bill stands at x 1300
  logs/s6/scan_t2t3_noremedy.json    no-remedy pass/fail of towers 2 and 3 by phase at the foot of tower 2
  logs/s6/*.seg.json                 full solves from start states (debug state and title-delay phase states)
The table predicts, for every phase p = $1A & 127 on the stage's first playable frame,
    frames(p) = prefix + C((p + offset) & 127) + suffix
with prefix / offset / suffix taken from the verified full solves (the suffix - after the towers - has no
global-timer hazard; it varies a little with the random number, mostly at the boss).
"""
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs" / "s6"

scan = {int(k): v for k, v in json.loads((LOGS / "scan_cluster.json").read_text()).items()}
C = {ph: v["rows"] for ph, v in scan.items() if v["res"] == "done"}
BASE = 791                      # the cluster with no remedy at all (never possible: see notes)

runs = []
for p in sorted(LOGS.glob("*.seg.json")):
    d = json.loads(p.read_text())
    if not d.get("ok") or not d.get("verified"):
        continue
    m = {x[0]: x for x in d["marks"]}
    if "tower1" not in m or "t3_out" not in m:
        continue
    runs.append({"name": p.name[:-9], "state": d["state"], "start_fc": d["start_fc"], "frames": d["frames"],
                 "lag": d["lag"], "prefix": m["tower1"][1], "phase_at_tower1": m["tower1"][2] & 127,
                 "offset": (m["tower1"][2] - d["start_fc"]) & 127,
                 "cluster": m["t3_out"][1] - m["tower1"][1] + 8, "suffix": d["frames"] - (m["t3_out"][1] + 8),
                 "boss_kill_row": m.get("boss_killed", [0, 0])[1], "remedies": d["remedies"]})
cur = [r for r in runs if r["prefix"] <= 1272]            # runs made with the current route parameters
ref = cur or runs
prefix = statistics.median(r["prefix"] for r in ref)
offset = statistics.mode(r["offset"] for r in ref)
suffix_best = min(r["suffix"] for r in ref)
suffix_med = statistics.median(r["suffix"] for r in ref)

# wait-only estimate (no pause): windows of the three towers with no remedy, waiting on the floor / a ledge
W1 = set(range(92, 120))                                   # phase at x 1300 for which tower 1 passes untouched
nr = json.loads((LOGS / "scan_t2t3_noremedy.json").read_text())
W2 = {r["phase"] for r in nr if "ledge" in r["marks"]}     # phase at tower 1's exit for which tower 2 passes
W3 = {(r["phase"] + r["marks"]["ledge"]) & 127 for r in nr if r["res"] == "done"}   # phase on the ledge, tower 3
T1, T2, T3 = 305, 262, 216 + 8


def wait_to(ph, win):
    for w in [0] + list(range(2, 129)):
        if (ph + w) & 127 in win:
            return w
    return None


table = []
for p in range(128):
    phi = (p + offset) & 127
    c = C.get(phi)
    w1 = wait_to(phi, W1)
    ph2 = (phi + w1 + T1) & 127
    w2 = wait_to(ph2, W2)
    ph3 = (ph2 + w2 + T2) & 127
    w3 = wait_to(ph3, W3)
    table.append({"start_phase": p, "phase_at_tower1": phi,
                  "cluster_frames": c, "cluster_cost_over_791": None if c is None else c - BASE,
                  "predicted_segment_best_luck": None if c is None else int(prefix + c + suffix_best),
                  "predicted_segment_median_luck": None if c is None else int(prefix + c + suffix_med),
                  "remedies_in_cluster": scan[phi]["remedies"] if phi in scan else None,
                  "wait_only_estimate_cluster_cost": w1 + w2 + w3,
                  "pause_saves_estimate": None if c is None else (w1 + w2 + w3) - (c - BASE)})
done = [t for t in table if t["cluster_frames"] is not None]
best = min(done, key=lambda t: t["cluster_frames"])
worst = max(done, key=lambda t: t["cluster_frames"])
out = {
    "_about": "Stage 6 (Energy Zone): segment length as a function of the global frame counter $1A & 127 on the "
              "stage's first playable frame. cluster_frames = MEASURED solver time from world x 1300 to 1900 "
              "(three flame towers) at that phase (scan made from a checkpoint of a full solve with a leading "
              "pause to set the phase; the pause is not counted). predicted_segment = prefix + cluster + suffix "
              "from the verified full solves listed in 'full_solves' (suffix_best = luckiest boss seen, "
              "suffix_median = typical). wait_only_estimate = what the towers would cost with no pause at all, "
              "computed from the no-remedy windows (not played). Made by tools/s6_phase_table.py.",
    "record_segment_frames": 4143,
    "prefix_frames_to_x1300": prefix, "phase_offset_start_to_x1300": offset,
    "suffix_frames_after_x1900": {"best": suffix_best, "median": suffix_med},
    "cluster_no_remedy_frames": BASE,
    "phases_scanned": len(done),
    "best": best, "worst": worst,
    "typical_cluster_frames": statistics.median(t["cluster_frames"] for t in done),
    "no_remedy_windows": {"tower1_phase_at_x1300": sorted(W1), "tower2_phase_at_tower1_exit": sorted(W2),
                          "tower3_phase_on_ledge": sorted(W3)},
    "full_solves": runs,
    "table": table,
}
p = ROOT / "knowledge" / "s6_phase_table.json"
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(json.dumps(out, indent=1), encoding="utf-8")
tmp.replace(p)
print("phases scanned", len(done), "prefix", prefix, "offset", offset, "suffix best/median", suffix_best, suffix_med)
print("best", best["start_phase"], best["cluster_frames"], best["predicted_segment_best_luck"],
      "worst", worst["start_phase"], worst["cluster_frames"], worst["predicted_segment_best_luck"])
for r in runs:
    print(r["name"], r["start_fc"], r["frames"], "prefix", r["prefix"], "cluster", r["cluster"], "suffix", r["suffix"],
          "pred", int(r["prefix"] + C.get(r["phase_at_tower1"], 0) + r["suffix"]) if r["phase_at_tower1"] in C else None)
