"""Walk The Revolution along the 1-player TAS from an exact sync point (2026-10-03): resync.py to the next TAS
landing (short legal prefix + the TAS's own inputs), check that any enemy the TAS hits in that stretch takes the
same hits (if not: try one idle frame inserted at a mid-air frame of the stretch - the enemies wake on a 4-frame
grid), and go on. Stops at the TAS's first banned press after `jstop` or when a stretch cannot be synced.
    python tasrun.py <bookmark at TAS index j0> <j0> <jstop> <out>   -> knowledge/tasrun_<out>.json (inputs from the bookmark), bookmark <out>_end
"""
import json, re, sys
from toads.emulator import BizHawk, LOGS_DIR, PROJECT
import resync
rows = resync.rows                                           # (f, x, h, z, an) placement-indexed
TAS = ["+".join(t) for t in resync.TAS]
log = [l for l in open("tas/watch_1p_l12.txt") if " x=" in l][24:]   # placement-indexed log lines
def foe_hp(l, ids):
    return tuple(int(h) for i, x, y, h, s in re.findall(r"([0-9a-f]{2}):(\d+),(\d+),(\d+),(\d+)", l) if int(i, 16) in ids)
IDS = {0x5c, 0x62}
bm, j0, jstop, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
ILL = lambda s: ("Left" in s and "Right" in s) or ("Up" in s and "Down" in s)
def landings(a, b):
    return [j for j in range(a + 1, b) if rows[j][3] == 0 and rows[j - 1][3] > 0]
inputs = []
cur_bm, j = bm, j0
e = BizHawk(log_name=f"tasrun_{out}.log")
while j < jstop:
    nxt = [x for x in landings(j + 25, min(jstop, j + 400))]
    if not nxt:
        print("no landing ahead", flush=True); break
    jcheck = nxt[0]
    ill = next((s for s in range(j + 1, jcheck + 1) if ILL(TAS[s])), None)
    if ill:
        print(f"the TAS presses a banned combination at {ill}: stopping at {j}", flush=True); break
    OC = None if __import__("os").environ.get("TASRUN_OBJCHECK") == "0" else (0x36, 0, 255)
    best = resync.run(cur_bm, j + 1, j + 40, jcheck, "R", 40, idle=False, objcheck=OC, stop_first=True, extend=True)
    if not best:
        best = resync.run(cur_bm, j + 1, j + 40, jcheck, "L", 40, idle=False, objcheck=OC, stop_first=True, extend=True)
    if not best:
        print(f"no resync from TAS {j} to {jcheck}", flush=True); break
    tot, jm, ins, jend = best
    # does the enemy take the TAS's hits in this stretch?
    tas_hits = [(s, foe_hp(log[s], IDS)) for s in range(j + 1, jend + 1) if sum(foe_hp(log[s], IDS)) < sum(foe_hp(log[s - 1], IDS))]   # blows, not spawns
    def play(seq):
        e.load(cur_bm); hits = []; prev = None
        for x in seq:
            e.step(tuple(v for v in x.split("+") if v), 1); m = e.ram(0, 0x800)
            hp = tuple(m[0x51A + q] for q in range(2, 15) if m[0x3C1 + q] in IDS)
            if hp != prev: hits.append(hp); prev = hp
            if m[0x51A] < 47 or m[0x11] < 6: return None
        m = e.ram(0, 0x800); return hits, (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475])
    want_end = rows[jend][1:4]
    res = play(ins)
    ok = res is not None and res[1] == want_end and (not tas_hits or (res[0] and res[0][-1] == tas_hits[-1][1]))
    if not ok and tas_hits:
        air = [i for i in range(len(ins)) if True]
        for p in range(0, len(ins), 2):                     # one idle frame inserted somewhere: the enemies' wake grid
            seq = ins[:p] + [""] + ins[p:]
            r2 = play(seq)
            if r2 is not None and r2[1] == want_end and r2[0] and r2[0][-1] == tas_hits[-1][1]:
                ins, res, ok = seq, r2, True; print(f"   fight fixed with an idle frame at +{p}", flush=True); break
    if not ok:
        print(f"stretch TAS {j}->{jend} does not reproduce (hits {tas_hits}, ours {res}); stopping at {j}", flush=True); break
    inputs += ins
    e.load(cur_bm)
    for x in ins: e.step(tuple(v for v in x.split("+") if v), 1)
    cur_bm = f"{out}_j{jend}"; e.save(cur_bm)
    print(f"TAS {j} -> {jend}: {len(ins)} frames (TAS {jend - j}); total {len(inputs)}", flush=True)
    j = jend
e.save(f"{out}_end")
json.dump({"bookmark": bm, "j0": j0, "jend": j, "inputs": inputs}, open(PROJECT / "knowledge" / f"tasrun_{out}.json", "w"))
print(f"saved knowledge/tasrun_{out}.json: TAS {j0} -> {j} in {len(inputs)} frames (TAS {j - j0})", flush=True)
e.close()
