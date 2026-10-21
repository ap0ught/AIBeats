"""Build knowledge/s7_phase_table.json (second pass) from the phase scan and the other verified solves.

    python tools/s7_phase_table.py

Inputs: logs/s7/scan/*.jsonl (tools/s7_phase_scan.py: one verified full solve per start phase),
logs/s7/*.seg.json (single solves), knowledge/s6_phase_table.json (stage 6, first builder).
"""
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REC7, REC6 = 4488, 4143
scan = []
seen_keys = set()
for p in sorted((ROOT / "logs" / "s7" / "scan").glob("*.jsonl")):
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            r = json.loads(line)
            r["scan_file"] = p.name
            if r.get("lead") and r.get("lead_seen") != r["lead"] and not r.get("name"):
                # first scan: the pause was put on row 0, where the game does not take Start. The solve is the
                # plain start of its state (ph<d>: fc 62 + d) with two ignored Start presses.
                d = int(r["state"].split("ph")[1])
                r["note"] = (f"asked for fc {r['fc']} by a {r['lead']}-frame pause on row 0, which the game ignored: "
                             f"this is the plain start fc {62 + d}")
                r["fc"], r["frames"], r["lead"] = 62 + d, r["rows"], 0
            key = (r.get("name"), r["fc"], r["state"], r.get("lead"), r.get("rows"))
            if key in seen_keys:
                continue                      # the same deterministic solve run twice
            seen_keys.add(key)
            scan.append(r)


def slim(r):
    pr = r.get("procs") or {}
    return {"start_fc": r["fc"], "start_phase_mod128": None if r["fc"] is None else r["fc"] & 127,
            "frames": r["frames"], "vs_record": None if r["frames"] is None else r["frames"] - REC7,
            "lag": r.get("lag"), "ok": r.get("ok"), "verified": r.get("verified"),
            "check_inputs": r.get("check_inputs"), "state": r.get("state"), "lead_pause": r.get("lead"),
            "real_start": not r.get("lead"), "result": r.get("result"), "deaths_repaired": r.get("deaths"),
            "remedies": r.get("remedies"), "local_beam_fixes": r.get("local_fixes"),
            "claw_corridor": {k: (pr.get("precart") or {}).get(k) for k in ("cost", "wait", "pauses")},
            "trio_rows": (pr.get("trio") or {}).get("rows"), "door_rows": (pr.get("boss") or {}).get("rows"),
            "marks": r.get("marks"), "stage8_start_fc": r.get("next_fc"), "name": r.get("name"),
            "note": r.get("note"), "scan_file": r.get("scan_file"), "solve_seconds": r.get("seconds")}


FINAL = ("F1.jsonl", "F2.jsonl", "F3.jsonl", "final.jsonl")
srt = lambda r: (r["start_phase_mod128"] if r["start_phase_mod128"] is not None else 999, r["start_fc"] or 0)  # noqa: E731
rows = sorted([slim(r) for r in scan if r["scan_file"] in FINAL], key=srt)        # final code: phases and chains
earlier = sorted([slim(r) for r in scan if r["scan_file"] not in FINAL], key=srt)
others = [r for r in rows if r["name"]]
others_earlier = [r for r in earlier if r["name"]]
good = [r for r in rows if r["ok"] and r["verified"] and str(r["check_inputs"]).endswith("PASS")]
by_phase = {}
for r in good:
    k = r["start_phase_mod128"]
    if k not in by_phase or r["frames"] < by_phase[k]["frames"]:
        by_phase[k] = r

singles = []
for p in sorted((ROOT / "logs" / "s7").glob("*.seg.json")):
    d = json.loads(p.read_text())
    if p.name.startswith("scan_"):
        continue
    singles.append({"name": p.name[:-9], "state": d.get("state"), "start_fc": d.get("start_fc"),
                    "frames": d.get("frames") if d.get("ok") else None, "lag": d.get("lag"),
                    "verified": d.get("verified"), "check_inputs": d.get("check_inputs"),
                    "second_pass": bool(d.get("procs")) or p.name.startswith(("n4", "n5", "chain66b", "c7_"))})


