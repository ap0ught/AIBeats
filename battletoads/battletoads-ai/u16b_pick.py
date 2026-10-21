"""u16b: write one variant found by u16b_sync.py as a segment.
    python u16b_pick.py <raw segment> <out> <old segment length in this slot (parity reference)> [alignment ts wanted]
Picks the shortest variant in logs/fix/u16b_sync_<out>.json that (a) tracked the old run and (b) shifts the route by an EVEN
number of frames against the old segment (the PPU's odd/even frames differ by a third of a CPU cycle: behind an odd
shift two runs are never identical for good, they only track each other by luck), replays it from the segment's bookmark,
saves bookmark <out>_end0 and logs/pbeam_<out>.json."""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, write_json, FIX, banned
RAW, OUT, OLDLEN = sys.argv[1], sys.argv[2], int(sys.argv[3])
TS = int(sys.argv[4]) if len(sys.argv) > 4 else None
sj = json.load(open(LOGS_DIR / f"pbeam_{RAW}.json"))
seg = [b.replace(",", "+") for b in sj["inputs"]]
n = len(seg)
res = json.load(open(FIX / f"u16b_sync_{OUT}.json"))["results"]
good = sorted((r for r in res if r[1] and (r[0] - OLDLEN) % 2 == 0 and (TS is None or r[3][1] == TS)), key=lambda r: (r[0], len(r[2])))
print(f"{len(good)} even-shift variants; lengths {sorted(set(r[0] for r in good))}; alignments {sorted(set(r[3][1] for r in good))}")
ln, ok, pr, ph = good[0]
pr = {int(k): v for k, v in pr.items()}
tail_input = lambda i: seg[i] if i < n else seg[n - 2 + (i - n) % 2]
add = lambda b, btn: b if btn in b.split("+") else (b + "+" + btn).lstrip("+")
full = [add(tail_input(i), pr[i]) if i in pr else tail_input(i) for i in range(ln)]
e = BizHawk(log_name=f"u16b_pick_{OUT}.log", fields={"level": 0x10, "x": 0x3FD, "hp": 0x51A, "lives": 0x11})
e.load(sj["bookmark"])
for b in full:
    s = e.step(bt(b), 1)
e.save(OUT + "_end0")
d = dict(sj)
d.update(inputs=full, built_from=RAW, sync_press={str(k): v for k, v in pr.items()}, alignment=ph)
if "placed" in d:
    d["placed"] = d["placed"] - n + ln
write_json(LOGS_DIR / f"pbeam_{OUT}.json", d)
print(f"wrote pbeam_{OUT}.json: {ln} inputs ({ln - n:+d} vs as built; {ln - OLDLEN:+d} vs the old segment), presses {pr}, alignment PC ${ph[0]:04X} ts {ph[1]}; "
      f"end level {s.level} hp {s.hp} lives {s.lives} x {s.x}; banned presses {sum(1 for x in full if banned(x))}; bookmark {OUT}_end0")
e.close()
