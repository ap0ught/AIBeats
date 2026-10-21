"""The run clock, defined on RAM and cross-checked against the picture (knowledge/clock.md has the evidence).

Rule (speedrun.com, Contra NES, Any%): time starts "when the blue life medals appear" at the start of Stage 1 and
ends when, after the heart dies, "Bill automatically reverts to his normal position (standing while pointing his
gun forward)" while Up or Down is held.

A "frame" here is the emulator's frame counter value after the frame was emulated (emu.framecount()); the RAM
sample of frame f is RAM as it is after frame f; the picture of frame f is what the PPU drew during frame f.
The game builds its sprite list ($0200-$02FF) at the END of a frame's logic and copies it to the PPU at the START
of the next NMI, so a pose/sprite decided in the logic of frame f is first SEEN in the picture of frame f+1
(the next frame on which the NMI handler runs its full path, i.e. the next non-lag frame).

    start: N  = first frame whose RAM has LEVEL_ROUTINE_INDEX ($2C) == 4 with $18 == 5, $30 == 0, $1C == 0
                (the same frame sets SPRITE_LOAD_TYPE $6A = $FF and writes the medal sprites into $0200).
           START (as seen) = N + 1.
    end:   A  = first frame whose RAM has $2C == 9 with $30 == 7 (stage 8). On frame A the player still had
                control. Frame A + 1 is the first whose logic zeroes the controller; if Bill is on the ground
                its sprite list already holds the standing pose ($BC == 0).
           P  = first frame > A whose RAM has Bill standing, aiming forward, on the ground
                ($BC == 0, $A0 == 0, $C2 in (2, 7))  -> normally A + 1 (later only if he was airborne).
           END (as seen) = P + 1.

    time = (END_seen - START_seen) / 60.0988 seconds          (NTSC NES frame rate)

Both "seen" frames use the same +1, so the timed interval equals P - N frames.
"""
from __future__ import annotations

from typing import Iterable, Mapping, Optional

NES_FPS = 60.0988                     # 39375000 / 11 / 4 / 341 / 262 * 2 ... the usual NTSC NES figure (1789772.7272 / 29780.5)

# RAM bytes the clock needs (name -> address); add them to the bridge's field list before tracing
FIELDS = {"groutine": 0x18, "demo": 0x1C, "lroutine": 0x2C, "elr": 0x2D, "level": 0x30, "bossdef": 0x3B,
          "hud": 0x6A, "pstate": 0x90, "jump": 0xA0, "pseq": 0xBC, "aim": 0xC2, "psprite": 0xD6, "pad": 0xF1,
          "spr0": 0x300}

STAND_AIMS = (2, 7)                   # PLAYER_AIM_DIR: 2 = facing right, gun forward; 7 = facing left, gun forward


def _next_drawn(trace, i: int) -> Optional[int]:
    """Index of the first frame after trace[i] on which the NMI handler ran its full path (OAM was copied)."""
    for j in range(i + 1, len(trace)):
        if not trace[j].get("lagged", 0):
            return j
    return None


def start_frame(trace: Iterable[Mapping[str, int]]) -> Optional[dict]:
    """trace: one mapping per frame with at least frame, groutine, demo, lroutine, level (and lagged).
    Returns {"ram": N, "seen": N+1 (next drawn frame)} or None."""
    trace = trace if isinstance(trace, list) else list(trace)
    for i, s in enumerate(trace):
        if s["groutine"] == 5 and s["demo"] == 0 and s["level"] == 0 and s["lroutine"] == 4:
            j = _next_drawn(trace, i)
            return {"ram": s["frame"], "seen": trace[j]["frame"] if j is not None else s["frame"] + 1,
                    "hud_flag": s.get("hud")}
    return None


def end_frame(trace: Iterable[Mapping[str, int]]) -> Optional[dict]:
    """Returns {"control_lost": A, "ram": P, "seen": P+1, "held_at_A": pad byte} or None if the run does not get there."""
    trace = trace if isinstance(trace, list) else list(trace)
    a = None
    for i, s in enumerate(trace):
        if a is None:
            if s["groutine"] == 5 and s["demo"] == 0 and s["level"] == 7 and s["lroutine"] == 9:
                a = i
            continue
        if s["pseq"] == 0 and (s["jump"] & 0x0F) == 0 and s["aim"] in STAND_AIMS:
            j = _next_drawn(trace, i)
            return {"control_lost": trace[a]["frame"], "ram": s["frame"],
                    "seen": trace[j]["frame"] if j is not None else s["frame"] + 1,
                    "held_at_control_loss": trace[a].get("pad"),
                    "up_or_down_held": bool(trace[a].get("pad", 0) & 0x0C)}
        if s["lroutine"] not in (9,) or s["level"] != 7:
            break
    return None


def run_time(start_seen: int, end_seen: int) -> float:
    return (end_seen - start_seen) / NES_FPS


def fmt(seconds: float) -> str:
    return f"{int(seconds // 60)}:{seconds % 60:06.3f}"


def measure(trace) -> dict:
    """START / END / time for a traced run. `finished` is False if the heart was never beaten."""
    trace = trace if isinstance(trace, list) else list(trace)
    st, en = start_frame(trace), end_frame(trace)
    out = {"start": st, "end": en, "finished": bool(st and en)}
    if st and en:
        out["frames"] = en["seen"] - st["seen"]
        out["seconds"] = run_time(st["seen"], en["seen"])
        out["time"] = fmt(out["seconds"])
    return out
