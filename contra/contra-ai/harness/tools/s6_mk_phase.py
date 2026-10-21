"""DEBUG: stage-start savestates for stage 6 or 7 at chosen frame-counter phases (never part of a run).

    python tools/s6_mk_phase.py <stage 6|7> <d1,d2,...|a-b>

Same method as tools/mk_stage_state.py (the game's own opening, CURRENT_LEVEL poked on the frame the game has
cleared its variables, the weapon byte poked one frame before the first playable frame), except for WHEN the
buttons are pressed on the title screen, which is exactly what a real run would do to choose the global-timer
phase. Two knobs, both MEASURED here (limits() prints them):

    w  idle frames before the first press (Select, normally frame 11). Moves the start in steps of 2 frames only
       (the jingle timer counts on even frames). Waits of 10..44 frames were used and work; the upper limit that
       limits() reports comes from a bisection that assumes "works up to w" is monotonic, which was not proven
       (one early attempt with 66 idle frames ended in the attract demo).
    k  frames between Select and the Start press that selects the game. Up to K0 = 262 the start does not move
       (the 328-frame jingle is what the game waits for); from there every extra frame moves the start by one
       frame, for up to 57 frames, after which the demo begins.

make(e, stage, d) gives a start d frames later than the earliest one: the frame counter $1A on the stage's first
playable frame is (62 + d) mod 256. Saves states/s<stage>/ph<d>.State (one frame before the first playable frame).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CAL = None      # (k0, earliest load frame, max second-press delay, max first-press wait)


def start_frame(e, k, w=0):
    """Opening with w idle frames first and Start pressed k frames after Select; the state on the first frame
    the game is in a level's load routine (game routine 5), or None if the demo began instead."""
    e.reset()
    rows = [()] * (10 + w) + [("Select",)] + [()] * k + [("Start",), ("Start",)]
    s = e.run(rows)
    for _ in range(900):
        if s["groutine"] == 5:
            return s
        if s["groutine"] == 2:
            return None
        s = e.step((), 1)
    return None


def limits(e):
    base = start_frame(e, 0)
    f0 = base["frame"]
    lo, hi = 0, 330
    while lo < hi:                      # largest k that still starts on the earliest frame
        mid = (lo + hi + 1) // 2
        s = start_frame(e, mid)
        if s is not None and s["frame"] == f0:
            lo = mid
        else:
            hi = mid - 1
    k0 = lo
    lo, hi = 0, 120
    while lo < hi:                      # largest extra delay of the second press before the demo begins
        mid = (lo + hi + 1) // 2
        if start_frame(e, k0 + mid) is not None:
            lo = mid
        else:
            hi = mid - 1
    dmax = lo
    lo, hi = 0, 200
    while lo < hi:                      # largest wait before the first press
        mid = (lo + hi + 1) // 2
        if start_frame(e, 0, mid) is not None:
            lo = mid
        else:
            hi = mid - 1
    wmax = lo
    return k0, f0, dmax, wmax


def make(e, stage, d, weapon=0x13):
    global CAL
    if CAL is None:
        CAL = limits(e)
    k0, f0, dmax, wmax = CAL
    d2 = min(d, dmax)                   # second-press delay (1-frame steps)
    w = d - d2                          # the rest by waiting before the first press (2-frame steps)
    if w % 2:
        w += 1
        d2 -= 1
    assert 0 <= d2 <= dmax and 0 <= w <= wmax, (d, d2, w, CAL)
    s = start_frame(e, k0 + d2, w)
    assert s is not None and s["groutine"] == 5, (d, d2, w)
    assert s["frame"] == f0 + d, (d, d2, w, s["frame"], f0)
    e.poke(0x30, stage - 1)
    n = 0
    sid = None
    while True:
        prev = sid
        sid = e.msave()
        s = e.step((), 1)
        n += 1
        if prev:
            e.mfree(prev)
        if s["lroutine"] == 4:
            break
        assert n < 2000, dict(s)
    e.mload(sid)
    e.mfree(sid)
    e.poke(0xAA, weapon)
    name = f"s{stage}/ph{d}"
    e.save(name)
    s2 = e.step((), 1)
    return {"d": d, "state": name, "L": s2["frame"], "fc_at_L": s2["fc"], "rng_at_L": s2["rng"], "level": s2["level"],
            "wait_before_select": w, "start_after_select": k0 + d2}


if __name__ == "__main__":
    from contra.emulator import BizHawk
    from contra.stages.s6lib import FIELDS
    stage = int(sys.argv[1])
    spec = sys.argv[2]
    if "-" in spec:
        a, b = spec.split("-")
        ds = list(range(int(a), int(b) + 1))
    else:
        ds = [int(x) for x in spec.split(",")]
    with BizHawk(log_name=f"s{stage}_mkphase.log", fields=FIELDS) as e:
        print("limits (k0, earliest load frame, max second-press delay, max first-press wait):", limits(e))
        for d in ds:
            print(make(e, stage, d), flush=True)
