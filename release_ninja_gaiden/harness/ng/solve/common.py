"""ng.solve.common - paths, stage names, TAS / record splits, input files, emulator opening.

Everything here is read-only over the existing data (logs/tas4751.*, knowledge/record_events.json).
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent.parent
LOGS = PROJECT / "logs"
STATES = PROJECT / "states"
KNOW = PROJECT / "knowledge"
ROM = PROJECT / "Ninja Gaiden (USA).nes"
STAGES_DIR = PROJECT / "ng" / "stages"          # no __init__.py on purpose (ng/stages.py must win `import ng.stages`)

for _p in (str(PROJECT), str(STAGES_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ng.inputs import read_inputs, write_inputs  # noqa: E402
from ng.stages import NAMES, FIRST_ROOM, BOSS  # noqa: E402

FPS = 60.0988


def stage_index(s) -> int:
    """'2-2' or 3 -> 3."""
    if isinstance(s, int):
        return s
    s = str(s)
    return int(s) if s.isdigit() else NAMES.index(s)


def rooms_of(stage) -> list[int]:
    i = stage_index(stage)
    lo = FIRST_ROOM[i]
    hi = FIRST_ROOM[i + 1] if i + 1 < len(FIRST_ROOM) else 48
    return list(range(lo, hi))


def stage_of_room(room: int) -> int:
    for i in range(len(FIRST_ROOM) - 1, -1, -1):
        if room >= FIRST_ROOM[i]:
            return i
    return 0


@lru_cache(None)
def tas_events() -> dict:
    return json.loads((LOGS / "tas4751.events.json").read_text())


def tas_control(stage) -> int:
    return tas_events()["stages"][stage_index(stage)]["control"]


def tas_split(stage) -> int:
    """TAS 4751M control -> next control (frames). Last stage: control -> END RAM 39,525."""
    i = stage_index(stage)
    if i >= 21:
        return 39525 - tas_control(21)
    return tas_control(i + 1) - tas_control(i)


@lru_cache(None)
def record_events() -> dict:
    return json.loads((KNOW / "record_events.json").read_text())


def record_control_cum(stage) -> float:
    """Record: NES frames from START (1-1 control) to this stage's control (estimate from the video)."""
    return record_events()["stages"][stage_index(stage)]["control_est_cum_nes"]


def record_split(stage) -> float:
    """Record control -> next control (NES frames). Last stage: control -> END (TIMER-000) of the record."""
    i = stage_index(stage)
    st = record_events()["stages"]
    if i + 1 < len(st):
        return round(st[i + 1]["control_est_cum_nes"] - st[i]["control_est_cum_nes"], 1)
    end = record_events().get("end", {})
    tot = end.get("cum_nes") or 41599
    return round(tot - st[i]["control_est_cum_nes"], 1)


def record_control_frame(stage) -> float:
    """The record's control of `stage` on OUR frame axis (power-on frame numbering, START = 1-1 control 174)."""
    return 174 + record_control_cum(stage)


def rows_of(path) -> list[tuple]:
    return [tuple(r) for r in read_inputs(str(path))]


def open_emu(log_name: str):
    """One EmuHawk through ng/emulator.py (hidden by hide_emus.py), as the act agents do."""
    from ng.emulator import BizHawk
    e = BizHawk(log_name=log_name)
    try:
        e.cmd("invis on")
    except Exception:
        pass
    return e


def abs_x(s) -> int:
    scr = s.get("scroll_scr", 0)
    if scr >= 128:
        scr -= 256
    return scr * 256 + s.get("scroll", 0) + s.get("x", 0)
