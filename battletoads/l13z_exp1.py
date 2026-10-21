"""Sub-search experiment: from a mid-fight state of a finished segment (after its hit <h0>), how fast do different beam
settings reach the next hits?   python l13z_exp1.py <segment> <h0> <frames> <width> <fd> <quota>"""
import json, sys
import l13z_beam as zb
from toads.emulator import LOGS_DIR
seg, h0, frames, width = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
zb.FD = float(sys.argv[5]) if len(sys.argv) > 5 else 0.25
quota = tuple(float(v) for v in sys.argv[6].split(",")) if len(sys.argv) > 6 else (0.72, 0.23, 0.05)
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
t0 = j["hits"][h0 - 1] + 2
e = zb.Emu(log_name=f"l13z_exp1_{width}_{sys.argv[5] if len(sys.argv) > 5 else 'd'}.log")
e.load(j["bookmark"])
for b in j["inputs"][:t0]:
    e.step(tuple(v for v in b.split("+") if v), 1)
f = e.feat(); sid = e.msave()
print(f"{seg} after hit {h0} (input {t0}): hits {f.hits}; the segment's own next hits at", [h - t0 for h in j["hits"][h0:h0 + 6]], "kill", j["kill_at"] - t0, flush=True)
cands, stats = zb.search(e, sid, f, width=width, M=2, select=1, log=lambda *a: None, quota=quota, max_frames=frames, t0_frames=t0, extra=0)
print(f"width {width} fd {zb.FD} quota {quota}: first reached {dict(sorted(stats['first_hit_t'].items()))}; kills {[(c.t, c.f.qh) for _, c in cands[:3]]}; {stats['evals']} evals {stats['seconds']:.0f}s", flush=True)
e.close()
