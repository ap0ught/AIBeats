"""The Revolution chain (journal 012): L12_r1 = the 1-player TAS replayed exactly (857 frames, all legal), then
scripted legal replacements for the TAS's Left+Right presses and follow searches on the TAS path in between.
Rows: ("SCRIPT", bookmark, inputs) = fixed inputs from the previous solved state + 2 idle frames;
      (bookmark, i_from, i_to, width, steps, macro[, env]) = a follow search (l4s.py follow, rev actions).
A row with an existing knowledge/l4s_<bm>.json is skipped.      python l12chain.py"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
P = Path(__file__).parent
L, N, LA = "Left", "", "Left+A"
# cluster 1 (TAS step 861, Left+Right+A = an instant-sprint jump left): the toad lands off the spring facing right.
# A legal sprint needs the toad to face the run direction and the double tap to start after the 6-frame turn:
# Left, 5 idle, Left, idle, then Left+A held (21 frames, as the TAS) -> lands on the x-187 platform 6 frames late.
SPRINT1 = [L, N, N, N, N, N, L, N] + [LA] * 21 + [L] * 16
# after the kill the toad stands on the sinking platform (x 316), 10 px off the TAS's launch spot, and no beam found
# the launch (bounce the platform with A while double-tapping, snap onto the ring ledge at x 385, sprint-jump to x 35).
# Exact fix: walk Left 68 f to the floor, double-tap Right + 5 f, then the TAS's own inputs 1344..1459 (they sync).
_T = json.load(open(P / "knowledge" / "tas1p_l12_inputs.json"))
F1S = [L] * 68 + ["Right", "", "Right"] + ["Right"] * 5 + _T[1344:1460]
ROWS = [("SCRIPT", "L12_r2", SPRINT1)]
W = int(os.environ.get("L12_WIDTH", 250))                  # beam width (400 for f0/f1; retry a failed section with 400)
ROWS += [("L12_f0", 897, 1197, 400, 200, 4),
         # the Hornhead (0x5c, hp 47, 16 per hit) must die: while it lives the camera won't scroll up and the
         # ledge at x 385 (TAS 1403) never appears. Skipping it (L12_f1a_skipfoe) dead-ends there.
         ("L12_f1k", 1197, 1320, 400, 200, 4, {"L4S_RATDEAD": "1", "L4S_FOEID": "0x5c", "L4S_FOEW": "20", "L4S_FOEDX": "1"}),
         ("SCRIPT", "L12_f1s", F1S)]                       # back down to the floor and redo the TAS's approach exactly
def KILL(foe):                                              # a kill section: damage on the foe outranks path progress; goal = its hp 0
    return {"L4S_RATDEAD": "1", "L4S_FOEID": foe, "L4S_FOEW": "20", "L4S_FOEDX": "2"}
# the TAS's kills after 1497 (logs: 5c = Hornhead, 62 = the other walker; 16 hp per hit) -> kill rows, follow rows between
PLAN = [(1459, 1640, "0x5c"), (1640, 1920, None), (1829, 1920, None), (1920, 2000, "0x62"), (2000, 2120, None), (2120, 2230, "0x5c"),
        (2230, 2390, None), (2390, 2500, "0x5c"), (2500, 2800, None), (2800, 3080, None), (3080, 3160, "0x62"),
        (3160, 3290, None), (3290, 3460, None, {"macro": 2}), (3442, 3600, None, {"macro": 2}), (3600, 3760, None), (3760, 4060, None), (4060, 4360, None), (4360, 4500, None),
        (4500, 4610, "0x5c"), (4610, 4910, None), (4910, 5200, None), (5200, 5350, "0x5c"), (5350, 5650, None),
        (5650, 5730, "0x62"), (5730, 6030, None), (6030, 6330, None), (6330, 6630, None), (6630, 6930, None),
        (6930, 7262, None)]
for item in PLAN:
    i0, i1, foe = item[:3]
    ov = item[3] if len(item) > 3 else {}
    if ov.get("macro"):                                     # finer steps (a platform circling the tower at 2 px/f)
        ROWS.append((f"L12_g{i0}", i0, i1, W, 300, ov["macro"], KILL(foe) if foe else {}))
        continue
    if (i0, foe) == (3080, "0x62"):
        # the 111-hp walker (7 hits) the TAS fights from the bouncing platform at x 487: it only walks over when the
        # RNG says so (inputs move the RNG); a found trigger (73 f of Select/Down/A/Up) + the TAS's own fight inputs
        # leave it at 31 hp with the toad unhurt; a kill section fenced to the platform side finishes it
        ROWS.append(("SCRIPT", "L12_g3080a", json.load(open(P / "knowledge" / "l12_fight62_part.json"))))
        ROWS.append(("L12_g3080b", 3140, 3160, W, 200, 4, dict(KILL(foe), L4S_FORBID="0,465,-99999,99999", L4S_FOEDX="0")))
        continue
    ROWS.append((f"L12_g{i0}" + ("k" if foe else ""), i0, i1, W, 200, 4, KILL(foe) if foe else {}))
BASE = ["L12_r1"]
done = list(BASE)

def run_script(bm, ins, idle=True):
    from toads.emulator import BizHawk
    e = BizHawk(log_name=f"script_{bm}.log"); e.load(f"{done[-1]}_solved")
    if idle:
        e.step((), 2)
    ni = P / "knowledge" / "l12_noidle.json"
    lst = set(json.loads(ni.read_text())) if ni.exists() else set()
    (lst.discard(bm) if idle else lst.add(bm)); ni.write_text(json.dumps(sorted(lst)))
    for s in ins:
        e.step(tuple(b for b in s.split("+") if b), 1)
    r = e.ram_all()
    e.save(f"{bm}_solved"); e.close()
    (P / "knowledge" / f"l4s_{bm}.json").write_text(json.dumps(ins))
    shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    return r


ENDS = P / "knowledge" / "l12_ends.json"                  # spliced sections -> the TAS frame they end on

def set_end(bm, j):
    ends = json.loads(ENDS.read_text()) if ENDS.exists() else {}
    ends[bm] = j; ENDS.write_text(json.dumps(ends))

def beam_resync(bm, i0, i1):
    """take the failed beam's best line, and from each of its last landings (latest first) re-sync with the TAS"""
    import resync
    from toads.emulator import BizHawk
    bj = P / "knowledge" / f"l4s_{bm}_best.json"
    if not bj.exists():
        return False
    ins = json.loads(bj.read_text())
    e = BizHawk(log_name=f"beamres_{bm}.log"); e.load(f"{done[-1]}_solved"); e.step((), 2)
    tr = []
    for s_ in ins:
        e.step(tuple(b for b in s_.split("+") if b), 1); r = e.ram_all()
        tr.append((r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x475], r[0x51A]))
    lands = [f for f in range(1, len(tr)) if tr[f][2] == 0 and tr[f - 1][2] > 0 and tr[f][3] >= 47][::-1][:6]
    R = resync.rows
    tl = [j for j in range(max(i0 - 10, 1), min(i1 + 120, len(R) - 1)) if R[j][3] == 0 and R[j - 1][3] > 0]
    for f in lands:
        x, h = tr[f][0], tr[f][1]
        cand = [(min(abs(R[j][1] - x), 512 - abs(R[j][1] - x)) + abs((R[j][2] - h + 128) % 256 - 128), -j, j) for j in tl]
        cand = [c for c in cand if c[0] <= 8]
        if not cand:
            continue
        j = min(cand)[2]
        nxt = [k for k in tl if j + 20 < k <= j + 200]
        if not nxt:
            continue
        jcheck = nxt[0]
        e.load(f"{done[-1]}_solved"); e.step((), 2)
        for s_ in ins[:f + 1]:
            e.step(tuple(b for b in s_.split("+") if b), 1)
        e.save(f"{bm}_m")
        print(bm, f"beam re-sync: landing at beam frame {f} (x {x} h {h}) ~ TAS {j}; target TAS {jcheck}", flush=True)
        best = None
        for dirc in ("L", "R"):
            b = resync.run(f"{bm}_m", j - 6, j + 30, jcheck, dirc, 8, objcheck=(0x36, 0, 255), idle=False)
            if b and (best is None or b[0] < best[0]):
                best = b
        if best:
            e.close()
            full = ins[:f + 1] + best[2]
            r = run_script(bm, full)
            set_end(bm, best[3])
            print(bm, f"beam re-synced: {len(full)} frames -> x {r[0x3FD] + 256 * r[0x3EE]} h {r[0x439]} (TAS {best[3]})", flush=True)
            return True
    e.close()
    return False

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for row in ROWS:
        if row[0] == "SCRIPT":
            _, bm, ins = row
            if not (P / "knowledge" / f"l4s_{bm}.json").exists():
                r = run_script(bm, ins)
                print(bm, f"scripted {len(ins)} frames -> x {r[0x3FD] + 256 * r[0x3EE]} h {r[0x439]} z {r[0x475]} hp {r[0x51A]}", flush=True)
            done.append(bm); continue
        bm, i0, i1, width, steps, macro = row[:6]
        extra = row[6] if len(row) > 6 else {}
        log = P / "logs" / f"l4s_{bm}.txt"; js = P / "knowledge" / f"l4s_{bm}.json"
        if js.exists():
            done.append(bm); print(bm, "already solved", flush=True); continue
        ends = json.loads(ENDS.read_text()) if ENDS.exists() else {}
        if done[-1] in ends:                                # the previous section was spliced and ends at a known TAS frame
            if i1 <= ends[done[-1]] + 20:
                print(bm, f"covered by {done[-1]} (ends at TAS {ends[done[-1]]}), skipped", flush=True); continue
            i0 = ends[done[-1]]
        if log.exists() and not any(w in log.read_text() for w in ("solved", "unsolved")):
            print(bm, "running elsewhere, waiting", flush=True)
            while not any(w in log.read_text() for w in ("solved", "unsolved")):
                time.sleep(20)
        else:
            out = subprocess.run([sys.executable, "l12.py", *done], cwd=P, capture_output=True, text=True).stdout
            hroot = int(re.findall(r"section \S+: \d+ frames -> f\d+ H (-?\d+)", out)[-1])
            shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
            print(f"{bm}: root H {hroot}, 1P TAS {i0}->{i1}", flush=True)
            env = dict(os.environ, L4S_LVL="5", L4S_XWRAP="512", L4S_ACTS="rev", L4S_AIRB="1", L4S_SAFE="20", L4S_STEPS=str(steps),
                       L4S_FOLLOW=f"{i0},{i1}", L4S_HROOT=str(hroot), L4S_TASLOG="tas/watch_1p_l12.txt", L4S_PLACE="136,30",
                       L4S_MACRO=str(macro), L4S_SPDKEY="1")
            env.update(extra)
            with open(log, "w") as f:
                subprocess.run([sys.executable, "l4s.py", bm, "0", "0", str(width), "follow"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
        txt = log.read_text()
        print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
        if js.exists():
            done.append(bm); continue
        if extra:
            break                                           # kill sections: no automatic fallback
        # fallback 1: the beam's own best line up to one of its landings, then a re-sync with the TAS from there
        if beam_resync(bm, i0, i1):
            done.append(bm); continue
        # fallback 2: a re-sync from the section's root
        import resync
        land = [j for j in range(i1 - 40, i1 + 60) if resync.rows[j][3] == 0 and resync.rows[j - 1][3] == 8]
        jcheck = land[0] if land else i1
        print(bm, f"follow failed: re-sync search TAS {i0}..{jcheck - 20} -> {jcheck}", flush=True)
        best = None
        for dirc in ("R", "L"):
            b = resync.run(f"{done[-1]}_solved", i0, jcheck - 20, jcheck, dirc, 40, idle=False)
            if b and (best is None or b[0] < best[0]):
                best = b
        if not best:                                        # moving platforms: also require the 0x36 objects where the TAS had them
            print(bm, "re-sync with platform positions", flush=True)
            for dirc in ("R", "L"):
                b = resync.run(f"{done[-1]}_solved", i0, jcheck - 20, jcheck, dirc, 40, objcheck=(0x36, 0, 255), idle=False)
                if b and (best is None or b[0] < best[0]):
                    best = b
        if best:
            r = run_script(bm, best[2], idle=False)
            set_end(bm, best[3])
            print(bm, f"re-synced: {len(best[2])} frames -> x {r[0x3FD] + 256 * r[0x3EE]} h {r[0x439]} (TAS {best[3]})", flush=True)
            done.append(bm); continue
        break
