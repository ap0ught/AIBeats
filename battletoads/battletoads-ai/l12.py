"""Level 12, The Revolution: replay the searched sections from `L12_start` (placement (136,30), written by l11.py),
then wait for the level to end and Start into Armageddon. Journal 012.
    python l10.py [sections...]   -> logs/pbeam_L12a.json, bookmarks L12_x<i>, L13_start"""
import json, sys, time
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens
from l6 import Unwrap, Rec
FULL = [f"L12_r{k}" for k in range(1, 40)]
_NI = PROJECT / "knowledge" / "l12_noidle.json"
NOIDLE = set(json.loads(_NI.read_text())) if _NI.exists() else set()
SECTIONS = sys.argv[1:] or [s for s in FULL if (PROJECT / "knowledge" / f"l4s_{s}.json").exists()]

def toad(r):
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=r[0x439], z=r[0x475], st=r[0x4B1], an=r[0x3B5], hp=r[0x51A],
                lives=r[0x11], lvl=r[0x10], cam=r[0x87] + 256 * r[0x88], camy=r[0x89] + 256 * r[0x8A])

def replay(rec, name):
    ins = json.loads((PROJECT / "knowledge" / f"l4s_{name}.json").read_text())
    for s in ins:
        rec.step(tuple(b for b in s.split("+") if b), 1)
    return len(ins)

def run(emu, bookmark="L12_start", log=print):
    emu.load(bookmark)
    H = Unwrap()
    rec = Rec(emu, sampler=lambda: H(emu.ram_all()[0x439]))
    H.reset(); H(emu.ram_all()[0x439], anchor=0)            # heights relative to the placement (h 30 there)
    first = True
    for i, name in enumerate(SECTIONS, 1):
        if not first and name not in NOIDLE:
            rec.step((), 2)                                 # search roots = the previous solved state + 2 idle frames
                                                            # (spliced TAS-sync sections continue without them: a bounce breaks)
        first = False                                       # (L12_r1 is the TAS replay: it starts at the placement itself)
        n = replay(rec, name)
        t = toad(emu.ram_all())
        log(f"section {name}: {n} frames -> f{rec.f} H {H.v} {t}")
        emu.save(f"L12_x{i}")
    if emu.ram_all()[0x10] == 5:
        return rec, H                                       # the level is not over yet: partial chain
    for _ in range(150):
        t = toad(emu.ram_all())
        if t["lvl"] not in (5, 254, 255) and t["hp"] == 47:
            break
        rec.step(("Start",), 2); rec.step((), 18)
    log(f"next level loaded at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L13_load")
    return rec, H

if __name__ == "__main__":
    emu = BizHawk(log_name="l12.log")
    t0 = time.time()
    rec, H = run(emu)
    t = toad(emu.ram_all())
    emu.close()
    print("segment", rec.f, "frames, end", t, "H", H.v, f"{time.time() - t0:.0f}s")
    (LOGS_DIR / "pbeam_L12a.json").write_text(json.dumps({
        "bookmark": "L12_start", "inputs": rec.inputs, "info": {"f": rec.f, "x": t["x"], "hp": t["hp"]}, "state": None, "history": [],
        "note": "THE REVOLUTION: up the rotating tower - springs, green timed platforms, Hornheads - a beam following a "
                "1-player TAS's route without its Left+Right presses.||" f"{rec.f} frames"}))
    tokens.mark("L12 segment", {"frames": rec.f, "hp": t["hp"], "lives": t["lives"]})
