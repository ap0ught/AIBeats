"""The Revolution, the pole at x 480 (TAS 4778-5040, a waiting room): from a bookmark hanging on the pole, hang w more
frames (w = 0..300), then replay the TAS's own inputs from its last hanging frame j0 (drop, land on the circling
platform, bounce, launch); keep the w whose replay stays within 3 px of the TAS longest and ends on an exact landing.
    python polewait.py <bookmark> [j0] [out.json]"""
import json, sys
from toads.emulator import BizHawk, PROJECT
import resync as R
bm = sys.argv[1]; j0 = int(sys.argv[2]) if len(sys.argv) > 2 else 5040
out = sys.argv[3] if len(sys.argv) > 3 else "l12_polewait.json"
e = BizHawk(log_name="polewait.log"); e.load(bm); root = e.msave()
best = None
for w in range(0, 301):
    e.mload(root)
    for i in range(w): e.step((), 1)
    q = R.st(e.ram_all())
    if q[2] == 0 or q[4] < 47: continue                   # fell off / hurt while hanging
    tail, jend, cur = [], None, []
    for s in range(j0 + 1, len(R.TAS) - 1):
        if R.ILL(R.TAS[s]): break
        e.step(R.TAS[s], 1); q2 = R.st(e.ram_all()); t2 = R.rows[s]
        dx = min(abs(q2[0] - t2[1]), 512 - abs(q2[0] - t2[1])); dh = abs((q2[1] - t2[2] + 128) % 256 - 128)
        if dx > 3 or dh > 3 or q2[2] != t2[3] or q2[4] < 47: break
        cur.append("+".join(R.TAS[s]))
        if t2[3] == 0 and R.rows[s - 1][3] > 0 and q2[:4] == t2[1:5]:
            tail, jend = list(cur), s
    if jend and (best is None or jend > best[1] or (jend == best[1] and w < best[0])):
        best = (w, jend, [""] * w + tail)
        print(f"wait {w}: in sync to TAS {jend}", flush=True)
        (PROJECT / "knowledge" / out).write_text(json.dumps({"ins": best[2], "end": jend, "wait": w}))
print("best", None if not best else best[:2])
e.close()
