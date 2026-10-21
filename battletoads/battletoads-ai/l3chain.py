"""Level 3 gauntlet on TAS #5093's line (2026-09-30): fast intro + TAS inputs to x 678, then searched sections.
Rebuilds from L1route_end, saves L3n_<section> bookmarks, writes logs/pbeam_L3n.json (ends at the bikes = the state
the tunnel-skip segment expects: x 1677, h 64, standing).

    python l3chain.py
"""
import json
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
import l3tas
from l4tas import conv

SECTIONS = [("r1", "knowledge/l3_rat827.json", 2),   # rat at 845: hit on the run (324 f)
            ("f2a", "knowledge/l3_f2a.json", 2),     # follow the TAS line to x 1167 (the pit ahead)
            ("r2", "knowledge/l3_r2.json", 2),       # the rat that spawns behind at 1128: kill it or the camera never scrolls
            ("f2b", "knowledge/l3_f2b.json", 0),     # dash-jump (tap, gap, Right+A) over the pit at ~1230 (scripted: no lead-in)
            ("r3", "knowledge/l3_r3.json", 2),       # the rat at 1432
            ("f4", "knowledge/l3_f4.json", 2)]       # to the bikes (x 1677)

def main():
    rows = l3tas.load("tas/ram_l3_1p.txt")
    e = BizHawk(log_name="l3chain.log")
    e.load("L1route_end"); ins = []
    def step(b):
        e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b); return e.ram(0, 0x800)
    for k in range(700):
        m = step("B" if k % 2 == 0 else "")
        if l3tas.placed(m): break
    for j in range(1, 765): step("+".join(conv(rows[13155 + j][0])))
    m = e.ram(0, 0x800); print("TAS line to x", m[0x3FD] | m[0x3EE] << 8, "at input", len(ins), flush=True)
    for name, fn, idle in SECTIONS:
        p = PROJECT / fn
        if not p.exists(): break
        for _ in range(idle): step("")
        for b in json.loads(p.read_text()): m = step(b)
        e.save(f"L3n_{name}")
        print(f"{name}: input {len(ins)}, x {m[0x3FD] | m[0x3EE] << 8}, h {m[0x439]}, hp {m[0x51A]}, lives {m[0x11]}, "
              f"rats {[(m[0x3FD+s]|m[0x3EE+s]<<8, m[0x51A+s]) for s in range(2,15) if m[0x3C1+s] in (0x47,0xC7)]}", flush=True)
    json.dump({"bookmark": "L1route_end", "inputs": ins,
               "note": "LEVEL 3: the rat gauntlet on the TAS's line. Cutscene and intro pages skipped with a button; TAS #5093's "
                       "own inputs to x 678; then searched sections - hit each rat on the run instead of waiting beside it."
                       "||Old route: stop, wait 93 frames, headbutt twice. New: ~1,300 frames faster per rat"},
              open(LOGS_DIR / "pbeam_L3n.json", "w"))
    print("total", len(ins)); e.close()

if __name__ == "__main__":
    main()
