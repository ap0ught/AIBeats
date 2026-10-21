"""Old Level 4 logic from the lower ledge (l4.py 'lower = ...' section onward) on n5_L4_cp6_lowerstart; bookmarks n5_."""
import inspect, json, textwrap, sys
import l4
from toads.emulator import BizHawk
src = inspect.getsource(l4.run)
start = src.index('            lower = PROJECT / "knowledge" / "l4s_L4_cp6_best_end.json"')
end = src.index("    return rec", start)
body = textwrap.dedent(src[start:end])
emu = BizHawk(log_name="l4tail5.log"); real_save = emu.save; emu.save = lambda name: real_save("n5_" + name)
emu.load("n5_L4_cp6_lowerstart"); rec = l4.Rec(emu)
def log(s): print(f"[{rec.f}] {s}", flush=True)
try: exec(body, {**vars(l4), "emu": emu, "rec": rec, "log": log})
except Exception as ex: print("STOPPED:", repr(ex), flush=True)
r = emu.ram_all(); print("end: frames", rec.f, "level", r[0x10], "cp", r[0x585], "lives", r[0x11], "hp", r[0x51A], flush=True)
json.dump(rec.inputs, open("knowledge/l4_tail5_inputs.json", "w")); emu.close()
