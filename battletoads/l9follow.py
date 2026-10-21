"""Terra Tubes follow chain on FODA's 1-player TAS path (tas/watch_1p_log.txt).
Rows: (bookmark, i_from, i_to, width, steps, macro) = a follow search; or ("WAIT", bookmark, obj_id, obj_x) = a
scripted wait (idle from the previous solved state until object obj_id at x obj_x is gone — e.g. a wall a gear
smashes). A row starts from the previous row's solved state; rows with an existing json are skipped.
    python l9follow.py"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
P = Path(__file__).parent
BASE = ["L9_s1", "L9_s1wait", "L9_s2b", "L9_s3cut", "L9_pipe", "L9_p2", "L9_gear"]
ROWS = [(f"L9_p{k}", 1085 + 300 * (k - 3), 1085 + 300 * (k - 2), 400, 200, 4) for k in range(3, 10)]   # p3..p9 (solved)
ROWS += [("L9_p10a", 3185, 3288, 400, 200, 4),              # down to the waiting spot (1388, -970) under gear 2's floor
         ("WAIT", "L9_p10w", 0x3f, 1436, 1388),             # step back to x 1388 (out of the gear's column), wait for it to smash the wall at x 1436
         ("L9_p10b", 3370, 3685, 400, 200, 4)]              # crouch-slide through, on down
ROWS += [(f"L9_q{k}", 3685 + 300 * k, 3685 + 300 * (k + 1), 400, 200, 4) for k in range(0, 7)]    # q0..q6 (solved)
GEAR = lambda r: [(r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s]) for s in range(2, 15) if r[0x3C1 + s] == 0x6b]
ROWS += [("L9_q7a", 5785, 5916, 400, 200, 4),              # to x 211 beside gear 3's column (x 192)
         ("WAITC", "L9_q7w", 211, lambda r: any(gx <= 186 and gh == 192 for gx, gh in GEAR(r))),   # until the gear rolls left past 186
         ("L9_q7b", 5976, 6285, 400, 200, 4)]              # follow behind it
ROWS += [(f"L9_q{k}", 6285 + 300 * (k - 8), 6285 + 300 * (k - 7), 400, 200, 4) for k in range(8, 11)]   # q8, q9, q10
ROWS += [("L9_q11a", 7185, 7200, 400, 100, 4),              # to x 488 beside gear 4's column (x 288)
         ("WAITC", "L9_q11w", 488, lambda r: any(286 <= gx <= 292 and 176 <= gh <= 200 for gx, gh in GEAR(r))),   # until the gear is near the top of its climb (raw wraps 224 -> 255 -> 0 -> 192)
         ("L9_q11b", 7308, 7585, 400, 200, 4)]             # swim left, duck under the gear, follow it to the wall at x 504
ROWS += [(f"L9_r{k}", 7585 + 300 * k, 7585 + 300 * (k + 1), 400, 200, 4) for k in range(0, 4)]    # r0..r3 to index 8785
ROWS += [("L9_end", 8785, 8949, 400, 200, 4, {"L4S_ENDCP": "27", "L4S_HPMIN": "0", "L4S_LIVESOK": "1"})]   # into the end trigger (death allowed)
done = list(BASE)
def run_wait(bm, oid, ox, hold_x=None):
    from toads.emulator import BizHawk
    e = BizHawk(log_name=f"wait_{bm}.log"); e.load(f"{done[-1]}_solved"); e.step((), 2); ins = []
    for k in range(900):
        r = e.ram_all()
        if not any(r[0x3C1 + s] == oid and r[0x3FD + s] + 256 * r[0x3EE + s] == ox for s in range(2, 15)):
            break
        x = r[0x3FD] + 256 * r[0x3EE]
        btn = ("Left",) if hold_x is not None and x > hold_x else ("Right",) if hold_x is not None and x < hold_x - 3 else ()
        e.step(btn, 1); ins.append("+".join(btn))
        if e.ram_all()[0x51A] < 47:
            e.close(); return None
    e.save(f"{bm}_solved"); e.close()
    (P / "knowledge" / f"l4s_{bm}.json").write_text(json.dumps(ins))
    shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    return len(ins)
def run_waitc(bm, hold_x, cond):
    from toads.emulator import BizHawk
    e = BizHawk(log_name=f"wait_{bm}.log"); e.load(f"{done[-1]}_solved"); e.step((), 2); ins = []
    for k in range(900):
        r = e.ram_all()
        if cond(r):
            break
        x = r[0x3FD] + 256 * r[0x3EE]
        btn = ("Left",) if x > hold_x + 1 else ("Right",) if x < hold_x - 2 else ()
        e.step(btn, 1); ins.append("+".join(btn))
        if e.ram_all()[0x51A] < 47:
            e.close(); return None
    e.save(f"{bm}_solved"); e.close()
    (P / "knowledge" / f"l4s_{bm}.json").write_text(json.dumps(ins))
    shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    return len(ins)
for row in ROWS:
    if row[0] == "WAITC":
        _, bm, hold_x, cond = row
        if (P / "knowledge" / f"l4s_{bm}.json").exists():
            done.append(bm); print(bm, "already done", flush=True); continue
        n = run_waitc(bm, hold_x, cond)
        print(bm, f"waited {n} frames" if n is not None else "HURT while waiting", flush=True)
        if n is None:
            break
        done.append(bm); continue
    if row[0] == "WAIT":
        _, bm, oid, ox, hold_x = row
        if (P / "knowledge" / f"l4s_{bm}.json").exists():
            done.append(bm); print(bm, "already done", flush=True); continue
        n = run_wait(bm, oid, ox, hold_x)
        print(bm, f"waited {n} frames for object {oid:#x} at x {ox}" if n is not None else "HURT while waiting", flush=True)
        if n is None:
            break
        done.append(bm); continue
    bm, i0, i1, width, steps, macro = row[:6]
    extra = row[6] if len(row) > 6 else {}
    log = P / "logs" / f"l4s_{bm}.txt"; js = P / "knowledge" / f"l4s_{bm}.json"
    if js.exists():
        done.append(bm); print(bm, "already solved", flush=True); continue
    if log.exists() and not any(w in log.read_text() for w in ("solved", "unsolved")):
        print(bm, "running elsewhere, waiting", flush=True)
        while not any(w in log.read_text() for w in ("solved", "unsolved")):
            time.sleep(20)
        if (P / "knowledge" / f"l4s_{bm}.json").exists():
            done.append(bm); continue
        break
    out = subprocess.run([sys.executable, "l9.py", *done], cwd=P, capture_output=True, text=True).stdout
    hroot = int(re.findall(r"section \S+: \d+ frames -> f\d+ H (-?\d+)", out)[-1])
    shutil.copy(P / "states" / f"{done[-1]}_solved.State", P / "states" / f"{bm}.State")
    print(f"{bm}: root H {hroot}, 1P TAS {i0}->{i1}", flush=True)
    env = dict(os.environ, L4S_LVL="11", L4S_SAFE="20", L4S_STEPS=str(steps), L4S_ACTS="swim", L4S_FOLLOW=f"{i0},{i1}",
               L4S_HROOT=str(hroot), L4S_TASLOG="tas/watch_1p_log.txt", L4S_MACRO=str(macro), **extra)
    with open(log, "w") as f:
        subprocess.run([sys.executable, "l4s.py", bm, "0", "0", str(width), "follow"], cwd=P, env=env, stdout=f, stderr=subprocess.STDOUT)
    txt = log.read_text()
    print(bm, [l for l in txt.splitlines() if l.startswith(("solved", "unsolved", "  best unsolved", "  GOAL"))][-2:], flush=True)
    if "unsolved" in txt:
        break
    done.append(bm)
