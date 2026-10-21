"""Give an existing queen segment (any segment whose 21st hit is known) the optimised ending:
    python l13z_retail.py <segment> <out> [budget=1500] [seeds=3]
Replays the segment's fight from its bookmark to the kill, runs l13z_tail.optimise (walk away, Select presses during the
queen's rise so her leftover timer reaches the top just above 228, Select presses for the short speech load, A mash),
writes logs/pbeam_<out>.json = fight + new tail THROUGH the cut to T. Bird, and checks it by a plain replay."""
import json, os, sys, time
import l13z_beam as zb, l13z_tail as zt
from toads.emulator import LOGS_DIR

seg, out = sys.argv[1], sys.argv[2]
budget = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
seeds = int(sys.argv[4]) if len(sys.argv) > 4 else 3
dst = LOGS_DIR / f"pbeam_{out}.json"
if dst.exists() and not os.environ.get("L13_FORCE"):
    print("refusing to overwrite", dst); sys.exit(2)
logf = open(LOGS_DIR / "fix" / f"l13z_retail_{out}.txt", "a")
def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); logf.write(s + "\n"); logf.flush()
j = json.load(open(seg if seg.endswith(".json") else LOGS_DIR / f"pbeam_{seg}.json"))    # a segment name, or a path (l13z_cand_*.json)
ins = j["inputs"]
e = zb.Emu(log_name=f"l13z_retail_{out}.log")
e.load(j["bookmark"])
kill = None
for n, b in enumerate(ins, 1):
    e.step(tuple(v for v in b.split("+") if v), 1)
    if n > 300 and n % 1 == 0:
        f = e.feat()
        if f.killed:
            kill = n; break
if kill is None:
    log("no kill found in", seg); sys.exit(1)
sid = e.msave()
log(f"== retail {seg} -> {out}: kill state after input {kill}: her h {f.qh}, timer state {f.qe1}/{f.qe2}, toad x {f.tx}")
best = None
for sd in range(1, seeds + 1):
    t0 = time.time()
    r = zt.optimise(e, sid, f, log=log, seed=sd, budget=budget, tops=3)
    if r is None:
        continue
    log(f"  seed {sd}: T. Bird at {kill + r['total']} (rise starts +{r['rise_start']}, speech load {r['load']}, last scene {r['scene']}, timer at the top {r['e2_top']}) {time.time() - t0:.0f}s")
    if best is None or r["total"] < best["total"]:
        best = r
new = ins[:kill] + best["inputs"]
# plain replay check
e.load(j["bookmark"])
prev, cuts, hits, k2, hpmin, prevc = 13, [], [], None, 99, 0
for n, b in enumerate(new, 1):
    e.step(tuple(v for v in b.split("+") if v), 1)
    r = e.ram_all()
    if not cuts:
        if n >= 12: hpmin = min(hpmin, r[0x51A])
        if r[0x586] > prevc and k2 is None: hits.append(n)
        if k2 is None and r[0x586] >= 240 and any(r[0x3C1 + s] == zb.BODY for s in range(2, 15)): k2 = n
        prevc = r[0x586]
    if r[0x10] != prev:
        if prev == 13 and r[0x10] == 254: cuts.append(n)
        prev = r[0x10]
ok = len(cuts) == 2 and cuts[1] == len(new) and hpmin == 47 and k2 is not None and len(hits) == 20
log(f"replay: hits {hits}")
log(f"replay: kill at {k2}, toad hp min {hpmin}, cut 1 at {cuts[0] if cuts else None}, cut to T. Bird at {cuts[1] if len(cuts) > 1 else None}; inputs {len(new)}; {'VALID' if ok else 'NOT VALID'}")
if ok:
    e.save(out + "_end")
    json.dump({"bookmark": j["bookmark"], "inputs": new, "kill_at": k2, "cut1_at": cuts[0], "tbird_at": cuts[1], "hits": hits,
               "tail": {k: v for k, v in best.items() if k != "inputs"}, "from_segment": os.path.basename(seg),
               "note": "ARMAGEDDON: the Dark Queen - 21 hits, no damage taken. After the last hit the toad steps aside, Select presses "
                       "during the Queen's rise re-roll her leftover timer so the last scene is as short as it gets, the speech is "
                       "skipped with A; the segment ends on the cut to Professor T. Bird (the leaderboard's end).||"
                       f"{len(new)} frames to the T. Bird cut, kill at {k2}"},
              open(str(dst) + ".tmp", "w"))
    os.replace(str(dst) + ".tmp", dst)
    log(f"wrote {dst.name}: T. Bird cut {cuts[1]} frames after the entry (L13y0 from L12g_end0 was 2196)")
e.close()
sys.exit(0 if ok else 1)
