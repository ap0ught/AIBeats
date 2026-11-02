"""Game mode from per-frame code-execution counters (the bridge's `tick`), proven in knowledge/ram_notes.md.

Ninja Gaiden has no single "game mode" byte: the mode is where the CPU is. Each name below counts how many times
one instruction ran during the frame; an address in the switchable $8000-$BFFF window carries the PRG bank that
must be mapped (RAM $5C, the game's copy of its bank number) for it to count.
"""
from __future__ import annotations

TICKS = {
    "gm": 0xC088,            # gameplay main loop: first instruction after the wait-for-NMI (one per game frame)
    "dw": 0xE40E,            # death: 190-frame wait loop after Ryu dies / time runs out
    "bk": 0xD5C0,            # boss killed: tally loop (boss kill indicator $04B8)
    "se": 0xD621,            # stage end: 10-frame wait before the stage-end cutscene / next stage
    "nx": 0xE8A8,            # next stage load ($6D += 1), once
    "cs": (0x80EC, 4),       # cinematic engine (bank 4) script loop (runs 1+ times a frame while a script plays)
    "csskip": (0x813E, 4),   # a script ends: Start was pressed (or its natural end; check Start held)
    "title": (0x80B0, 4),    # power-on flow: the opening (script 0) is over -> the title script $0D starts
    "act1": (0x80BA, 4),     # power-on flow: Start on the title -> the ACT I card script $0C starts
    "csdone": (0x80BD, 4),   # power-on flow: the ACT I card is over (skipped or not) -> the game starts
}


def mode(s) -> str:
    """One word for a traced State (needs the TICKS fields)."""
    if s.get("gm"):
        return "pause" if s.get("pause", 0) & 0x80 else "play"
    for k, name in (("dw", "death"), ("bk", "bosskill"), ("se", "stageend"), ("cs", "cinema"), ("nx", "load")):
        if s.get(k):
            return name
    return "other"
