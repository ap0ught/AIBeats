"""Stage 7: solve the stage from chosen start phases ($1A on the first playable frame) - second pass.

    python -u tools/s7_phase_scan.py <tag> <fc1,fc2,...|a-b:step> [--force-lead]

For every start phase fc: a start state and a full solve + open-loop replay check (tools/s6_solve.run), result
appended to logs/s7/scan/<tag>.jsonl and written to logs/s7/scan_<fc>.seg.json / .inputs.txt.

Start states. fc 62..162 are real starts made with the title-screen delay (tools/s6_mk_phase.make: states/s7/ph<d>,
fc = 62 + d). Every other fc is played from states/s7/ph100 (or ph95) with a pause of `lead` frames on the very
first frame (the frame counter runs during a pause, the game does not): the stage is then played as if it had
started `lead` frames later; the pause's frames are not counted ("frames" in the result = rows - lead).
--force-lead uses the pause method even where a real start exists (to check the method against real starts).
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from contra.stages.s6lib import Sim  # noqa: E402
import s6_solve  # noqa: E402
import s6_mk_phase  # noqa: E402


def start_for(fc, force_lead=False):
    """(d, lead) for a start phase."""
    fc &= 255
    if 62 <= fc <= 162 and not force_lead:
        return fc - 62, 0
    d = 100
    lead = (fc - 162) & 255
    if force_lead:
        d = max(0, min(100, fc - 62 - 10))
        lead = (fc - 62 - d) & 255
    if 0 < lead < 5:
        d -= 5
        lead += 5
    return d, lead


def main():
    tag = sys.argv[1]
    spec = sys.argv[2]
    force = "--force-lead" in sys.argv
    if ":" in spec:
        rng, step = spec.split(":")
        a, b = rng.split("-")
        fcs = list(range(int(a), int(b) + 1, int(step)))
    else:
        fcs = [x if x.startswith("state=") else int(x) for x in spec.split(",")]
    outp = ROOT / "logs" / "s7" / "scan"
    outp.mkdir(parents=True, exist_ok=True)
    with Sim(f"s7_scan_{tag}") as sim:
        for fc in fcs:
            if isinstance(fc, str):
                # "state=<savestate>=<out name>": a plain solve from that state (e.g. the state stage 6 ends in)
                _, st_name, out_name = fc.split("=")
                t0 = time.time()
                try:
                    res, rows = s6_solve.run(sim, 7, st_name, out_name, None, True,
                                             log=lambda *a: print(*a, flush=True))
                except Exception as ex:      # noqa: BLE001
                    res = {"ok": False, "result": f"exception {ex!r}"}
                rec = {"fc": res.get("start_fc"), "state": st_name, "lead": 0, "ok": res.get("ok"),
                       "verified": res.get("verified"), "frames": res.get("frames") if res.get("ok") else None,
                       "rows": res.get("frames"), "lag": res.get("lag"), "result": res.get("result"),
                       "check_inputs": res.get("check_inputs"), "deaths": res.get("deaths"),
                       "remedies": res.get("remedies"), "local_fixes": res.get("local_fixes"),
                       "marks": {m[0]: m[1] for m in res.get("marks", [])}, "procs": res.get("procs"),
                       "next_fc": (res.get("replay") or {}).get("next_frame", {}).get("fc"),
                       "seconds": round(time.time() - t0), "name": out_name}
                with open(outp / f"{tag}.jsonl", "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec) + "\n")
                print("RESULT", json.dumps({k: rec[k] for k in ("fc", "state", "ok", "verified", "frames", "lag",
                                                                 "check_inputs", "seconds")}), flush=True)
                continue
            d, lead = start_for(fc, force)
            st = ROOT / "states" / "s7" / f"ph{d}.State"
            if not st.exists():
                info = s6_mk_phase.make(sim.e, 7, d)
                print("made", info, flush=True)
                sim.e.trace(True)
            name = f"scan_{fc}" + ("L" if force else "")
            t0 = time.time()
            try:
                res, rows = s6_solve.run(sim, 7, f"s7/ph{d}", name, {"lead_pause": lead} if lead else None, True,
                                         log=lambda *a: print(*a, flush=True))
            except Exception as ex:      # noqa: BLE001
                res = {"ok": False, "result": f"exception {ex!r}"}
            rec = {"fc": fc, "state": f"s7/ph{d}", "lead": lead, "ok": res.get("ok"), "verified": res.get("verified"),
                   "frames": (res.get("frames") - lead) if res.get("ok") else None, "rows": res.get("frames"),
                   "lag": res.get("lag"), "start_fc_state": res.get("start_fc"), "result": res.get("result"),
                   "check_inputs": res.get("check_inputs"), "deaths": res.get("deaths"),
                   "remedies": res.get("remedies"), "local_fixes": res.get("local_fixes"),
                   "marks": {m[0]: m[1] for m in res.get("marks", [])}, "procs": res.get("procs"),
                   "next_fc": (res.get("replay") or {}).get("next_frame", {}).get("fc"),
                   "lead_seen": res.get("lead_pause_frames_seen"),
                   "seconds": round(time.time() - t0)}
            with open(outp / f"{tag}.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
            print("RESULT", json.dumps({k: rec[k] for k in ("fc", "state", "lead", "ok", "verified", "frames", "lag",
                                                             "check_inputs", "seconds")}), flush=True)


if __name__ == "__main__":
    main()
