"""Tail timing experiments: from a state after the kill, apply toad input patterns and report (cut1, tower, tbird) and the number
of lag frames ($0B not advancing) in each phase.   python l13z_tail2.py <segment> <start input>"""
import json, sys
import l13z_beam as zb
from toads.emulator import LOGS_DIR
seg, n0 = sys.argv[1], int(sys.argv[2])
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = j["inputs"]
e = zb.Emu(log_name="l13z_tail2.log")
out = open(LOGS_DIR / "fix" / "l13z_tail2.txt", "a")
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.write(s + "\n"); out.flush()
e.load(j["bookmark"])
for b in ins[:n0]:
    e.step(tuple(v for v in b.split("+") if v), 1)
base = e.msave()
P(f"== {seg} from input {n0}: toad x {e.feat().tx}")

def run(name, fn0, fn2=lambda k, f: "", mash=lambda k: "A" if k % 2 == 0 else ""):
    """fn0(k, f): input before cut 1; mash(k): during the speech; fn2(k, f): in the last scene"""
    e.mload(base)
    n = n0; phase = 0; k = 0; ev = {}; f = e.feat(); lag = [0, 0, 0]; p0b = f.t0b; hpmin = 99
    while n < n0 + 2600:
        b = fn0(k, f) if phase == 0 else (mash(k) if phase == 1 else fn2(k, f))
        f = e.xp(None, [((b or "-"),)])[0][1]
        n += 1; k += 1
        if f.t0b == p0b: lag[phase] += 1
        p0b = f.t0b
        hpmin = min(hpmin, f.thp)
        if phase == 0 and f.lvl != 13:
            phase = 1; k = 0; ev["cut1"] = n; ev["x1"] = f.tx
        elif phase == 1 and f.lvl == 13:
            phase = 2; k = 0; ev["tower"] = n
        elif phase == 2 and f.lvl == 254:
            ev["tbird"] = n; ev["x2"] = f.tx
            break
    P(f"{name:34s} cut1 {ev.get('cut1')} (+{ev.get('tower', 0) - ev.get('cut1', 0)}) tower {ev.get('tower')} (+{ev.get('tbird', 0) - ev.get('tower', 0)}) tbird {ev.get('tbird')}  lag {lag} toad x at cut1 {ev.get('x1')} end {ev.get('x2')} hpmin {hpmin}")
    return ev

idle = lambda k, f: ""
def goto(x):
    return lambda k, f: ("Right" if f.tx < x - 1 else ("Left" if f.tx > x + 1 else ""))
run("idle", idle)
for x in (40, 70, 100, 128, 160, 190, 224):
    run(f"goto {x} then idle", goto(x))
run("idle; Right in last scene", idle, lambda k, f: "Right")
run("idle; Left in last scene", idle, lambda k, f: "Left")
run("jump mash before cut1", lambda k, f: "A" if (k // 2) % 2 == 0 else "")
run("B mash before cut1", lambda k, f: "B" if k % 2 == 0 else "")
run("Select mash before cut1", lambda k, f: "Select" if k % 2 == 0 else "")
run("idle; Select mash last scene", idle, lambda k, f: "Select" if k % 2 == 0 else "")
run("idle; A mash last scene", idle, lambda k, f: "A" if k % 2 == 0 else "")
run("idle; mash A odd", idle, mash=lambda k: "A" if k % 2 == 1 else "")
run("idle; mash A hold", idle, mash=lambda k: "A")
run("idle; mash B", idle, mash=lambda k: "B" if k % 2 == 0 else "")
run("idle; mash Select", idle, mash=lambda k: "Select" if k % 2 == 0 else "")
e.close()
