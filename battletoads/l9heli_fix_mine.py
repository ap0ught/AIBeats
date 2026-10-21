"""Randomised repair of one corridor hop (2026-10-10).  The leftover propeller bug shifts the corridor mines to other object slots, their lunge
scripts run a frame or two off and the old inputs get hit.  The corridor floor is slow water: on the ground the vertical sub-pixel is
constant, so only the HORIZONTAL inputs and the waiting are changed; every hop keeps the old run's A frames (same height track, same $466).

From a join bookmark replay the old inputs (with earlier repairs) to old index A (a landing, toad state exact), then per trial:
  ground: g frames of random pieces (nothing / Left / Right)
  hop:    the old hop's A pattern (first K frames with A), random direction pieces, until the landing
  run-up: hold Right; if the toad passes the old run's exact take-off state TGT (x, sub-x, speed, $466) the old inputs TGT+1.. are replayed
          and compared with the old run for VER frames (lag-aware: an input is held until the frame counter ticks).
    python l9heli_fix_mine.py <bookmark> <A> <K> <TGT> <tag> <seed> [trials] [edits json]
-> logs/fix/heli_mine_<tag>.json {A, TGT, inputs (raw, replace old A+1..TGT), shift}, bookmark L9heli_M_<tag>"""
import json, sys, os, random, time
from l9heli_fix_lib import *

BM, A, K, TGT, TAG, SEED = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], int(sys.argv[6])
TRIALS = int(sys.argv[7]) if len(sys.argv) > 7 else 3000
EDITS = json.load(open(sys.argv[8])) if len(sys.argv) > 8 else []
SHOFF = int(os.environ.get("SHOFF", 0))                     # our vertical sub-pixel minus the old run's (a tolerated constant offset)
SMOD = os.environ.get("SMOD")                               # "r": only shifts with shift % 4 == r are verified and kept
VER = int(os.environ.get("VER", 120)); GMAX = int(os.environ.get("GMAX", 30)); RUNDIR = os.environ.get("RUNDIR", "Right")
FLD = {"x": 0x3FD, "xh": 0x3EE, "sub": 0x448, "h": 0x439, "hh": 0x42A, "z": 0x475, "spd": 0x565, "hp": 0x51A, "sh": 0x466, "f": 0x4A2, "an": 0x3D0, "t": 0x0B}
R = cap(); ins = up14_inputs(); rng = random.Random(SEED)


def old_inputs(a, b):
    out = []; k = a
    while k < b:
        ed = [x for x in EDITS if x["A"] == k]
        if ed:
            out += ed[0]["inputs"]; k = ed[0]["TGT"]
        else:
            out.append(ins[OFF + k]); k += 1
    return out


e = BizHawk(log_name=f"l9heli_fix_mine_{TAG}.log", fields=FLD); e.load(BM)
st = e.state()


def lstep(b):
    """one logic frame (input held through lag frames) -> (state, raw input list)"""
    global st
    t0 = st.t; raw = []
    for _ in range(6):
        st = e.step(bt(b), 1); raw.append(b)
        if st.t != t0:
            break
    return st, raw


for b in old_inputs(8279, A):
    lstep(b)
ref = bytes(R[OFF + A - 1])
print("at A", A, "ours x", st.x | st.xh << 8, st.sub, "H", st.h | st.hh << 8, "spd", st.spd, "sh", st.sh, "| old", ref[0x3FD] | ref[0x3EE] << 8, ref[0x448], ref[0x439] | ref[0x42A] << 8, ref[0x565], ref[0x466], flush=True)
T = bytes(R[OFF + TGT - 1]); TK = (T[0x3FD] | T[0x3EE] << 8, T[0x448], T[0x439] | T[0x42A] << 8, T[0x475], T[0x565], T[0x466])
FLOOR = TK[2]; print("target", TGT, TK, flush=True)
S0 = e.msave(); st0 = st; hp0 = st.hp; stats = {}; found = []; t0 = time.time()


def key(s):
    return (s.x | s.xh << 8, s.sub, s.h | s.hh << 8, s.z, s.spd, (s.sh - SHOFF) & 255)


def okin(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x448], m[0x439] | m[0x42A] << 8, m[0x475], m[0x565], m[0x51A])


def pieces(n, opts, kmax):
    if n <= 0:
        return []
    k = rng.randint(1, kmax); cuts = sorted(rng.sample(range(1, n), min(k - 1, n - 1))) if n > 1 and k > 1 else []
    out = []; prev = 0
    for c in cuts + [n]:
        out += [rng.choice(opts)] * (c - prev); prev = c
    return out


