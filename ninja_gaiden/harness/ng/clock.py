"""The run clock (speedrun.com Ninja Gaiden NES Any%), defined on RAM and checked against the picture.
Evidence: knowledge/clock.md (screenshots shots/clock/, tools/clock_evidence.py).

Board rule (knowledge/rules_verbatim.md): "Timing starts when you gain control of Ryu." "Timing ends when the timer
reaches 000 after defeating the demon statue." The record's moderators timed the first video frame where Ryu is
visible in 1-1 to the first video frame showing TIMER-000 (knowledge/record_notes.md).

A "frame" is emu.framecount() after the frame was emulated; the RAM sample of frame f is RAM after frame f; the
picture of frame f is the screenshot taken after frame f (it shows the sprites in PPU OAM after frame f).

    START: N = first frame with $33 == $97 in stage $6D == 0 (the main loop's first frame of 1-1: the timer $63
              drops from 150 to 149 and the sub-timer $62 starts). Ryu's sprites are in OAM / the picture of frame
              N + 1 (and not before)               -> START seen = N + 1.
    END:   P = first frame in stage $6D == 21 (6-5) with $63 == 0 during the final tally (the stack byte $1FD is
              $D5 there, the autosplitter's own condition; the boss HP display $66 is already 0 from the previous
              boss, so it cannot be used). The HUD redraws one of six status-bar parts per frame ($3E counts
              5..0); the timer digits are put in the PPU buffer ($0700 = 03 A9 20 d d d) on the frame whose RAM has
              $3E == 1 and reach the screen in the next frame's picture. So
              E = first frame > P with $3E == 1                      -> END seen = E + 1 (= P + 2..P + 7).
    time = (END seen - START seen) / 60.0988 s.
"""
from __future__ import annotations

from typing import Mapping, Optional, Sequence

NES_FPS = 60.0988
START_PICTURE_OFFSET = 1      # measured: tools/clock_evidence.py start (Ryu first drawn on N + 1)
HUD_TIMER_PHASE = 1           # $3E value of the frame that buffers the timer digits (measured, knowledge/clock.md)

FIELDS = {"ctl": 0x33, "stage": 0x6D, "timer": 0x63, "subtimer": 0x62, "bosshp": 0x66, "stk": 0x1FD, "hudphase": 0x3E}


def start_frame(tr: Sequence[Mapping[str, int]]) -> Optional[dict]:
    for s in tr:
        if s["stage"] == 0 and s["ctl"] == 0x97:
            return {"ram": s["frame"], "seen": s["frame"] + START_PICTURE_OFFSET}
    return None


def end_frame(tr: Sequence[Mapping[str, int]]) -> Optional[dict]:
    p = None
    for s in tr:
        if p is None:
            if s["stage"] == 21 and s["timer"] == 0 and s["stk"] == 0xD5:
                p = s["frame"]
            else:
                continue
        if "hudphase" not in s:
            return {"ram": p, "seen": None, "why": "no hudphase ($3E) in the trace"}
        if s["hudphase"] == HUD_TIMER_PHASE and s["frame"] > p:
            # strictly after P: in the tally loop the HUD buffer is built ($D5C3 JSR $F7FC) BEFORE the timer is
            # decremented ($D5EC JSR $D65A), so a phase-1 frame equal to P still buffers "001"
            return {"ram": p, "hud_buffer_frame": s["frame"], "seen": s["frame"] + 1}
    return {"ram": p, "seen": None, "why": "trace ends before the HUD shows 000"} if p else None


def fmt(seconds: float) -> str:
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"


def measure(tr) -> dict:
    tr = tr if isinstance(tr, list) else list(tr)
    st, en = start_frame(tr), end_frame(tr)
    out = {"start": st, "end": en, "finished": bool(st and en and en.get("seen"))}
    if out["finished"]:
        out["frames"] = en["seen"] - st["seen"]
        out["seconds"] = out["frames"] / NES_FPS
        out["time"] = fmt(out["seconds"])
        out["ram_frames"] = en["ram"] - st["ram"]
    return out
