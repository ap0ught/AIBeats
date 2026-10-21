"""Board a moving platform so that the toad AND the platform match a TAS frame exactly, then replay the TAS's own
inputs while in sync (3 px tolerance), ending on its last exactly matching landing.
    python boardsync.py <bookmark> <jlo> <jhi> <plat_id hex> <out.json> [idle 0|1] [maxw]"""
import json, sys
from toads.emulator import BizHawk, PROJECT
import resync as R
bm, jlo, jhi, pid, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4], 16), sys.argv[5]
idle = len(sys.argv) > 6 and sys.argv[6] == "1"; maxw = int(sys.argv[7]) if len(sys.argv) > 7 else 300
OC = (pid, 0, 255)
e = BizHawk(log_name=f"boardsync_{bm}.log"); e.load(bm)
if idle: e.step((), 2)
root = e.msave()
idx = {}
for j in range(jlo, jhi + 1):
    idx.setdefault(R.rows[j][1:5], []).append(j)
def sig(r): return R.objsig([(r[0x3C1+k], r[0x3FD+k]+256*r[0x3EE+k], r[0x439+k]) for k in range(2, 15)], OC)
N, A, L, Rt = (), ("A",), ("Left",), ("Right",)
JUMPS = [(A, L), (A, Rt), (A, N), (("Left", "A"), L), (("Right", "A"), Rt), (L, L), (Rt, Rt), (N, N)]
best = None
for w in range(0, maxw):
    e.mload(root)
    for i in range(w): e.step(N, 1)
    ws = e.msave()
    for jb, drift in JUMPS:
        for k in (1, 2, 4, 6, 9, 12, 16, 20):
            e.mload(ws); seq = [N] * w
            for b in [jb] * k + [drift] * 50:
                e.step(b, 1); seq.append(b); r = e.ram_all(); q = R.st(r)
                if q[4] < 47: break
                for j in idx.get(q[:4], []):
                    if sig(r) != R.objsig(R.objs[j], OC): continue
                    sid = e.msave(); cur = []; tail = []; jend = None
                    for s in range(j + 1, len(R.TAS) - 1):
                        if R.ILL(R.TAS[s]): break
                        e.step(R.TAS[s], 1); q2 = R.st(e.ram_all()); t2 = R.rows[s]
                        dx = min(abs(q2[0] - t2[1]), 512 - abs(q2[0] - t2[1])); dh = abs((q2[1] - t2[2] + 128) % 256 - 128)
                        if dx > 3 or dh > 3 or q2[2] != t2[3] or q2[4] < 47: break
                        cur.append("+".join(R.TAS[s]))
                        if t2[3] == 0 and R.rows[s - 1][3] > 0 and q2[:4] == t2[1:5]: tail, jend = list(cur), s
                    e.mload(sid); e.mfree(sid)
                    if jend and (best is None or jend > best[1] or (jend == best[1] and len(seq) + len(tail) < best[0])):
                        best = (len(seq) + len(tail), jend)
                        (PROJECT / "knowledge" / out).write_text(json.dumps({"ins": ["+".join(b) for b in seq] + tail, "end": jend}))
                        print(f"MATCH at TAS {j} after {len(seq)} f (wait {w}); TAS inputs keep sync to {jend}", flush=True)
    if best and w > best[0]: break
print("best", best)
e.close()
