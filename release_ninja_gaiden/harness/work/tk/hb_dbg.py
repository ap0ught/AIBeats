import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ng.solve import common as C, hitbox as H
from ng.mode import TICKS
import a56_common as A
e = C.open_emu("tk_hb_dbg.log")
try:
    e.tick(TICKS); e.load("ref4751/09_4-2_control")
    e.run(A.tas_rows()[16682:18652])
    st, rams = e.run_ram(A.tas_rows()[18652:18659])
finally:
    e.close()
for k, r in enumerate(rams):
    print(18653 + k, "ryu", H.ryu(r)["x"], H.ryu(r)["y"], "h", r[0x90], "kb", hex(r[0x93]), "flags", hex(r[0x84]), "act", r[0x80])
    for en in H.enemies(r): print("    ", en["slot"], en["type"], en["pose"], en["x"], en["y"], en["xr"], en["yr"], H.hurts(r, en))
