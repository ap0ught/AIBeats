"""Stage A variants, part 2: prepend d idle frames on the upper step (normal ground: $466 changes 79 per frame there) and vary the A-window
length n of the tunnel jump; the rest of the AB0 + b4 inputs unchanged.  Survivors: landing frame, x.sub, speed, landing $466.
Wanted landing $466 for a single hop under the shaft to end on 118: k1 87, k2 159, k3 205, k4 60, k5 180, k6 59, k7 219, k8 152."""
import json, sys
from l9heli_fix_lib import *
import l9heli_fix_tail as T
AB = T.AB["inputs"]; B4 = T.B4["inputs"]
WANT = {87: 1, 159: 2, 205: 3, 60: 4, 180: 5, 59: 6, 219: 7, 152: 8}
e = BizHawk(log_name="l9heli_fix_stA2.log", fields=T.FLD); e.load("L9heli_7819"); root = e.msave()
dirs = [x.replace("+A", "").replace("A", "") for x in AB]
out = []
for d in range(0, 49):
    for where in ("start", "mid"):
        for n in range(1, 10):
            seq = []
            for i, dd in enumerate(dirs):
                seq.append((dd + "+A").strip("+") if 17 <= i < 17 + n else dd)
            seq = ([""] * d + seq) if where == "start" else (seq[:7] + ["Right"] * 0 + seq[7:])
            if where == "mid":
                if d == 0: continue
                seq = seq[:16] + [""] * 0 + seq[16:]          # (placeholder: only the start delay is used)
                continue
            e.mload(root); dead = None
            for i, b in enumerate(seq + B4):
                s = e.step(bt(b), 1)
                if s.hp < 47 or s.an in CARRIED: dead = i + 1; break
            if dead: continue
            H = s.h | s.hh << 8
            r = dict(d=d, n=n, frames=len(seq + B4), x=s.x | s.xh << 8, sub=s.sub, H=H, z=s.z, spd=s.spd, sh=s.sh, inputs=seq + B4)
            out.append(r)
            print(f"d {d} n {n}: end frame {r['frames']} x {r['x']}.{r['sub']} H {H} z {s.z} spd {s.spd} $466 {s.sh}", "<== k%d" % WANT[s.sh] if (s.sh in WANT and s.z == 0) else "", flush=True)
json.dump(out, open(LOGS_DIR / "fix" / "heli_stA2.json", "w"))
e.close()