def t7(phase):
    """Stage 7 frames at a start phase: nearest scanned phase (circular mod 128). Returns (frames, scanned phase)."""
    if not by_phase:
        return None, None
    k = min(by_phase, key=lambda q: min((q - phase) % 128, (phase - q) % 128))
    return by_phase[k]["frames"], k


pair = None
s6p = ROOT / "knowledge" / "s6_phase_table.json"
if s6p.exists() and by_phase:
    s6 = json.loads(s6p.read_text())
    lag6 = 15
    tab = []
    for x in s6["table"]:
        for luck in ("best", "median"):
            n6 = x[f"predicted_segment_{luck}_luck"]
            ph7 = (x["start_phase"] + n6 - lag6) % 128
            n7, near = t7(ph7)
            tab.append({"s6_start_phase": x["start_phase"], "s6_luck": luck, "s6_frames": n6, "s7_start_phase": ph7,
                        "s7_frames_nearest_scanned": n7, "s7_scanned_phase_used": near, "sum": n6 + n7,
                        "vs_record_pair": n6 + n7 - REC6 - REC7})
    best_luck = sorted([t for t in tab if t["s6_luck"] == "best"], key=lambda t: t["sum"])
    med_luck = sorted([t for t in tab if t["s6_luck"] == "median"], key=lambda t: t["sum"])
    def chain_list(src):
        out_c = []
        for r in src:
            if r["state"] and r["state"].startswith("s6/") and r["frames"]:
                n6 = next((f for f in s6["full_solves"] if r["state"] == f"s6/{f['name']}_end"), None)
                out_c.append({"s6_run": n6["name"] if n6 else r["state"], "s6_start_fc": n6["start_fc"] if n6 else None,
                              "s6_frames": n6["frames"] if n6 else None, "s7_run": r["name"],
                              "s7_start_fc": r["start_fc"], "s7_frames": r["frames"], "s7_lag": r["lag"],
                              "s7_verified": r["verified"], "sum": (n6["frames"] + r["frames"]) if n6 else None,
                              "vs_record_pair": (n6["frames"] + r["frames"] - REC6 - REC7) if n6 else None})
        return sorted(out_c, key=lambda c: (c["sum"] is None, c["sum"]))

    chains = chain_list(others)
    pair = {
        "rule": "stage 7's $1A on its first frame = stage 6's $1A on its first frame + stage 6's segment length - "
                "the lag frames inside stage 6's segment (mod 256; 13 of them are in the load, 14-22 measured in "
                "total: 15 is used below). With the Barrier route stage 7 should depend on $1A mod 128 only; the "
                "measured 128-apart pairs (period_check) differ by 10-31 frames through random soldiers (claw "
                "corridor plan, lag), so read every stage 7 number as +-15.",
        "record_pair_frames": REC6 + REC7,
        "measured_chains": chains,
        "measured_chains_earlier_code": chain_list(others_earlier),
        "predicted_best_pairs_best_luck_stage6": best_luck[:8],
        "predicted_best_pairs_median_luck_stage6": med_luck[:8],
        "predicted_worst_pair_best_luck": best_luck[-1] if best_luck else None,
        "caveat": "predicted = stage 6 table (cluster scan + measured prefix/suffix, first builder) + stage 7 at "
                  "the NEAREST scanned phase (the scan step is 8; stage 7 changes by tens of frames between "
                  "neighbouring phases, so a predicted pair is good to about +/-20 frames). Only measured_chains "
                  "are real: stage 7 solved from the state a stage 6 segment ends in.",
    }

