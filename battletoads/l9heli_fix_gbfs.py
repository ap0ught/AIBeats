"""Ground re-join BFS inside the old route (2026-10-10): the leftover propeller bug puts the corridor mines in other object slots, their lunge
scripts run a frame or two off, and the old inputs get hit while the toad stands next to a mine.  The corridor floor is 'slow water': on the
ground the vertical sub-pixel does not change, so time spent on the ground is free state-wise.

From a join bookmark replay the old inputs (plus earlier repairs) to old index A (a ground frame), then search, layer by layer (one frame per
layer; inputs: nothing / Left / Right; states that lose health are dropped), for the old run's exact ground state at index TGT
(x, sub-x, height, speed, vertical sub-pixel, flags).  Each hit is verified: the old inputs TGT+1.. must reproduce the old run's track for
VER frames.
    python l9heli_fix_gbfs.py <bookmark> <A> <TGT> <depth> <tag> [edits json]
-> logs/fix/heli_gbfs_<tag>.json {A, TGT, inputs (replace old inputs A+1..TGT), shift}, bookmark L9heli_G_<tag> (state at TGT)"""
import json, sys, os, time
from l9heli_fix_lib import *

BM, A, TGT, DEPTH, TAG = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
EDITS = json.load(open(sys.argv[6])) if len(sys.argv) > 6 else []          # earlier repairs: list of {A, TGT, inputs}
VER = int(os.environ.get("VER", 120)); XWIN = int(os.environ.get("XWIN", 24))
ACTS = os.environ.get("ACTS", ",Left,Right").split(",")
R = cap(); ins = up14_inputs()


SHOFF = int(os.environ.get("SHOFF", 0))                     # our vertical sub-pixel minus the old run's (a tolerated constant offset)


def kin(m, off=0):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], (m[0x466] - off) & 255, m[0x4A2] & 0x48, m[0x3D0])


def track(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x51A])


def old_inputs(a, b):
    """old inputs for old indices a+1..b with the earlier repairs applied (as a list of input strings)"""
    out = []; k = a
    while k < b:
        ed = [x for x in EDITS if x["A"] == k]
        if ed:
            out += ed[0]["inputs"]; k = ed[0]["TGT"]
        else:
            out.append(ins[OFF + k]); k += 1
    return out


e = BizHawk(log_name=f"l9heli_fix_gbfs_{TAG}.log"); e.load(BM)
LAGS = [0]


def lstep(b):
    """one LOGIC frame: the input is held until the frame counter $0B ticks (a lag frame does not read the pad). Returns (ram, raw inputs)"""
    t0 = e.byte(0x0B); raw = []
    for _ in range(6):
        e.step(bt(b), 1); raw.append(b); m = e.ram(0, 0x800)
        if m[0x0B] != t0:
            break
        LAGS[0] += 1
    return m, raw


PRE = []
for b in old_inputs(8279, A):
    m, raw = lstep(b); PRE += raw
print("replayed to A with", LAGS[0], "lag frames", flush=True)
ref = bytes(R[OFF + A - 1])
print("at A", A, "ours", tstr(m), "| old", tstr(ref), "| same toad:", track(m) == track(ref), "|", ostr(m), flush=True)
tk = kin(bytes(R[OFF + TGT - 1])); x0 = tk[0]; hp0 = m[0x51A]
print("target (old", TGT, "):", tk, flush=True)
layer = [(e.msave(), [])]; found = None; t0 = time.time()
for d in range(1, DEPTH + 1):
    nxt = {}
    for sid, path in layer:
        for a in ACTS:
            e.mload(sid); m, raw = lstep(a)
            if m[0x51A] < hp0 or m[0x475] != 0:
                continue
            k = kin(m, SHOFF)
            if abs(k[0] - x0) > XWIN or k in nxt:
                continue
            p2 = path + raw
            if k == tk and a == ins[OFF + TGT - 1].replace(",", "+"):
                sv = e.msave(); ok = 0; bad = None
                for j in range(TGT, TGT + VER):
                    mm, _ = lstep(ins[OFF + j]); rr = bytes(R[OFF + j])
                    if track(mm) != track(rr):
                        bad = (j + 1, track(mm), track(rr)); break
                    ok += 1
                print(f"depth {d}: target state reached ({len(p2)} frames for the old {TGT - A}; shift {len(p2) - (TGT - A):+d}); verify {ok}/{VER}, first diff {bad}", flush=True)
                if bad is None:
                    found = (sv, p2); break
                e.mfree(sv)
            nxt[k] = (e.msave(), p2)
        if found:
            break
    for sid, _ in layer:
        e.mfree(sid)
    if found:
        break
    layer = list(nxt.values())
    if d % 5 == 0:
        print(f"depth {d}: {len(layer)} states, {time.time() - t0:.0f}s", flush=True)
    if not layer:
        print("no states left", flush=True); break
if found:
    sv, p2 = found
    e.mload(sv); e.save(f"L9heli_G_{TAG}")
    json.dump({"A": A, "TGT": TGT, "inputs": p2, "shift": len(p2) - (TGT - A), "pre_raw": PRE}, open(LOGS_DIR / "fix" / f"heli_gbfs_{TAG}.json", "w"))
    print("SAVED", TAG, "shift", len(p2) - (TGT - A), " ".join(x or "-" for x in p2), flush=True)
else:
    print("no verified re-join", flush=True)
e.close()
