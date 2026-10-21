"""Level 10, Rat Race: replay the searched sections from `L10_start` (the placement at (88,158), written by l9.py),
then wait for the level to end (rat boot) and Start into Clinger-Winger. Journal 010.
    python l10.py [sections...]   -> logs/pbeam_L10a.json, bookmarks L10_x<i>, L11_start"""
import json, sys, time
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens
from l6 import Unwrap, Rec
FULL = [f"L10_f{k}" for k in range(1, 7)]              # f1-f4 follow, f5 scripted bomb kick, f6 scripted hard hit + boot
SECTIONS = sys.argv[1:] or FULL

def toad(r):
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=r[0x439], z=r[0x475], st=r[0x4B1], an=r[0x3B5], hp=r[0x51A],
                lives=r[0x11], lvl=r[0x10], cam=r[0x87] + 256 * r[0x88], camy=r[0x89] + 256 * r[0x8A])

def replay(rec, name):
    ins = json.loads((PROJECT / "knowledge" / f"l4s_{name}.json").read_text())
    for s in ins:
        rec.step(tuple(b for b in s.split("+") if b), 1)
    return len(ins)

def run(emu, bookmark="L10_start", log=print):
    emu.load(bookmark)
    H = Unwrap()
    rec = Rec(emu, sampler=lambda: H(emu.ram_all()[0x439]))
    rec.step((), 2)                                         # every search root = its bookmark + 2 idle frames
    H.reset(); H(emu.ram_all()[0x439], anchor=0)            # heights relative to the placement (h 158 there)
    for i, name in enumerate(SECTIONS, 1):
        n = replay(rec, name)
        t = toad(emu.ram_all())
        log(f"section {name}: {n} frames -> f{rec.f} H {H.v} {t}")
        emu.save(f"L10_x{i}")
        rec.step((), 2)
    if emu.ram_all()[0x10] == 9 and not any(emu.ram_all()[0x3C1 + s] == 0x46 and emu.ram_all()[0x51A + s] == 0 for s in range(2, 15)):
        return rec, H                                       # the rat is not booted yet: partial chain
    for _ in range(900):
        if emu.ram_all()[0x10] != 9:
            break
        rec.step((), 1)
    log(f"level byte left 9 at f{rec.f}")
    for _ in range(150):
        t = toad(emu.ram_all())
        if t["lvl"] == 10 and t["hp"] == 47:
            break
        rec.step(("Start",), 2); rec.step((), 18)
    log(f"Clinger-Winger loaded at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L11_load")
    for _ in range(400):                                    # the toad appears at (28, 44) ~220 frames later and rolls right
        t = toad(emu.ram_all())
        if t["lvl"] == 10 and t["x"] == 28 and t["h"] == 44 and t["hp"] == 47:
            break
        rec.step((), 1)
    log(f"Clinger-Winger start at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L11_start")
    return rec, H

if __name__ == "__main__":
    emu = BizHawk(log_name="l10.log")
    t0 = time.time()
    rec, H = run(emu)
    t = toad(emu.ram_all())
    emu.close()
    print("segment", rec.f, "frames, end", t, "H", H.v, f"{time.time() - t0:.0f}s")
    (LOGS_DIR / "pbeam_L10a.json").write_text(json.dumps({
        "bookmark": "L10_start", "inputs": rec.inputs, "info": {"f": rec.f, "x": t["x"], "hp": t["hp"]}, "state": None, "history": [],
        "note": "RAT RACE: one race down the shaft ahead of the rat, kick the bomb, then the rat boot - a hard hit and a "
                "boot end the level (allowed in Any% No Credits Warp).||" f"{rec.f} frames"}))
    tokens.mark("L10 segment", {"frames": rec.f, "hp": t["hp"], "lives": t["lives"]})
