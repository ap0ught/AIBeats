"""The last flagpole grab (2026-10-04): the old route runs right from old frame 8750 (7 idle, Right+A x67) and hangs on the pole at (288,4944) at 8832
(anim 95). From our state at 8750 (OW_o4) scan a few idle frames and run-up frames before the Right+A hold so that we hang on the same pole.
    python l12pole2.py  -> knowledge/l12_pole2.json {inputs from OW_o4}, bookmark PL2_hang"""
import json
from toads.emulator import BizHawk, LOGS_DIR
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]
def toad(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l12pole2.log"); e.load("L12w_at6705")
for i in range(6705, 8832): e.step(tuple(v for v in old[i].split("+") if v), 1)
ref = toad(e.ram(0, 0x800)); print("old hang at 8832:", ref, flush=True)
e.load("OW_o4"); base = e.msave(); found = []
for k in list(range(0, 12)) + list(range(30, 48)):
    for r in range(0, 4):
        for hold in (60, 67, 75):
            e.mload(base); ins = [""] * k + ["Right"] * r + ["Right+A"] * hold
            e.step((), k); e.step(("Right",), r); hang = None
            for t in range(hold + 60):
                e.step(("Right", "A") if t < hold else (), 1); m = e.ram(0, 0x800)
                if t >= hold: ins.append("")
                if m[0x11] < 4: break
                if m[0x3B5] == 95: hang = (t, toad(m)); break
            if hang and abs(hang[1][0] - ref[0]) <= 2 and abs(hang[1][1] - ref[1]) <= 2:
                found.append((len(ins), k, r, hold, hang)); print("HANG:", "k", k, "r", r, "hold", hold, "at", hang, "after", len(ins), "frames (old 82)", flush=True)
                e.save("PL2_hang"); json.dump({"bookmark": "OW_o4", "inputs": ins, "old_at": 8832}, open("knowledge/l12_pole2.json", "w"))
            elif hang and k == 0 and r == 0: print("k0 r0 hold", hold, "hang elsewhere:", hang, flush=True)
    if found: break
if not found: print("no matching hang", flush=True)
e.close()
