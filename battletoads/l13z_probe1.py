"""L13 ending forensics (2026-10-09): replay a queen segment from its entry bookmark, dump the whole RAM every frame
from input <from> on, through the first cut (level 13->254, the Queen's speech), an A mash through the speech, and on
to the second 13->254 (the cut to T. Bird = the leaderboard's end).
    python l13z_probe1.py <segment> <from> <tag>      -> logs/fix/l13z_<tag>_ram.bin (+ .json index), states L13z_<tag>_*"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

seg, i0, tag = sys.argv[1], int(sys.argv[2]), sys.argv[3]
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = j["inputs"]
bt = lambda s: tuple(b for b in s.split("+") if b)
e = BizHawk(log_name=f"l13z_probe1_{tag}.log")
e.load(j["bookmark"])
out = open(LOGS_DIR / "fix" / f"l13z_{tag}_ram.bin", "wb")
idx = {"segment": seg, "bookmark": j["bookmark"], "from": i0, "events": []}
prev = 13
n = 0
cuts = []
saves = {int(v) for v in sys.argv[4].split(",")} if len(sys.argv) > 4 else set()
k = 0
while n < len(ins) + 3000:
    if n < len(ins):
        b = bt(ins[n])
    else:
        b = ("A",) if k % 2 == 0 else ()
        k += 1
    e.step(b, 1)
    n += 1
    if n in saves:
        e.save(f"L13z_{tag}_i{n}")
    if n >= i0:
        r = e.ram_all()
        out.write(r)
        lv = r[0x10]
    else:
        lv = e.byte(0x10)
    if lv != prev:
        idx["events"].append((n, prev, lv))
        print("input", n, "level", prev, "->", lv, flush=True)
        if prev == 13 and lv == 254:
            cuts.append(n)
            if len(cuts) == 1:
                e.save(f"L13z_{tag}_cut1")
            if len(cuts) == 2:
                break
        prev = lv
out.close()
idx["cuts"] = cuts
idx["frames"] = n
json.dump(idx, open(LOGS_DIR / "fix" / f"l13z_{tag}_ram.json", "w"))
print("cuts", cuts, "T. Bird cut at input", cuts[-1] if len(cuts) == 2 else None, flush=True)
e.close()
