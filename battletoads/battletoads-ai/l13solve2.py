"""Armageddon solved for the EARLIEST CUT TO PROFESSOR T. BIRD (2026-10-09; replaces l13solve.py for the timing fix).

    python l13solve2.py <entry bookmark> <idle frames first> <out> [width=800] [macro=2] [select=1]
        -> logs/pbeam_<out>.json   inputs from the entry bookmark THROUGH the cut to T. Bird (the leaderboard's end):
           the fight (21 hits), the toad's step aside, Select presses during the Queen's rise (they re-roll her leftover
           timer, which sets the last scene's length), idle to her speech, A mash through it, idle to the cut.
           len(inputs) = frames from the entry to the T. Bird cut; 'kill_at', 'cut1_at', 'tbird_at', 'hits', 'tail' are stored.
        -> logs/l13solve2_<out>.txt  (progress), knowledge/l4s_<out>_beam.json (the beam's best lines every 50 frames),
           states/<out>_end.State (the frame of the cut)

Three stages:
  1. l13z_beam.search  - one time-bucketed beam for all 21 hits (2-frame decisions, Select as a dice re-roll, no damage);
     it runs on for L13_EXTRA (40) frames after the first kill and keeps every distinct kill state.
  2. l13z_tail.optimise - for the kill states in order of their best case: the ending, searched (see l13z_tail.py).
  3. a plain replay from the bookmark that must show 20 counted hits, the kill, full health, and the second
     level-byte 13 -> 254 change on the very last input; only then is the segment written.

The entry bookmark is the previous level's end state (e.g. L12g_end0); any state at Armageddon's entry works - re-run it
after The Revolution changes (the random numbers differ, so the fight must be searched again). Different <idle frames>
(0, 1, 2 ...) are different dice: run a few and keep the shortest. Width 800 takes ~50 min next to two other searches;
400 is ~25 min and ~20 frames worse. Use a FRESH <out> name every time (the script refuses to overwrite a segment).
Env: L13_EXTRA, L13_MAXC (kill states tried, 40), L13_SEEDS (4), L13_QUOTA, L13_MAXFRAMES, L13_FORCE=1 (overwrite).
Measured from L12g_end0 (2026-10-09): L13y0 (published) 2196 frames to the T. Bird cut; this solver 2021 (L13z3t)."""
import json
import os
import sys
import time

import l13z_beam as zb
from toads.emulator import LOGS_DIR, PROJECT

entry, k, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
width = int(sys.argv[4]) if len(sys.argv) > 4 else 800
M = int(sys.argv[5]) if len(sys.argv) > 5 else 2
select = int(sys.argv[6]) if len(sys.argv) > 6 else 1
seg_path = LOGS_DIR / f"pbeam_{out}.json"
if seg_path.exists() and not os.environ.get("L13_FORCE"):
    print("refusing to overwrite", seg_path, "- use a fresh <out> name")
    sys.exit(2)
logf = open(LOGS_DIR / f"l13solve2_{out}.txt", "a")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n"); logf.flush()


log(f"== l13solve2 {entry} idle {k} -> {out}: width {width}, macro {M}, select {select}  ({time.strftime('%Y-%m-%d %H:%M:%S')})")
e = zb.Emu(log_name=f"l13solve2_{out}.log")
e.load(entry)
pre = [""] * k
if os.environ.get("L13_PREFIX"):
    # polish mode: L13_PREFIX=<segment>:<hit number> - keep that segment's fight up to two frames after its hit N and search
    # the rest again from there (a narrower problem: the beam finds a few frames the full search left; see l13z_exp1.py)
    pseg, phit = os.environ["L13_PREFIX"].split(":")
    pj = json.load(open(LOGS_DIR / f"pbeam_{pseg}.json"))
    assert pj["bookmark"] == entry, "the prefix segment starts from another bookmark"
    pre = pj["inputs"][:pj["hits"][int(phit) - 1] + 2]
    log(f"polish: {pseg}'s first {len(pre)} inputs kept (through its hit {phit})")
k = len(pre)
for b in pre:
    e.step(tuple(v for v in b.split("+") if v), 1)
root_sid = e.msave()
root_f = e.feat()
log(f"root: level {root_f.lvl} lives {root_f.lives} hp {root_f.thp} toad ({root_f.tx},{root_f.th}) rng {root_f.rng.hex()}")
quota = tuple(float(v) for v in os.environ.get("L13_QUOTA", "0.72,0.23,0.05").split(","))
HP0 = 47                                                   # full health; the byte reads 0 for the first 10 frames (the toad is placed at 11)
cands, stats = zb.search(e, root_sid, root_f, width=width, M=M, select=select, log=log, quota=quota, hp0=HP0, t0_frames=k,
                         extra=int(os.environ.get("L13_EXTRA", 40)),
                         max_frames=int(os.environ.get("L13_MAXFRAMES", 1500)), ck_path=PROJECT / "knowledge" / f"l4s_{out}_beam.json")
log(f"search done: {stats['evals']} evals in {stats['seconds']:.0f}s; hit times {stats['first_hit_t']}; {len(cands)} kill candidates")
if not cands:
    log("unsolved")
    e.close()
    sys.exit(1)
