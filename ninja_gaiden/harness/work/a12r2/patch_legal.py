"""Append the round-2 waypoint section to ng/legal.py (safe edit: .backup, temp file + rename)."""
import os
import shutil
import sys

p = "ng/legal.py"
add = open(sys.argv[1], encoding="utf-8").read()
src = open(p, encoding="utf-8").read()
if "class Waypoints" in src:
    print("already patched")
    sys.exit(0)
shutil.copy(p, p + ".backup")
old = 'KEYS                                    the trace fields compared for "in sync"'
new = ("Waypoints(rec_json, stage, tas=None)    (round 2) the record holder's route from the record video: .pts\n"
       "    [(t, room, X, y)], .at(t) -> (room, X, y), .time_map() -> TAS frame per record time, .columns()\n"
       "waypoint_ref(wp, f0) -> dict           a beam reference that follows the record in record time from our frame\n"
       "    f0 (the `ref` format of ng/stages/a56_beam.StageBeam; driver ng/stages/a12r2_solve.py)\n" + old)
assert old in src
src = src.replace(old, new, 1)
tmp = p + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    f.write(src.rstrip("\n") + "\n" + add)
os.replace(tmp, p)
print("patched")
