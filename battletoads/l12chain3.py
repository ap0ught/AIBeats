"""The Revolution tail on the NEW timeline (2026-10-04): l4s follow searches along the 1P TAS path from our state at
TAS row 4217 (bookmark L12_u4217_solved), the same way l12chain.py built the old route (kill sections for the
Hornheads 0x5c / walker 0x62). Sections are named L12_u<i0>; each starts from the previous section's solved state.
    python l12chain3.py            -> knowledge/l4s_L12_u<i0>.json per section, bookmarks L12_u<i0>_solved"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path
P = Path(__file__).parent
W = int(os.environ.get("L12_WIDTH", 250))
def KILL(foe): return {"L4S_RATDEAD": "1", "L4S_FOEID": foe, "L4S_FOEW": "20", "L4S_FOEDX": "2"}
PLAN = [(4217, 4360, None), (4360, 4500, None), (4500, 4610, "0x5c"), (4610, 4910, None), (4910, 5200, None), (5200, 5350, "0x5c"),
        (5350, 5650, None), (5650, 5730, "0x62"), (5730, 6030, None), (6030, 6330, None), (6330, 6630, None), (6630, 6930, None), (6930, 7262, None)]
HS = json.load(open(P / "knowledge" / "tas_l12_H.json"))
ENDS = P / "knowledge" / "l12u_ends.json"
done = ["L12_u4217"]
for i0, i1, foe in PLAN:
    bm = f"L12_u{i0}" + ("k" if foe else "")
    js = P / "knowledge" / f"l4s_{bm}.json"; log = P / "logs" / f"l4s_{bm}.txt"
    if js.exists(): done.append(bm); print(bm, "already solved", flush=True); continue
    ends = json.loads(ENDS.read_text()) if ENDS.exists() else {}
    if done[-1] in ends:
        if i1 <= ends[done[-1]] + 20: print(bm, "covered, skipped", flush=True); continue
        i0 = ends[done[-1]]
    shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    hroot = HS[i0]
    env = dict(os.environ, L4S_LVL="5", L4S_XWRAP="512", L4S_ACTS="rev", L4S_AIRB="1", L4S_SAFE="20", L4S_STEPS="200",
               L4S_FOLLOW=f"{i0},{i1}", L4S_HROOT=str(hroot), L4S_TASLOG="tas/watch_1p_l12.txt", L4S_PLACE="136,30", L4S_MACRO="4", L4S_SPDKEY="1")
    if foe: env.update(KILL(foe))
    print(f"{bm}: TAS {i0}->{i1}, H root {hroot}", flush=True)
    with open(log, "w") as f:
        subprocess.run([sys.executable, "l4s.py", bm, "0", "0", str(W), "follow"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = log.read_text()
    print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
    if js.exists(): done.append(bm); continue
    # fallback: resync from the section's root to the next TAS landing after i1
    import resync
    land = [j for j in range(i1 - 40, i1 + 60) if resync.rows[j][3] == 0 and resync.rows[j - 1][3] == 8]
    jcheck = land[0] if land else i1
    best = None
    for dirc in ("R", "L"):
        b = resync.run(f"{done[-1]}_solved", i0, jcheck - 20, jcheck, dirc, 40, idle=False)
        if b and (best is None or b[0] < best[0]): best = b
    if best:
        from toads.emulator import BizHawk
        e = BizHawk(log_name=f"script_{bm}.log"); e.load(f"{done[-1]}_solved")
        for s in best[2]: e.step(tuple(v for v in s.split("+") if v), 1)
        e.save(f"{bm}_solved"); e.close(); js.write_text(json.dumps(best[2]))
        ends = json.loads(ENDS.read_text()) if ENDS.exists() else {}; ends[bm] = best[3]; ENDS.write_text(json.dumps(ends))
        print(bm, f"re-synced: {len(best[2])} frames (TAS {best[3]})", flush=True); done.append(bm); continue
    print(bm, "FAILED; stopping", flush=True); break
print("chain done:", done, flush=True)
