"""Run the OLD Level 4 logic from platform 2 (l4.py, "# the line ends mid-punch" through cp6_bowl) on n2_L4_cp6_onp2.
Bookmarks get an 'n3_' prefix. Writes knowledge/l4_tail3_inputs.json."""
import inspect, json, textwrap
import l4
from toads.emulator import BizHawk

src = inspect.getsource(l4.run)
start = src.index("        # the line ends mid-punch")
end = src.index("    return rec", start)
body = textwrap.dedent(src[start:end])

def main():
    emu = BizHawk(log_name="l4tail3.log")
    real_save = emu.save
    emu.save = lambda name: real_save("n3_" + name)
    emu.load("n2_L4_cp6_onp2")
    rec = l4.Rec(emu)
    def log(s): print(f"[{rec.f}] {s}", flush=True)
    try:
        exec(body, {**vars(l4), "emu": emu, "rec": rec, "log": log})
    except Exception as ex:
        print("STOPPED:", repr(ex), flush=True)
    r = emu.ram_all()
    print("end: frames", rec.f, "level", r[0x10], "cp", r[0x585], "lives", r[0x11], "hp", r[0x51A], flush=True)
    json.dump(rec.inputs, open("knowledge/l4_tail3_inputs.json", "w"))
    emu.close()

if __name__ == "__main__":
    main()
