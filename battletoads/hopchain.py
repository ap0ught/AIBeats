"""Hop from platform to platform: for each target (object id, x), search wait w, run-up r, jump (A held k frames,
direction d in the air) until the toad lands on the target's top; chain the targets; stop early if an end object
appears.   python hopchain.py <bookmark> <out.json> <id:x,id:x,...> [endobj hex]"""
import json, sys
from toads.emulator import BizHawk, PROJECT
import resync as R
bm, out = sys.argv[1], sys.argv[2]
targets = [(int(t.split(":")[0], 16), int(t.split(":")[1])) for t in sys.argv[3].split(",")]
endobj = int(sys.argv[4], 16) if len(sys.argv) > 4 else None
N, L, Rt, A = (), ("Left",), ("Right",), ("A",)
def objs(r): return [(r[0x3C1+s], r[0x3FD+s]+256*r[0x3EE+s], r[0x439+s]) for s in range(2, 15) if r[0x3C1+s]]
def on(r, tid, tx):
    q = R.st(r)
    if q[2] != 0: return False
    for i, x, h in objs(r):
        if i == tid and x == tx and min(abs(q[0]-x), 512-abs(q[0]-x)) <= 18 and 0 <= (q[1] - h) % 256 <= 12: return True
    return False
def ended(r): return endobj is not None and any(i == endobj for i, x, h in objs(r))
seq_all = []
e = BizHawk(log_name=f"hopchain_{bm}.log"); e.load(bm)
for tid, tx in targets:
    root = e.msave(); best = None
    for w in range(0, 260, 2):
        if best and w > best[0]: break
        e.mload(root)
        dead = False
        for i in range(w):
            e.step(N, 1)
            if R.st(e.ram_all())[4] < 47 or e.ram_all()[0x475] != 0: dead = True; break
        if dead: break
        ws = e.msave()
        for d in (N, L, Rt):
            for k in range(2, 26, 2):
                for steer in (N, L, Rt):
                    e.mload(ws); seq = [N] * w + [d + A] * k + [steer] * 60; air = False
                    for i, b in enumerate(seq[w:]):
                        e.step(b, 1); r = e.ram_all(); q = R.st(r)
                        if q[4] < 47 or q[5] < 6: break
                        if ended(r): best = (w + i + 1, seq[:w + i + 1], "END"); break
                        if q[2] > 0: air = True
                        if air and q[2] == 0:
                            if on(r, tid, tx) and (best is None or w + i + 1 < best[0]): best = (w + i + 1, seq[:w + i + 1], q[:4])
                            break
                    if best and best[2] == "END": break
                if best and best[2] == "END": break
            if best and best[2] == "END": break
        e.mfree(ws)
        if best and best[2] == "END": break
    e.mfree(root)
    if not best: print("no way onto", hex(tid), tx, flush=True); break
    print(f"onto {hex(tid)}@{tx}: {best[0]} frames -> {best[2]}", flush=True)
    e.mload(root) if False else None
    e.load(bm) if False else None
    # replay the whole chain so far from the bookmark to continue from the real state
    seq_all += best[1]
    (PROJECT / "knowledge" / out).write_text(json.dumps(["+".join(b) for b in seq_all]))
    e.close()
    import time
    for attempt in range(4):
        try:
            time.sleep(3); e = BizHawk(log_name=f"hopchain_{bm}_{len(seq_all)}.log"); break
        except RuntimeError as ex:
            print("emulator restart failed, retrying", flush=True)
    e.load(bm)
    for b in seq_all: e.step(b, 1)
    if best[2] == "END": print("END OBJECT appeared"); break
e.close()
print("total", len(seq_all))
