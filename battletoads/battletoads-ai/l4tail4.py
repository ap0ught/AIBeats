"""Old Level 4 logic from the cp6 pillar top (l4.py, 'spiky = ...' through cp6_bowl) on n3_L4_cp6_pillar; bookmarks n4_."""
import inspect, json, textwrap, sys
import l4
from toads.emulator import BizHawk
src = inspect.getsource(l4.run)
start = src.index('        spiky = PROJECT / "knowledge" / "l4s_L4_cp6_pillar.json"')
end = src.index("    return rec", start)
body = textwrap.dedent(src[start:end])
emu = BizHawk(log_name="l4tail4.log"); real_save = emu.save; emu.save = lambda name: real_save("n4_" + name)
emu.load(sys.argv[1] if len(sys.argv) > 1 else "n3_L4_cp6_pillar"); rec = l4.Rec(emu)
def log(s): print(f"[{rec.f}] {s}", flush=True)
try: exec(body, {**vars(l4), "emu": emu, "rec": rec, "log": log})
except Exception as ex: print("STOPPED:", repr(ex), flush=True)
r = emu.ram_all(); print("end: frames", rec.f, "level", r[0x10], "cp", r[0x585], "lives", r[0x11], "hp", r[0x51A], flush=True)
json.dump(rec.inputs, open("knowledge/l4_tail4_inputs.json", "w")); emu.close()