frames = [r["frames"] for r in by_phase.values()]
per = []
for r in good:
    tw = [q for q in good if q is not r and q["start_fc"] is not None and r["start_fc"] is not None
          and (q["start_fc"] - r["start_fc"]) % 256 == 128]
    for q in tw:
        if r["start_fc"] < q["start_fc"]:
            per.append({"fc": r["start_fc"], "frames": r["frames"], "fc_plus_128": q["start_fc"], "frames_plus_128": q["frames"]})
out = {
    "_about": "Stage 7 (Hangar), SECOND PASS (Barrier route). Segment length as a function of the global frame "
              "counter $1A on the stage's first playable frame. Every row is one full solve by contra/stages/s7.py "
              "from a debug start state, replayed open-loop twice (identical, no death, weapon $13 out) and "
              "checked with check_inputs.py. real_start = no leading pause (title-screen delay state ph<d>, the "
              "end state of a stage 6 solve, or the integrator's real run state real_c1_s7_pre); otherwise the "
              "phase was set by a pause of lead_pause frames on row 40 (not counted in frames; checked: ph80 + 10 "
              "reproduces ph90's marks to within one frame). 'table' = solves with the FINAL code. Made by "
              "tools/s7_phase_table.py from tools/s7_phase_scan.py / s7_j_solve1.py runs.",
    "record_segment_frames": REC7,
    "scanned_phases": len(by_phase),
    "best": min(good, key=lambda r: r["frames"]) if good else None,
    "worst": max(good, key=lambda r: r["frames"]) if good else None,
    "median_frames": statistics.median(frames) if frames else None,
    "mean_frames": round(statistics.mean(frames), 1) if frames else None,
    "phases_beating_the_record": sum(1 for f in frames if f < REC7),
    "period_check": per,
    "lead_pause_method_check": [r for r in rows if r.get("state") and r["lead_pause"] and r["start_fc"] is not None
                                and 62 <= r["start_fc"] <= 162],
    "table": rows,
    "solves_with_earlier_code_versions_of_the_second_pass": earlier,
    "single_solves": singles,
    "pairing_with_stage_6": pair,
    "what_depends_on_the_phase": {
        "global_timer_claws": "x 310..438 (screen 1, lower route), 742/758, 1270..1398 (the corridor before the "
                              "cart: 0 to 15 frames), 3014..3094 (six long claws: 5 to 10 frames): drop when "
                              "$1A & $7F == trigger; a 5-frame pause over the trigger frame deletes the drop",
        "seeking_claws_heartbreak_alley": "no longer matter: Bill is invincible there (Barrier)",
        "random": "soldiers and their bullets (the random number is advanced by the idle loop): one solve lost "
                  "33 frames to a jump into a hanging wall before the remedy cost check was added",
    },
}
p = ROOT / "knowledge" / "s7_phase_table.json"
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(json.dumps(out, indent=1), encoding="utf-8")
tmp.replace(p)
print("phase  fc   frames  vs rec  lag  corridor  state lead")
for r in rows:
    print(f"{str(r['start_phase_mod128']):>5} {str(r['start_fc']):>4} {str(r['frames']):>7} {str(r['vs_record']):>6} "
          f"{str(r['lag']):>4}  {str(r['claw_corridor']['cost']):>4}     {r['state']} {r['lead_pause']} "
          f"{'OK' if (r['ok'] and r['verified']) else 'FAILED: ' + str(r['result'])}")
print("earlier code versions:", [(r["start_fc"], r["frames"], r["name"]) for r in earlier])
if frames:
    print("best", min(frames), "median", statistics.median(frames), "worst", max(frames), "of", len(frames), "phases")
if pair:
    print("measured chains:", pair["measured_chains"])
    print("best predicted pairs (best luck):", [(t["s6_start_phase"], t["s6_frames"], t["s7_start_phase"], t["s7_frames_nearest_scanned"], t["sum"]) for t in pair["predicted_best_pairs_best_luck_stage6"][:5]])
