"""Level 8 on a new upstream route (2026-10-02). The climb is NOT random: the old seven sections replay exactly
from any run's placement (found by replaying pbeam_L8a on the new route: it reaches the arena untouched and only
the Robo-Manus fight goes wrong). So: l8.run() from the new entry with the old climb, a fresh boss search, and the
same closed-loop ending.

    python l8f.py arena  <entry bookmark>          -> bookmark L8f_arena (root for: L4S_LVL=7 python l4s.py L8f_arena 0 0 300 boss)
    python l8f.py finish <entry bookmark> [out]    -> logs/pbeam_<out or L8f>.json, bookmark f_L9_drop
"""
import json
import sys

import l8
from toads.emulator import BizHawk, LOGS_DIR

l8.SECTIONS = ["L8_c1", "L8_c2", "L8_c3", "L8_c4", "L8_c5", "L8_c6", "L8_c7"]


def main(mode, entry, out="L8f"):
    emu = BizHawk(log_name="l8f.log")
    real_save = emu.save
    emu.save = lambda name: real_save("f_" + name)        # keep the old route's bookmarks
    l8.BOSS = "L8f_arena" if mode == "finish" else None
    rec, H = l8.run(emu, bookmark=entry)
    r = emu.ram_all()
    if mode == "arena":
        rec.step((), 160)
        real_save("L8f_arena")
        print("arena:", l8.toad(emu.ram_all()), "after", rec.f, "frames; H", H.v)
    else:
        note = json.load(open(LOGS_DIR / "pbeam_L8a.json")).get("note", "")
        json.dump({"bookmark": entry, "inputs": rec.inputs, "note": note}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
        print("saved", f"pbeam_{out}.json", rec.f, "frames; end", l8.toad(r))
    emu.close()


if __name__ == "__main__":
    main(*sys.argv[1:])
