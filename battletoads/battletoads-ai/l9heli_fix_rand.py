"""Randomised two-hop search for the exact join T' (2026-10-09).

Prefix: a stage-A variant from logs/fix/heli_stA4.json whose water landing has $466 = L0 (default 67: root 7817, j 18, h1 3, n 5).
Then:  run left g1 frames -> hop 1 under the LOW ceiling (A x K1; $466 += shift) -> a few ground frames -> hop 2 under the shaft (A x K2)
-> landing with $466 == 118 -> run left (with an optional one/two-frame hiccup) until T' = (785.160, speed 96, $466 118, flags 72, Left held).
Every T' is verified by replaying the old inputs (L9c 8280...) against the old run's own RAM for VER frames.
    python l9heli_fix_rand.py <tag> <seed> [trials] [L0 K1 K2]
-> logs/fix/heli_rand_<tag>.json (verified joins), bookmark L9heli_R_<tag>_<n>; statistics of where trials fail are printed."""
import json, sys, os, random, time
from l9heli_fix_lib import *
import l9heli_fix_tail as T

TAG = sys.argv[1]; SEED = int(sys.argv[2]); TRIALS = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
L0 = int(sys.argv[4]) if len(sys.argv) > 4 else 67; K1 = int(sys.argv[5]) if len(sys.argv) > 5 else 4; K2 = int(sys.argv[6]) if len(sys.argv) > 6 else 1
SH1 = int(os.environ.get("SH1", -1)); VER = int(os.environ.get("VER", 150))
R = cap(); ins = up14_inputs(); rng = random.Random(SEED)
cands = [o for o in json.load(open(LOGS_DIR / "fix" / "heli_stA4.json")) if o["land"][4] == L0]
var = min(cands, key=lambda o: o["land"][0])
print("prefix variant", {k: var[k] for k in ("root", "j", "h1", "n", "land")}, flush=True)
J0 = 8279; TK = T.TK
e = BizHawk(log_name=f"l9heli_fix_rand_{TAG}.log", fields=T.FLD)
e.load("L9heli_7800")
for f in range(OFF + 7800, OFF + var["root"]):
    e.step(bt(ins[f]), 1)
for b in var["inputs"]:
    s = e.step(bt(b), 1)
print("water landing: index", var["root"] + len(var["inputs"]), "x", s.x | s.xh << 8, s.sub, "spd", s.spd, "$466", s.sh, "mine", T.mine(e), flush=True)
S0 = e.msave(); IDX0 = var["root"] + len(var["inputs"])
stats = {}; found = []; t0 = time.time()


def pieces(n, opts, kmax):
    """random piecewise-constant direction plan of total length n"""
    k = rng.randint(1, kmax); cuts = sorted(rng.sample(range(1, n), min(k - 1, n - 1))) if k > 1 else []
    out = []; prev = 0
    for c in cuts + [n]:
        out += [rng.choice(opts)] * (c - prev); prev = c
    return out


def fail(why):
    stats[why] = stats.get(why, 0) + 1


def play(seq, need_air=False):
    """step a list; returns (state, frames used, landed?) stopping at the first floor landing after leaving the ground if need_air"""
    left = False; s = None
    for i, b in enumerate(seq):
        s = e.step(bt(b), 1)
        if s.hp < 47 or s.an in CARRIED:
            return s, i + 1, "dead"
        if need_air:
            if s.z:
                left = True
            elif left and (s.h | s.hh << 8) == 6182:
                return s, i + 1, "land"
    return s, len(seq), "end"


for trial in range(TRIALS):
    e.mload(S0); path = []
    g1 = rng.randint(12, 22); seq = ["Left"] * g1
    s, n, r = play(seq); path += seq[:n]
    if r == "dead": fail("run1 dead"); continue
    x1 = s.x | s.xh << 8
    d1 = pieces(46, ["Left", "", "Right", "Right", ""], 4)
    seq = [(d + "+A").strip("+") if i < K1 else d for i, d in enumerate(d1)]
    s, n, r = play(seq, True); path += seq[:n]
    if r != "land": fail("hop1 " + r); continue
    if SH1 >= 0 and s.sh != SH1: fail(f"hop1 $466 {s.sh}"); continue
    sh1 = s.sh
    g2 = rng.randint(0, 8); seq = pieces(g2, ["Left", "", "Right"], 2) if g2 else []
    if seq:
        s, n, r = play(seq); path += seq[:n]
        if r == "dead": fail("ground2 dead"); continue
    d2 = pieces(70, ["Left", "", "Right", "Left"], 6)
    seq = [(d + "+A").strip("+") if i < K2 else d for i, d in enumerate(d2)]
    s, n, r = play(seq, True); path += seq[:n]
    if r != "land": fail("hop2 " + r); continue
    if s.sh != TK[5]: fail(f"hop2 $466 {sh1}->{s.sh}"); continue
    xl = s.x | s.xh << 8
    if xl < 786: fail("hop2 lands left of 786"); continue
    land2 = e.msave(); hit = None
    variants = [()] + [(p, w, b) for p in range(0, 14) for w in (1, 2) for b in ("", "Right")]
    for hv in variants:
        e.mload(land2); seq = []; ok = None
        for k in range(60):
            b = "Left"
            if hv and hv[0] <= k < hv[0] + hv[1]: b = hv[2]
            s = e.step(bt(b), 1); seq.append(b)
            if s.hp < 47: ok = "dead"; break
            x = s.x | s.xh << 8
            if x < 785: break
            if b == "Left" and (x, s.sub, s.h | s.hh << 8, s.z, s.spd, s.sh, s.f) == TK: ok = "T"; break
        if ok == "T":
            sv = e.msave(); good = 0; bad = None
            for j in range(J0, J0 + VER):
                s = e.step(bt(ins[OFF + j]), 1); ref = bytes(R[OFF + j])
                if T.kin(s) != T.ckin(ref): bad = (j + 1, T.kin(s), T.ckin(ref)); break
                good += 1
            f = IDX0 + len(path) + len(seq)
            print(f"trial {trial}: T' at index {f} (gain {J0 - f}) landing2 x {xl} hiccup {hv}: verify {good}/{VER} first diff {bad}", flush=True)
            if bad is None:
                full = var["inputs"] + path + seq
                found.append({"root": f"L9c index {var['root']}", "root_index": var["root"], "inputs": full, "join_old_index": J0, "index": f, "gain": J0 - f, "trial": trial})
                e.mload(sv); e.save(f"L9heli_R_{TAG}_{len(found) - 1}")
                json.dump(found, open(LOGS_DIR / "fix" / f"heli_rand_{TAG}.json", "w"))
                hit = True
            else:
                fail("T' but verify failed")
            e.mfree(sv)
            if hit: break
    e.mfree(land2)
    if not hit: fail(f"no T' (landing2 ok)")
    if trial % 200 == 199:
        print(f"-- {trial + 1} trials, {len(found)} verified, {time.time() - t0:.0f}s; fails: {sorted(stats.items(), key=lambda kv: -kv[1])[:12]}", flush=True)
print("done", TRIALS, "trials;", len(found), "verified joins; best gain", max([f["gain"] for f in found], default=None), "stats", stats, flush=True)
e.close()
