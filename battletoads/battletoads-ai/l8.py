"""Level 8, Intruder Excluder: replay the beam-searched climb sections from `L8_start` (written by l6.py), then
the Robo-Manus fight. Journal 008 has the level's mechanics.

    python l8.py   -> logs/pbeam_L8a.json (segment for assemble.py), bookmarks L8_s<i>, L8_top
"""
import json
import sys
import time

from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens
from l6 import Unwrap, Rec

SECTIONS = sys.argv[1:] or ["L8_c1", "L8_c2", "L8_c3", "L8_c4", "L8_c5", "L8_c6", "L8_c7"]
BOSS = __import__("os").environ.get("L8_BOSS")            # e.g. L8_arena: knowledge/l4s_L8_arena.json (the fight)


def toad(r):
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=r[0x439], z=r[0x475], st=r[0x4B1], an=r[0x3B5], hp=r[0x51A],
                lives=r[0x11], lvl=r[0x10], camy=r[0x89] + 256 * r[0x8A])


def objs(r):
    return [(hex(r[0x3C1 + s]), r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s], r[0x51A + s], r[0x4B1 + s])
            for s in range(2, 15) if r[0x3C1 + s]]


def replay(rec, name):
    ins = json.loads((PROJECT / "knowledge" / f"l4s_{name}.json").read_text())
    for s in ins:
        rec.step(tuple(b for b in s.split("+") if b), 1)
    return len(ins)


def run(emu, bookmark="L8_start", log=print):
    emu.load(bookmark)
    H = Unwrap()
    rec = Rec(emu, sampler=lambda: H(emu.ram_all()[0x439]))
    rec.step((), 2)                                         # every search root = its bookmark's saved state + 2 idle frames (both recorded)
    H(emu.ram_all()[0x439], anchor=94)
    for i, name in enumerate(SECTIONS, 1):
        n = replay(rec, name)
        t = toad(emu.ram_all())
        log(f"section {name}: {n} frames -> f{rec.f} H {H.v} {t}")
        emu.save(f"L8_s{i}")
        rec.step((), 2)                                     # the next search's root = this solved state + 2 idle frames
    emu.save("L8_top")
    if not BOSS:
        return rec, H
    # Robo-Manus: the arrival animation (toad anim 50) ends ~160 frames after the drop; the boss search started
    # from L8_arena = L8_top + 160 idle frames
    rec.step((), 160)
    n = replay(rec, BOSS)
    t = toad(emu.ram_all()); r = emu.ram_all()
    log(f"boss segment {BOSS}: {n} frames -> f{rec.f} {t} score {r[0x5F4]}{r[0x5F5]}{r[0x5F6]}000 boss {[hex(r[0x3C1 + s]) for s in range(2, 15) if r[0x3C1 + s] in (0x7d, 0x46)]}")
    emu.save("L8_boss_dead")
    # the level ends ~440 frames after the kill: wait for the level byte to leave 7, then mash Start through the
    # card until Terra Tubes (level byte 11) has the toad placed with full health
    for _ in range(900):
        if emu.ram_all()[0x10] != 7:
            break
        rec.step((), 1)
    log(f"level byte left 7 at f{rec.f}")
    for _ in range(150):
        t = toad(emu.ram_all())
        if t["lvl"] == 11 and t["hp"] == 47 and t["z"] == 0:
            break
        rec.step(("Start",), 2); rec.step((), 18)
    # Terra Tubes loads ~180 frames later: the toad is dropped in at (40,112) and falls to the floor at h 6.
    # The segment ends the frame the toad appears (L9_drop): the start-of-level out-of-bounds needs inputs
    # during that fall
    for _ in range(600):
        t = toad(emu.ram_all())
        if t["lvl"] == 11 and t["x"] <= 60 and t["h"] >= 100 and t["hp"] == 47:
            break
        rec.step((), 1)
    t = toad(emu.ram_all())
    log(f"Terra Tubes drop-in at f{rec.f}: {t}")
    emu.save("L9_drop")
    return rec, H


if __name__ == "__main__":
    emu = BizHawk(log_name="l8.log")
    t0 = time.time()
    rec, H = run(emu)
    t = toad(emu.ram_all())
    emu.close()
    print("segment", rec.f, "frames, end", t, "H", H.v, f"{time.time() - t0:.0f}s")
    (LOGS_DIR / "pbeam_L8a.json").write_text(json.dumps({
        "bookmark": "L8_start", "inputs": rec.inputs, "info": {"f": rec.f, "x": t["x"], "hp": t["hp"]}, "state": None, "history": [],
        "note": "INTRUDER EXCLUDER: a 4,000-px tower climbed floor by floor - each jump's apex lands on the next floor's "
                "edge, moving electric holes and elevators timed by beam search.||" f"{rec.f} frames"}))
    tokens.mark("L8 climb segment", {"frames": rec.f, "hp": t["hp"], "lives": t["lives"]})
