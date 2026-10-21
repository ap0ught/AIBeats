"""Old cp6_bowl (and what follows it) from the new bowl-top state n7_L4_bowltop; bookmarks n7_."""
import json, sys
import l4
from toads.emulator import BizHawk
emu = BizHawk(log_name="l4tail6.log"); real_save = emu.save; emu.save = lambda name: real_save("n7_" + name)
emu.load("n7_L4_bowltop"); rec = l4.Rec(emu)
def log(s): print(f"[{rec.f}] {s}", flush=True)
try: l4.cp6_bowl(emu, rec, log)
except Exception as ex: print("STOPPED:", repr(ex), flush=True)
r = emu.ram_all(); print("end: frames", rec.f, "level", r[0x10], "cp", r[0x585], "lives", r[0x11], "hp", r[0x51A], flush=True)
json.dump(rec.inputs, open("knowledge/l4_tail6_inputs.json", "w")); emu.close()
