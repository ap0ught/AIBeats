"""u16b probe: L6c with its warp-page tail replaced (a) by A,B alternating, (b) by the old tail with Start -> A; writes test segments
u16b_B6x / u16b_B6s (bookmark L4c5_end0) for u16b_tailprobe.py.  Not route segments."""
import json
from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, write_json
sj = json.load(open(LOGS_DIR / "pbeam_L6c.json")); seg = [b.replace(",", "+") for b in sj["inputs"]]
F = {"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A}
e = BizHawk(log_name="u16b_mkb6x.log", fields=F)
for name, tail in (("u16b_B6x", None), ("u16b_B6s", [("A" if b == "Start" else b) for b in seg[2392:]])):
    e.load(sj["bookmark"])
    ins = []
    for b in seg[:2392]:
        e.step(bt(b), 1); ins.append(b)
    stage = 0
    for j in range(400):
        b = ["A", "B"][j % 2] if tail is None else (tail[j] if j < len(tail) else "")
        s = e.step(bt(b), 1); ins.append(b)
        if stage == 0 and s.level == 7: stage = 1
        if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0: stage = 2
        if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0: break
    d = dict(sj); d["inputs"] = ins
    write_json(LOGS_DIR / f"pbeam_{name}.json", d)
    print(name, len(ins), "inputs (L6c 2595)")
e.close()