# keep the fights of the best kill states on disk: if anything below fails, `python l13z_retail.py <that file> <out>` redoes the ending
os.makedirs(LOGS_DIR / "fix", exist_ok=True)
for i, (sc, c) in enumerate(cands[:5]):
    json.dump({"bookmark": entry, "inputs": pre + c.inputs(), "est_body_gone": sc, "her_h": c.f.qh, "timer": [c.f.qe1, c.f.qe2]},
              open(LOGS_DIR / "fix" / f"l13z_cand_{out}_{i}.json", "w"))

# ---- the ending for the kill candidates (l13z_tail.optimise: walk aside, Select presses during her rise so the leftover timer
#      wraps to 255 as early as it can, Select presses for the short speech load, A mash); candidates in order of the best
#      case, skipped once their best case cannot beat what is in hand
import l13z_tail as zt
quiet = lambda *a: None
results = []
best_total = None
tried = 0
MAXC = int(os.environ.get("L13_MAXC", 40))
seen_state = {}
for sc, c in cands:
    opt = k + c.t + zb.flight_est(c.f.qh) - 2 + zb.TAIL_BEST
    if best_total is not None and opt >= best_total:
        continue
    if tried >= MAXC:
        break
    sk = (c.f.qe1, c.f.qe2, c.f.qh, c.t)
    if sk in seen_state:
        continue
    seen_state[sk] = True
    tried += 1
    r = zt.optimise(e, c.sid, c.f, log=quiet, seed=1, budget=700, tops=2, waits=8)
    if r is None:
        log(f"  candidate t {c.t} (her h {c.f.qh}, timer {c.f.qe1}/{c.f.qe2}): no ending found")
        continue
    total = k + c.t + r["total"]
    log(f"  candidate t {c.t} (her h {c.f.qh}, timer {c.f.qe1}/{c.f.qe2}, toad x {c.f.tx}): rise +{r['rise_start']}, load {r['load']}, "
        f"last scene {r['scene']} (timer at the top {r['e2_top']}) -> T. Bird at {total}")
    results.append((total, c, r))
    if best_total is None or total < best_total:
        best_total = total
if not results:
    log("no candidate with an ending")
    e.close()
    sys.exit(1)
results.sort(key=lambda x: x[0])
final = None
for total, c, r in results[:3]:                           # polish the best three with more seeds
    for sd in range(2, 2 + int(os.environ.get("L13_SEEDS", 4))):
        if total <= k + c.t + zb.flight_est(c.f.qh) - 2 + zb.TAIL_BEST + 1:
            break
        r2 = zt.optimise(e, c.sid, c.f, log=quiet, seed=sd, budget=2000, tops=3, waits=12)
        if r2 is not None and k + c.t + r2["total"] < total:
            total, r = k + c.t + r2["total"], r2
    log(f"  polished: kill state t {c.t} -> T. Bird at {total} (load {r['load']}, last scene {r['scene']})")
    if final is None or total < final[0]:
        final = (total, c, r)
total, c, r = final
ins = pre + c.inputs() + r["inputs"]
log(f"chosen: kill state at search frame {c.t}; predicted T. Bird cut {total} frames after the entry")

# ---- verification: plain replay from the bookmark, frame by frame
e.load(entry)
prev = 13
hits, kill, cuts, hpmin, prevc, lv = [], None, [], 99, 0, 13
for n, b in enumerate(ins, 1):
    e.step(tuple(v for v in b.split("+") if v), 1)
    ram = e.ram_all()
    lv = ram[0x10]
    if not cuts:
        if n >= 12:
            hpmin = min(hpmin, ram[0x51A])
        if ram[0x586] > prevc and kill is None:
            hits.append(n)
        if kill is None and ram[0x586] >= 240 and any(ram[0x3C1 + sl] == zb.BODY for sl in range(2, 15)):
            kill = n
        prevc = ram[0x586]
    if lv != prev:
        if prev == 13 and lv == 254:
            cuts.append(n)
        prev = lv
ok = len(cuts) == 2 and cuts[1] == len(ins) and hpmin == HP0 and kill is not None and len(hits) == 20
log(f"replay from {entry}: hits at {hits}")
log(f"replay: kill at input {kill}, toad hp min {hpmin}, cut 1 (the Queen's speech) at {cuts[0] if cuts else None}, "
    f"cut to T. Bird at {cuts[1] if len(cuts) > 1 else None}; inputs {len(ins)}; {'VALID' if ok else 'NOT VALID'}")
if ok:
    e.save(out + "_end")
    json.dump({"bookmark": entry, "inputs": ins, "kill_at": kill, "cut1_at": cuts[0], "tbird_at": cuts[1], "hits": hits,
               "search": {"width": width, "macro": M, "select": select, "idle": k, "evals": stats["evals"], "seconds": round(stats["seconds"])},
               "tail": {kk: vv for kk, vv in r.items() if kk != "inputs"},
               "note": "ARMAGEDDON: the Dark Queen - 21 hits (RAM $586 counts 12 per hit; the 21st kills), no damage taken. After the last hit "
                       "the toad steps aside, Select presses during the Queen's rise re-roll her leftover timer so the last scene is as short "
                       "as it gets, the speech is skipped with A; the segment ends on the cut to Professor T. Bird (the leaderboard's end).||"
                       f"{len(ins)} frames to the T. Bird cut, kill at {kill}"},
              open(str(seg_path) + ".tmp", "w"))
    os.replace(str(seg_path) + ".tmp", seg_path)
    log(f"wrote {seg_path.name}: T. Bird cut {cuts[1]} frames after the entry (L13y0 from L12g_end0: 2196)")
e.close()
sys.exit(0 if ok else 1)
