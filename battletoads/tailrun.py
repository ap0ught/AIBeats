"""Carry the old route's tail on our timeline by repeated rejoins (2026-10-04). From our state at old frame f0
(a bookmark), replay the old inputs; at the first old landing we miss (x, h, z not equal), go back to the last
landing we matched and run rejoin.py's beam from there onto the old run's ground states after the miss; continue.
    python tailrun.py <our bookmark> <old frame f0> <out> [end]  -> knowledge/tail_<out>.json {f0, inputs}, bookmark TAIL_<out>"""
import json, os, sys, subprocess
from toads.emulator import BizHawk, LOGS_DIR
import shortcut as sc
sc.WRAP = 512
bm, f0, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]; end = int(sys.argv[4]) if len(sys.argv) > 4 else None
w = json.load(open(LOGS_DIR / "pbeam_L12w.json")); old = [x.replace(",", "+") for x in w["inputs"]]; end = end or len(old)
def key(m): return (sc.tx(m), m[0x439], m[0x475])
e2 = BizHawk(log_name=f"tailrun_ref_{out}.log"); e2.load("L12w_at5011"); ref = {}; pz = 0
for i, b in enumerate(old[5011:end]):
    e2.step(tuple(v for v in b.split("+") if v), 1); m2 = e2.ram(0, 0x800); f = 5011 + i + 1
    if m2[0x475] == 0 and pz > 0 and f > f0: ref[f] = key(m2)
    pz = m2[0x475]
    if m2[0x10] != 5: end = f; break
e2.close(); lands = sorted(ref); print(f"{len(lands)} old landings {f0}..{end}", flush=True)
e = BizHawk(log_name=f"tailrun_{out}.log"); e.load(bm)
inputs = []; cur_old = f0; cur_bm = bm; guard = 0
while cur_old < end and guard < 60:
    guard += 1
    e.load(cur_bm); seq = []; last_good = None; last_good_bm = None; miss = None; f = cur_old
    for b in old[cur_old:end]:
        e.step(tuple(v for v in b.split("+") if v), 1); seq.append(b); m = e.ram(0, 0x800); f += 1
        if m[0x51A] < 47 or m[0x11] < 4 or m[0x10] != 5: miss = f; break
        if f in ref:
            if key(m) == ref[f]:
                last_good = (f, len(seq)); e.save(f"TAILG_{out}"); last_good_bm = f"TAILG_{out}"
            else: miss = f; break
    if miss is None:
        inputs += seq; print("END reached: old inputs hold to", f, flush=True); break
    if last_good is None:
        print(f"no good landing between {cur_old} and the miss at {miss}; beam from {cur_old}", flush=True)
        start_bm, start_old, kept = cur_bm, cur_old, []
    else:
        start_bm, start_old, kept = last_good_bm, last_good[0], seq[:last_good[1]]
    print(f"miss at old {miss} (from {cur_old}); rejoin from old {start_old} into {max(start_old + 1, miss - 100)}..{miss + 320}", flush=True)
    env = dict(os.environ, RJ_FROM=str(start_old), SC_WRAP="512", SC_MAXLAYERS=os.environ.get("SC_MAXLAYERS", "340"))
    tag = f"{out}_{miss}"
    r = subprocess.run([sys.executable, "-u", "rejoin.py", start_bm, "L12w", "L12w_at5011", "5011", f"{max(start_old + 1, miss - 100)}-{miss + 320}", tag], env=env, capture_output=True, text=True)
    print(r.stdout[-600:], flush=True)
    if not os.path.exists(f"knowledge/rejoin_{tag}.json") or "saved" not in r.stdout:
        print("STUCK: no rejoin at", miss, flush=True); break
    rj = json.load(open(f"knowledge/rejoin_{tag}.json"))
    inputs += kept + rj["inputs"]; cur_old = rj["join"]; cur_bm = f"RJ_{tag}"
    json.dump({"f0": f0, "inputs": inputs, "old_at": cur_old}, open(f"knowledge/tail_{out}.json", "w"))
    print(f"   -> at old {cur_old}; ours {len(inputs)} frames so far (old {cur_old - f0})", flush=True)
json.dump({"f0": f0, "inputs": inputs, "old_at": cur_old, "end": end}, open(f"knowledge/tail_{out}.json", "w"))
e.load(bm)
for b in inputs: e.step(tuple(v for v in b.split("+") if v), 1)
e.save(f"TAIL_{out}"); print("saved TAIL_" + out, len(inputs), "frames; old reached", cur_old, "of", end, flush=True)
e.close()
