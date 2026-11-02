"""Events of a traced run: stages, rooms, control, bosses, deaths, cutscenes, lag. Used by tools/events.py and
assemble.py. A trace is a list of mappings (one per frame) holding at least: frame, stage, room, ctl, timer,
subtimer, bosshp, lives, dead, pause, lagged and the ng.mode TICKS counters (gm, dw, bk, se, nx, cs, csskip).

Definitions (evidence in knowledge/ram_notes.md):
  load     first frame with a new $6D (stage) value
  control  first frame of the stage on which the play loop runs (gm > 0): always load + 151 in the TAS replay.
           In 1-1 this is also the first $33 == $97 frame (the autosplitter's start; $63 150 -> 149), but $33 is
           sprite data, not a flag: it is $9A at 6-4b and $9B at 6-5 control.
  room     first frame with a new $6E
  boss_hp_set first frame in a boss stage with $0497 (boss slot HP) > 0 after control ("boss reached")
  boss0    first frame in a boss stage with $66 (boss HP display) == 0 after control
  death    first frame of the game's death wait loop (dw > 0 after dw == 0)
  cutscene a run of frames on which the cinematic engine ran (cs > 0); skipped if the script-end code ($813E, bank 4)
           ran on a frame with Start held
  game lag a frame between control and the end of play in that stage on which the main loop did not start
           (gm == 0) while nothing else ran (no death / boss tally / stage end / cutscene) and the game is not paused
"""
from __future__ import annotations

from typing import Mapping, Sequence

from .stages import BOSS, name


def analyse(tr: Sequence[Mapping[str, int]]) -> dict:
    stages: list[dict] = []
    cur = None
    deaths, rooms, cutscenes, game_lag = [], [], [], []
    cs_run = None
    prev = None
    for i, s in enumerate(tr):
        if s["stage"] > 21:                   # power-on RAM ($FF) before the reset routine clears it
            continue
        f = s["frame"]
        if prev is None or s["stage"] != prev["stage"]:
            cur = {"stage": s["stage"], "name": name(s["stage"]), "load": f if prev is not None else None,
                   "first_frame_seen": f}
            stages.append(cur)
        if "control" not in cur and s.get("gm"):
            cur["control"] = f
            cur["timer_at_control"] = s["timer"]
            cur["lives_at_control"] = s["lives"]
            cur["lag_at_control"] = s["lag"]
        if prev is not None and s["room"] != prev["room"]:
            rooms.append({"frame": f, "stage": name(s["stage"]), "room": s["room"], "from": prev["room"]})
        if s["stage"] in BOSS and "control" in cur and "boss_hp_set" not in cur and s.get("boss_real", 0) > 0:
            cur["boss_hp_set"] = f              # boss slot 7 ($0497) gets its HP: the boss is there
        if s["stage"] in BOSS and "control" in cur and "boss0" not in cur and s["bosshp"] == 0:
            cur["boss0"] = f
        if s.get("dw") and not (prev or {}).get("dw"):
            deaths.append({"frame": f, "stage": name(s["stage"]), "room": s["room"], "lives_after": s["lives"]})
        if s.get("cs") or (cs_run is not None and s.get("csskip")):
            if cs_run is None:
                cs_run = {"first": f, "stage": name(s["stage"]), "skipped": False}
            cs_run["last"] = f
            if s.get("csskip") and (s.get("pad", 0) & 0x10):
                cs_run["skipped"] = True          # $813E also runs at a script's natural end: need Start held
        elif cs_run is not None and f - cs_run["last"] > 3:
            cutscenes.append(cs_run)
            cs_run = None
        if ("control" in cur and not s.get("gm") and not s.get("dw") and not s.get("bk") and not s.get("se")
                and not s.get("cs") and not s.get("nx") and not (s.get("pause", 0) & 0x80)
                and prev is not None and prev.get("gm") and s["stage"] == prev["stage"]):
            # the loop is late: count it only if play resumes within 3 frames (otherwise it is a transition)
            nxt = tr[i + 1:i + 4]
            if any(x.get("gm") for x in nxt):
                game_lag.append(f)
        prev = s
    if cs_run is not None:
        cutscenes.append(cs_run)
    for a, b in zip(stages, stages[1:]):
        if "control" in a and b.get("load"):
            a["control_to_next_load"] = b["load"] - a["control"]
        if "control" in a and "control" in b:
            a["control_to_next_control"] = b["control"] - a["control"]
    return {"stages": stages, "rooms": rooms, "deaths": deaths, "cutscenes": cutscenes,
            "game_lag_frames": len(game_lag), "game_lag_first": game_lag[:50],
            "bizhawk_lag_total": tr[-1]["lag"] if tr else 0, "frames": len(tr),
            "last": dict(tr[-1]) if tr else {}}
