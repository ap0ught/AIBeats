"""Per-stage numbers from stage fits (logs/<dir>/mars_s<k>.seg.json or any seg.json): frames, lag, boss, exit.

    python tools/dbg_stage_report.py <stage>:<state>:<seg.json> [...]   -> logs/dbg/stage_report.json

For each: load the state (one frame before the stage's first playable frame L), play the fitted rows, then nothing
until the next stage's first playable frame (or the ending). All numbers are frames relative to L:
    boss_defeated   $3B first 1          control_lost   $2C first 9 (A)
    level_change    $30 changes          next_L         next stage's first frame with $2C == 4
    lag_in_level / lag_in_transition     BizHawk lag-counter differences
    ignored         play frames on which the game's controller byte differed from what was sent
Stage 8: end_ram (P) and end_seen from contra/clock.py.
States made by tools/mk_stage_state.py are DEBUG states (stage and weapon written into RAM at the start of the game):
these are per-stage facts about a fitted TAS movie, not a run.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra import clock  # noqa: E402
from contra.emulator import BizHawk, LOGS_DIR  # noqa: E402
from contra.inputs import to_mask  # noqa: E402

F = dict(clock.FIELDS)
F.update({"lives": 0x32, "death": 0xB4, "screen": 0x64, "scroll": 0x65, "weapon": 0xAA, "pause": 0x25, "loc": 0x40})
out = {}
with BizHawk(log_name="dbg_stage_report.log", fields=F) as e:
    for spec in sys.argv[1:]:
        k, state, segp = spec.split(":", 2)
        k = int(k)
        seg = json.loads(Path(segp).read_text(encoding="utf-8"))
        if not seg.get("done"):
            out[k] = {"stage": k, "fitted": False, "edits": seg.get("edits")}
            print(f"stage {k}: NOT fitted")
            continue
        rows = [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
        e.load(state)
        s0 = e.state()
        e.trace(True)
        e.run(rows + [()] * 700)
        tr = e.last_trace
        e.trace(False)
        L = s0["frame"] + 1

        def first(cond, lo=0):
            return next((i for i in range(lo, len(tr)) if cond(tr[i])), None)
        ib = first(lambda s: s["bossdef"] == 1)
        ia = first(lambda s: s["lroutine"] == 9)
        ic = first(lambda s: s["level"] != k - 1)
        inx = first(lambda s: s["lroutine"] == 4 and s["level"] == k, ic or 0) if ic is not None else None
        deaths = sum(1 for i in range(1, len(tr)) if (tr[i]["death"] & 1) and not (tr[i - 1]["death"] & 1))
        ign = sum(1 for i, s in enumerate(tr[:len(rows)]) if not s["lagged"] and s["lroutine"] == 4 and s["pause"] == 0
                  and s["pad"] != to_mask(rows[i]))
        rooms = [i for i in range(1, ic or len(tr)) if tr[i]["screen"] != tr[i - 1]["screen"] and tr[i]["loc"] in (1, 0x80)]
        r = {"stage": k, "fitted": True, "state": state, "L": L, "rows": len(rows), "m": seg.get("m"),
             "edits": seg.get("edits"), "lost_presses_repeated": seg.get("lost_presses_repeated"),
             "weapon_at_start": tr[0]["weapon"], "weapon_at_end": tr[(ic or len(tr)) - 1]["weapon"],
             "boss_defeated": None if ib is None else ib, "control_lost_A": None if ia is None else ia,
             "level_change": None if ic is None else ic, "next_L": inx,
             "lag_in_level": (tr[ic]["lag"] if ic is not None else tr[-1]["lag"]) - s0["lag"],
             "lag_in_transition": None if inx is None else tr[inx]["lag"] - tr[ic]["lag"],
             "deaths": deaths, "ignored_controller_frames": ign, "pause_frames": sum(1 for s in tr[:len(rows)] if s["pause"]),
             "base_room_frames": rooms}
        if k == 8:
            en = clock.end_frame([dict(s, groutine=5, demo=0) for s in tr])
            if en:
                r["end_ram_P"] = en["ram"] - L
                r["end_seen"] = en["seen"] - L
                r["end_up_or_down_held"] = en["up_or_down_held"]
        out[k] = r
        print(f"stage {k}: L={L} boss defeated +{ib} control lost +{ia} level change +{ic} next stage +{inx} "
              f"lag {r['lag_in_level']}+{r['lag_in_transition']} deaths {deaths} ignored {ign} "
              f"weapon ${r['weapon_at_start']:02x}->${r['weapon_at_end']:02x} edits {len(seg.get('edits', []))}"
              + (f" END ram +{r.get('end_ram_P')} seen +{r.get('end_seen')}" if k == 8 else ""), flush=True)
p = LOGS_DIR / "dbg" / "stage_report.json"
old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
old.update({str(k): v for k, v in out.items()})
p.write_text(json.dumps(old, indent=1), encoding="utf-8")
