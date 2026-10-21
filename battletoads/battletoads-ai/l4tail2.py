"""Run the OLD Level 4 policy's closed-loop logic from checkpoint 5 (l4.py, "desc = ..." through the warp) on the
new state L4n_cp5. Bookmarks it saves get an 'n2_' prefix. Writes knowledge/l4_tail2_inputs.json."""
import inspect, json, textwrap
import l4
from toads.emulator import BizHawk

src = inspect.getsource(l4.run)
start = src.index('    desc = PROJECT / "knowledge" / "l4s_L4_cp5_done.json"')
end = src.index("    return rec", start)
body = textwrap.dedent(src[start:end])

def main():
    emu = BizHawk(log_name="l4tail2.log")
    real_save = emu.save
    emu.save = lambda name: real_save("n2_" + name)
    emu.load("L4n_cp5")
    rec = l4.Rec(emu)
    def log(s): print(f"[{rec.f}] {s}", flush=True)
    try:
        exec(body, {**vars(l4), "emu": emu, "rec": rec, "log": log})
    except Exception as ex:
        print("STOPPED:", repr(ex), flush=True)
    r = emu.ram_all()
    print("end: frames", rec.f, "level", r[0x10], "cp", r[0x585], "lives", r[0x11], "hp", r[0x51A], flush=True)
    json.dump(rec.inputs, open("knowledge/l4_tail2_inputs.json", "w"))
    emu.close()

if __name__ == "__main__":
    main()
