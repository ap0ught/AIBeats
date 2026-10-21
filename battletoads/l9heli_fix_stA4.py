"""Stage A variants, part 4: roots 7816..7819, the dash-jump at frame j (tap hiccup 'Left' at j-1), first hiccup at h1 (or none), A frames n.
Rest = AB0 directions + b4.  Survivors that land on the floor: (root, h1, j, n) -> landing index, x.sub, spd, $466.  WANT marks values from
which ONE hop under the shaft ends on 118."""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
AB = T.AB["inputs"]; B4 = T.B4["inputs"]; ins = up14_inputs()
WANT = {87: 1, 159: 2, 205: 3, 60: 4, 180: 5, 59: 6, 219: 7, 152: 8}
e = BizHawk(log_name="l9heli_fix_stA4.log", fields=T.FLD)
tail = [x.replace("+A", "").replace("A", "") for x in AB][20:]          # after the three jump frames
out = []; seen = {}
for r0 in (7816, 7817, 7818, 7819):
    e.load("L9heli_7800")
    for f in range(OFF + 7800, OFF + r0): s = e.step(bt(ins[f]), 1)
    root = e.msave()
    for j in range(15, 21):
        for h1 in (None, 3, 4, 5, 6, 7, 8, 9):
            for n in range(1, 10):
                head = ["Right"] * (j - 1) + ["Left"] + ["Right+A"] * n
                if h1 is not None: head[h1] = "Left"
                seq = head + ["Right"] * max(0, 3 - n) + tail[max(0, n - 3) + (j - 17):] + B4 + ["Left"] * 6
                e.mload(root); land = None
                for i, b in enumerate(seq):
                    s = e.step(bt(b), 1)
                    if s.hp < 47 or s.an in CARRIED: break
                    if i > 100 and s.z == 0 and (s.h | s.hh << 8) == 6182: land = (r0 + i + 1, s.x | s.xh << 8, s.sub, s.spd, s.sh); break
                if land:
                    out.append(dict(root=r0, j=j, h1=h1, n=n, land=land, inputs=seq[:land[0] - r0]))
                    if land[4] not in seen or land[0] < seen[land[4]][0]: seen[land[4]] = (land[0], r0, j, h1, n, land)
                    if land[4] in WANT: print(f"root {r0} j {j} h1 {h1} n {n}: land {land} <== one hop k={WANT[land[4]]}", flush=True)
print(len(out), "survivors;", len(seen), "distinct landing $466:", sorted(seen), flush=True)
json.dump(out, open(LOGS_DIR / "fix" / "heli_stA4.json", "w"))
e.close()
