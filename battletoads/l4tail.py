"""Run the OLD Level 4 policy's closed-loop logic from the icy ledge (l4.py, "the ledge is an icy ramp ..." through
the warp) on the NEW fast state L4n_ledge5. The code is sliced out of l4.run's source so it stays identical; the
bookmarks it saves get an 'n_' prefix. Reports each stage and whether the warp (level byte 8) fires.

    python l4tail.py  -> knowledge/l4_tail_inputs.json (inputs after L4n_ledge5), bookmark L4n_seg_end
"""
import inspect, json, textwrap
import l4
from toads.emulator import BizHawk

src = inspect.getsource(l4.run)
start = src.index("    # the ledge is an icy ramp")
end = src.index("    return rec", start)
body = textwrap.dedent(src[start:end])

def main():
    emu = BizHawk(log_name="l4tail.log")
    real_save = emu.save
    emu.save = lambda name: real_save("n_" + name)
    emu.load("L4n_ledge5")
    rec = l4.Rec(emu)
    def log(s): print(f"[{rec.f}] {s}", flush=True)
    try:
        exec(body, {**vars(l4), "emu": emu, "rec": rec, "log": log})
    except Exception as ex:
        print("STOPPED:", repr(ex), flush=True)
    r = emu.ram_all()
    print("end: frames", rec.f, "level", r[0x10], "cp", r[0x585], "lives", r[0x11], "hp", r[0x51A], flush=True)
    json.dump(rec.inputs, open("knowledge/l4_tail_inputs.json", "w"))
    emu.close()

if __name__ == "__main__":
    main()
