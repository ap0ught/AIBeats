"""Brute force for the last flagpole grab (2026-10-04): from OW_o4 (old 8750) idle k, then hold Right and press A from frame a on (hold 67),
until the toad hangs (anim 95) near the old's pole hang (288,4944). -> knowledge/l12_pole2.json, bookmark PL2_hang"""
import json
from toads.emulator import BizHawk
def toad(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l12pole2b.log"); e.load("OW_o4"); base = e.msave(); best = None
for k in range(0, 80):
    for a in range(0, 30):
        e.mload(base); e.step((), k); ins = [""] * k; hang = None
        for t in range(a + 67 + 70):
            b = ("Right",) if t < a else (("Right", "A") if t < a + 67 else ())
            e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
            if m[0x11] < 4 or m[0x51A] < 47: break
            if m[0x3B5] == 95: hang = toad(m); break
        if hang and abs(hang[0] - 288) <= 3 and abs(hang[1] - 4944) <= 3:
            print("HANG k", k, "a", a, "at", hang, "after", len(ins), "frames (old 82)", flush=True)
            if best is None or len(ins) < best[0]:
                best = (len(ins), k, a, ins); e.save("PL2_hang"); json.dump({"bookmark": "OW_o4", "inputs": ins, "old_at": 8832}, open("knowledge/l12_pole2.json", "w"))
        elif hang and a == 0 and k % 10 == 0: print("k", k, "a 0: hangs elsewhere", hang, flush=True)
    if best and k > best[1] + 4: break
print("best", best[:3] if best else None, flush=True); e.close()
