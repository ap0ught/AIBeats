"""Level 9, Terra Tubes: replay the beam-searched sections from `L9_drop` (the frame the toad appears, written by
l8.py). Journal 009 has the level's mechanics and the TAS waypoints.

    python l9.py [sections...]   -> logs/pbeam_L9a.json (segment for assemble.py), bookmarks L9_x<i>, L9_end
"""
import json
import sys
import time

from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens
from l6 import Unwrap, Rec

FULL = (["L9_s1", "L9_s1wait", "L9_s2b", "L9_s3cut", "L9_pipe", "L9_p2", "L9_gear"] + [f"L9_p{k}" for k in range(3, 10)]
        + ["L9_p10a", "L9_p10w", "L9_p10b"] + [f"L9_q{k}" for k in range(0, 7)] + ["L9_q7a", "L9_q7w", "L9_q7b", "L9_q8", "L9_q9", "L9_q10",
        "L9_q11a", "L9_q11w", "L9_q11b", "L9_r0", "L9_r1", "L9_r2", "L9_r3", "L9_end"])
SECTIONS = sys.argv[1:] or FULL


def toad(r):
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=r[0x439], z=r[0x475], st=r[0x4B1], an=r[0x3B5], hp=r[0x51A],
                lives=r[0x11], lvl=r[0x10], cam=r[0x87] + 256 * r[0x88], camy=r[0x89] + 256 * r[0x8A], cp=r[0x585])


def replay(rec, name):
    ins = json.loads((PROJECT / "knowledge" / f"l4s_{name}.json").read_text())
    for s in ins:
        rec.step(tuple(b for b in s.split("+") if b), 1)
    return len(ins)


def run(emu, bookmark="L9_drop", log=print):
    emu.load(bookmark)
    H = Unwrap()
    rec = Rec(emu, sampler=lambda: H(emu.ram_all()[0x439]))
    rec.step((), 2)                                         # every search root = its bookmark's saved state + 2 idle frames
    H.reset(); H(emu.ram_all()[0x439], anchor=0)            # heights relative to the drop-in (h 112 there)
    rec.step(("Left", "A"), 24)                             # the start-of-level OOB: jump left over the wall top at once
    rec.step((), 2)                                         # section 1's bookmark (L9_s1) is the state right after the jump
    for i, name in enumerate(SECTIONS, 1):
        n = replay(rec, name)
        t = toad(emu.ram_all())
        log(f"section {name}: {n} frames -> f{rec.f} H {H.v} {t}")
        emu.save(f"L9_x{i}")
        rec.step((), 2)
    emu.save("L9_end_reached")
    if SECTIONS[-1] != "L9_end":
        return rec, H
    # the end trigger fired while dying; the level byte leaves 11 ~340 frames later. Then Start through the card
    # until Rat Race (level byte 9) has the toad placed with full health
    for _ in range(900):
        if emu.ram_all()[0x10] != 11:
            break
        rec.step((), 1)
    log(f"level byte left 11 at f{rec.f}")
    for _ in range(150):
        t = toad(emu.ram_all())
        if t["lvl"] == 9 and t["hp"] == 47:
            break
        rec.step(("Start",), 2); rec.step((), 18)
    t = toad(emu.ram_all())
    log(f"Rat Race loaded at f{rec.f}: {t}")
    emu.save("L10_load")
    for _ in range(400):                                    # the toad is placed at (88, 158) ~220 frames later, controllable at once
        t = toad(emu.ram_all())
        if t["lvl"] == 9 and t["x"] == 88 and t["h"] == 158:
            break
        rec.step((), 1)
    log(f"Rat Race start at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L10_start")
    return rec, H


if __name__ == "__main__":
    emu = BizHawk(log_name="l9.log")
    t0 = time.time()
    rec, H = run(emu)
    t = toad(emu.ram_all())
    emu.close()
    print("segment", rec.f, "frames, end", t, "H", H.v, f"{time.time() - t0:.0f}s")
    (LOGS_DIR / "pbeam_L9a.json").write_text(json.dumps({
        "bookmark": "L9_drop", "inputs": rec.inputs, "info": {"f": rec.f, "x": t["x"], "hp": t["hp"]}, "state": None, "history": [],
        "note": "TERRA TUBES: over the start wall (its top has no collision), down the outside of the tubes, through a "
                "spark-guarded pipe, and four gear checkpoints - the beam follows a 1-player TAS's path; the end is reached "
                "while dying on the last spikes.||" f"{rec.f} frames"}))
    tokens.mark("L9 segment", {"frames": rec.f, "hp": t["hp"], "lives": t["lives"]})
