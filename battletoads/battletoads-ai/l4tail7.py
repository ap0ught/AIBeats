"""Old logic after checkpoint 6 (l4.cp6_bowl source from 'left2 = ' to its end) on L4n_cp6; bookmarks n8_."""
import inspect, json, textwrap
import l4
from toads.emulator import BizHawk
src = inspect.getsource(l4.cp6_bowl)
start = src.index("    left2 = ")
body = textwrap.dedent(src[start:])
emu = BizHawk(log_name="l4tail7.log"); real_save = emu.save; emu.save = lambda name: real_save("n8_" + name)
emu.load("L4n_cp6"); rec = l4.Rec(emu)
def log(s): print(f"[{rec.f}] {s}", flush=True)
try: exec(body, {**vars(l4), "emu": emu, "rec": rec, "log": log})
except Exception as ex: print("STOPPED:", repr(ex), flush=True)
r = emu.ram_all(); print("end: frames", rec.f, "level", r[0x10], "cp", r[0x585], "lives", r[0x11], "hp", r[0x51A], flush=True)
json.dump(rec.inputs, open("knowledge/l4_tail7_inputs.json", "w")); emu.close()