def fail(w):
    stats[w] = stats.get(w, 0) + 1


DELTA = [0, 64, 136, 200, 256, 336, 384, 472, 512]
PLAN = {}


def ground_plan(dx, v, vt, depth=44):
    """slow-water ground model, moving right: Right +2 (cap 96), nothing -4, Left -12 (not below 0); x += DELTA[speed // 16] (new speed).
    Shortest input list that covers exactly dx (1/256 px) and ends on speed vt with a Right press; None if none within depth."""
    if (dx, v) in PLAN:
        return PLAN[(dx, v)]
    layer = {(0, v): []}; res = None
    for d in range(depth):
        nxt = {}
        for (x, sp), path in layer.items():
            for b, sp2 in (("Right", min(sp + 2, 96) if sp < 96 else sp), ("", max(sp - 4, 0)), ("Left", max(sp - 12, 0))):
                if b == "Left" and sp2 == 0:
                    continue                                  # (would turn round)
                x2 = x + DELTA[min(sp2 // 16, 8)]
                if x2 > dx:
                    continue
                if x2 == dx and sp2 == vt and b == "Right":
                    res = path + [b]; break
                if (x2, sp2) not in nxt:
                    nxt[(x2, sp2)] = path + [b]
            if res:
                break
        if res:
            break
        layer = nxt
        if not layer:
            break
    PLAN[(dx, v)] = res
    return res


for trial in range(TRIALS):
    e.mload(S0); st = st0; path = []
    dead = False
    for b in pieces(rng.randint(1, GMAX), ["", "Left", "Right", ""], 4):
        s, raw = lstep(b); path += raw
        if s.hp < hp0: dead = True; break
        if s.z: break                                         # walked off something
    if dead: fail("ground dead"); continue
    plan = pieces(60, ["Left", "", "Right", "Right"], 5)
    land = False
    for i in range(60):
        b = (plan[i] + "+A").strip("+") if i < K else plan[i]
        s, raw = lstep(b); path += raw
        if s.hp < hp0: dead = True; break
        if i > 3 and s.z == 0:
            land = (s.h | s.hh << 8) == FLOOR; break
    if dead: fail("hop dead"); continue
    if not land: fail("hop no landing on the floor"); continue
    hit = False
    if s.f & 0x40: fail("lands facing left"); continue
    dx = (TK[0] * 256 + TK[1]) - ((s.x | s.xh << 8) * 256 + s.sub)
    gp = ground_plan(dx, s.spd, TK[4]) if 0 < dx < 40 * 256 else None
    if gp is None: fail("no ground plan to the take-off state"); continue
    for b in gp:
        s, raw = lstep(b); path += raw
        if s.hp < hp0: dead = True; break
    if dead: fail("run-up dead"); continue
    if key(s) != TK: fail(f"ground model off"); continue
    hit = True
    if SMOD is not None and (len(path) - (TGT - A)) % 4 != int(SMOD): fail(f"take-off state reached with shift {len(path) - (TGT - A):+d} (wrong phase)"); continue
    sv = e.msave(); stv = st; good = 0; bad = None
    for j in range(TGT, TGT + VER):
        lstep(ins[OFF + j]); m = e.ram(0, 0x800)
        if okin(m) != okin(bytes(R[OFF + j])): bad = (j + 1, okin(m), okin(bytes(R[OFF + j]))); break
        good += 1
    sh = len(path) - (TGT - A)
    print(f"trial {trial}: take-off state reached, {len(path)} raw frames for the old {TGT - A} (shift {sh:+d}); verify {good}/{VER} first diff {bad}", flush=True)
    if bad is None:
        found.append({"A": A, "TGT": TGT, "inputs": path, "shift": sh})
        e.mload(sv); e.save(f"L9heli_M_{TAG}_{len(found) - 1}")
        json.dump(found, open(LOGS_DIR / "fix" / f"heli_mine_{TAG}.json", "w"))
    else:
        fail("verify failed")
    e.mfree(sv)
    if trial % 500 == 499:
        print(f"-- {trial + 1} trials, {len(found)} good, {time.time() - t0:.0f}s, fails {sorted(stats.items(), key=lambda kv: -kv[1])}", flush=True)
print("done;", len(found), "good; best shift", min([f["shift"] for f in found], default=None), "stats", stats, flush=True)
e.close()
