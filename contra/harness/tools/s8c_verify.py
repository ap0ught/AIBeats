"""Rule v2 verification of finished stage 8 / stage 3 segments: open-loop replay on a FRESH emulator, END by
contra/clock.py, check_inputs.py with the sustained windows on history + segment, press statistics.

    python tools/s8c_verify.py s8:<state>:<seg name under logs/>[:<prior inputs file, path from the project>] ...
    python tools/s8c_verify.py s3:<state>:<seg name>[:<prior>] ...

Writes logs/<seg name>.verify_v3.json and logs/<seg name>.withprior.inputs.txt (history tail + segment), prints one
block per segment. Nothing is poked.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from contra.stages.s3s8_engine import Engine, TR  # noqa: E402
from contra.stages.s3s8_lib import LOGS_DIR, check_rows, read_inputs, write_inputs, history_tail, WINDOWS  # noqa: E402
from contra.stages.s8 import press_report  # noqa: E402
from contra import clock  # noqa: E402

WSPEC = ",".join(f"{w}:{n}" for w, n in WINDOWS)

if __name__ == "__main__":
    fields = dict(TR)
    fields.update(clock.FIELDS)
    out_all = []
    with Engine(1, tag="s8", fields=fields) as eng:
        for spec in sys.argv[1:]:
            parts = spec.split(":")
            stage, state, name = parts[0], parts[1], parts[2]
            prior_all = read_inputs(ROOT / parts[3]) if len(parts) > 3 else []
            prior = history_tail(prior_all) if prior_all else []
            j = json.loads((LOGS_DIR / f"{name}.seg.json").read_text(encoding="utf-8"))
            rows = [tuple(x for x in r.split("+") if x) for r in j["rows"]]
            tr = eng.sim(eng.root(state), rows + [()] * 3)
            L = next(s["frame"] for s in tr if s["lroutine"] == 4)
            deaths = sum(1 for k in range(1, len(tr)) if (tr[k]["death"] & 1 and not tr[k - 1]["death"] & 1)
                         or (tr[k]["pstate"] == 2 and tr[k - 1]["pstate"] != 2))
            lag = [k for k, s in enumerate(tr[:len(rows)]) if s["lagged"]]
            bad = check_rows(rows, prior)
            both = LOGS_DIR / f"{name}.withprior.inputs.txt"
            write_inputs(both, list(prior) + rows, f"history_tail={len(prior)} segment={len(rows)}")
            c = subprocess.run([sys.executable, str(ROOT / "check_inputs.py"), str(both), "--windows", WSPEC],
                               capture_output=True, text=True)
            res = {"segment": name, "state": state, "rows": len(rows), "L_frame": L, "deaths": deaths,
                   "lag_rows": lag, "weapon_out": tr[min(len(tr) - 1, len(rows))]["weapon"],
                   "history_tail_rows": len(prior), "pad_violations": len(bad),
                   "check_inputs_cmd": f"python check_inputs.py {both.relative_to(ROOT)} --windows {WSPEC}",
                   "check_inputs_result": c.stdout.strip().splitlines()[-1] if c.stdout.strip() else f"exit {c.returncode}",
                   "check_inputs_exit": c.returncode}
            if stage == "s8":
                en = clock.end_frame(tr)
                res["END"] = en
                res["frames_L_to_END"] = None if en is None else en["ram"] - L
                a = next((k for k, s in enumerate(tr) if s["lroutine"] == 9), None)
                res["pad_at_control_loss"] = None if a is None else tr[a]["pad"]
                res["up_or_down_held_at_control_loss"] = None if a is None else bool(tr[a]["pad"] & 0x0C)
                ev = {}
                sp = next((k for k, s in enumerate(tr) if any(s[f"r{q}"] and s[f"t{q}"] == 0x10 for q in range(16))), None)
                ev["guardian_spawn"] = sp

                def ghp(s):
                    for q in range(16):
                        if s[f"r{q}"] and s[f"t{q}"] == 0x10:
                            return s[f"h{q}"]
                    return None
                ev["guardian_dead"] = next((k for k, s in enumerate(tr) if sp is not None and k > sp and ghp(s) == 0), None)
                ev["boss_scroll"] = next((k for k, s in enumerate(tr) if s["auto0"] > 0 and k > (ev["guardian_dead"] or 0)), None)
                ev["heart_dead_flag"] = next((k for k, s in enumerate(tr) if s["bossdef"] == 1), None)
                res["events_trace_index"] = ev
                res["presses"] = press_report(rows, tr, ev, prior)
                print(f"{name} from {state}: rows {len(rows)}, L frame {L}, END by clock.py {en}, frames L to END "
                      f"{res['frames_L_to_END']}; deaths {deaths}; lag {len(lag)} {lag}; weapon out ${res['weapon_out']:02x}; "
                      f"Up/Down at control loss {res['up_or_down_held_at_control_loss']}")
                pz = res["presses"]
                print(f"   B presses {pz['B_presses']}; most in any 60 / 600 / 1800 rows (history counted): "
                      f"{pz['B_max_in_60']} / {pz['B_max_in_600']} / {pz['B_max_in_1800']}")
                for sec, d in pz["sections"].items():
                    print(f"   {sec:15s} rows {d['rows'][0]:5d}..{d['rows'][1]:5d}: presses {d['presses']:3d}, pellets "
                          f"{d['pellets']:3d}, fired nothing {d['presses_that_fired_nothing']:3d}, lag {d['lag']}")
            else:
                k = next((i for i, s in enumerate(tr) if s["level"] == 3 and s["lroutine"] == 4), None)
                res["next_stage_first_frame_index"] = k
                res["next_ok"] = k == len(rows)
                st = [i for i, r in enumerate(rows) if "B" in r and (i == 0 or "B" not in rows[i - 1])]
                res["B_presses"] = len(st)
                print(f"{name} from {state}: rows {len(rows)}, L frame {L}, stage 4's first frame at trace index {k} "
                      f"(expected {len(rows)}); deaths {deaths}; lag {len(lag)}; weapon out ${res['weapon_out']:02x}; "
                      f"B presses {len(st)}")
            print(f"   history tail {len(prior)} rows; Pad violations {len(bad)}; {res['check_inputs_cmd']} -> "
                  f"{res['check_inputs_result']}")
            (LOGS_DIR / f"{name}.verify_v3.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
            out_all.append(res)
