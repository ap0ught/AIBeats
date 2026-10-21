"""Level 11, Clinger-Winger: replay the searched sections from `L11_start` (placement at (28,44), written by l10.py).
"Height" here = -(camera y - 168). Journal 011.    python l11.py [sections...] -> logs/pbeam_L11a.json"""
import json, sys, time
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
from toads import tokens
from l6 import Rec
FULL = [f"L11_c{k}" for k in range(1, 30)]
SECTIONS = sys.argv[1:] or [s for s in FULL if (PROJECT / "knowledge" / f"l4s_{s}.json").exists()]

def toad(r):
    cy = (r[0x89] + 256 * r[0x8A] + 32768) % 65536 - 32768
    return dict(x=r[0x3FD] + 256 * r[0x3EE], h=r[0x439], an=r[0x3B5], hp=r[0x51A], lives=r[0x11], lvl=r[0x10], camy=cy, spd=r[0x565])

def replay(rec, name):
    ins = json.loads((PROJECT / "knowledge" / f"l4s_{name}.json").read_text())
    for s in ins:
        rec.step(tuple(b for b in s.split("+") if b), 1)
    return len(ins)

def run(emu, bookmark="L11_start", log=print):
    emu.load(bookmark)
    rec = Rec(emu)
    rec.step((), 2)
    for i, name in enumerate(SECTIONS, 1):
        n = replay(rec, name)
        t = toad(emu.ram_all())
        log(f"section {name}: {n} frames -> f{rec.f} H {-(t['camy'] - 168)} {t}")
        emu.save(f"L11_x{i}")
        rec.step((), 2)
    r = emu.ram_all()
    if any(r[0x3C1 + s] == 0x7b and r[0x51A + s] > 0 for s in range(2, 15)) or SECTIONS[-1] != "L11_c5":
        return rec                                          # the Buzzball is not beaten yet: partial chain
    for _ in range(1200):
        if emu.ram_all()[0x10] != 10:
            break
        rec.step((), 1)
    log(f"level byte left 10 at f{rec.f}")
    for _ in range(150):
        t = toad(emu.ram_all())
        if t["lvl"] == 5 and t["hp"] == 47:
            break
        rec.step(("Start",), 2); rec.step((), 18)
    log(f"The Revolution loaded at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L12_load")
    for _ in range(400):                                    # the toad is placed at (136, 30) ~219 frames later
        t = toad(emu.ram_all())
        if t["lvl"] == 5 and t["x"] == 136 and t["h"] == 30 and t["hp"] == 47:
            break
        rec.step((), 1)
    log(f"The Revolution start at f{rec.f}: {toad(emu.ram_all())}")
    emu.save("L12_start")
    return rec

if __name__ == "__main__":
    emu = BizHawk(log_name="l11.log"); t0 = time.time()
    rec = run(emu); t = toad(emu.ram_all()); emu.close()
    print("segment", rec.f, "frames, end", t, f"{time.time() - t0:.0f}s")
    (LOGS_DIR / "pbeam_L11a.json").write_text(json.dumps({"bookmark": "L11_start", "inputs": rec.inputs, "info": {"f": rec.f}, "state": None, "history": [],
        "note": "CLINGER-WINGER: the unicycle maze with the Buzzball behind - a beam follows the 1-player TAS's route, "
                "turning at every arrow (no Up+Down presses).||" f"{rec.f} frames"}))
