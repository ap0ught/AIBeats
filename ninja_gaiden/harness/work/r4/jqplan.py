"""Round 4 Jaquio planner: pure model search (no emulator), from the 6-4b control state tmp/a56r2_64b_control.
Model (measured 2026-10-22, work/r4/jq_play.py; hitbox formulas from the community Lua scripts):
  * Jaquio x per row: work/r4/jx_idle.txt (deterministic); his box x+-28, y 24..96 (box index $43F = 112).
  * Sword (swing row = Down+B row, $83 == 7): box Ryu.x..+32 (facing right) or -32..x (left), y-25..y-9;
    hit iff Ryu y <= 120 and J-x in [-28, 60] (right) / [-60, 28] (left). Body contact if y <= 121 and |dx| <= BODY.
  * Pedestals (Ryu x on top, y 160): L 27..71, M 92..136, R 189..232. Floor y 208, walls x 24 / 236.
  * Pedestal jump: press row r (A 2 rows) -> y profile PJ[i] (i = rows after r), lands at r+43 if over a pedestal.
    Floor jump: y 208 -> 160 at i = 19 (lands on a pedestal top if x over one).
  * Air: facing fixed at takeoff; holding the facing direction 1.5 px/f, the other direction 0.5 px/f; no momentum.
  * Ground walk 1.5 px/f from the first held row.
python work/r4/jqplan.py <tag> [maxwait] [beam] [body]  -> logs/r4/jq_plan_<tag>.json (best plans)"""
import json
import sys
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent.parent.parent
JX = np.array([0.0] + [float(v) for v in (P / "work/r4/jx_idle.txt").read_text().split()] + [0.0] * 600)
PJ = np.array([160, 156, 152, 148, 144, 140, 137, 134, 131, 128, 125, 123, 121, 119, 117, 116, 115, 114, 113, 112, 112,
               112, 112, 112, 112, 112, 113, 114, 115, 116, 118, 120, 122, 124, 126, 129, 132, 135, 138, 141, 145, 149,
               153, 157], float)
NI = 43
PEDS = [(31, 67), (96, 132), (193, 228)]   # measured L 27..71, M 92..136, R 189..232, minus 2 px margins
YMAX = 119  # sword_hit: Ryu y - 96 < $91 (24)
BODY = 28   # hurt_ryu ($E144): |dx| < 28 (Jaquio's x radius) and Ryu y in (24, 121)
NEED = 16
TOP = []
HOLDS = [("N", 0, 0)]
for k in range(2, NI, 2):
    HOLDS.append(("F", 1, 1 + k))
    HOLDS.append(("O", 1, 1 + k))
for k in range(4, NI - 1, 4):
    HOLDS.append(("F", k, NI))
    HOLDS.append(("O", k, NI))
D = np.zeros((len(HOLDS), NI + 1))
for h, (hd, a, b) in enumerate(HOLDS):
    if hd == "F":
        D[h, a:b] = 1.5
    elif hd == "O":
        D[h, a:b] = -0.5
CUM = np.cumsum(D, axis=1)


def ped_of(x):
    r = np.full(np.shape(x), -1)
    for k, (a, b) in enumerate(PEDS):
        r = np.where((x >= a) & (x <= b), k, r)
    return r


def expand(nd, maxwait, need):
    """all pedestal jumps from node nd -> list of child tuples"""
    a, b = PEDS[int(ped_of(nd["x"]))]
    out = []
    for T in range(nd["t"], nd["t"] + maxwait + 1):
        n = T - nd["t"]
        jx = JX[T:T + NI + 1]
        for F in (1, -1):
            # facing at takeoff = direction of the walk before it (>= 2 rows), or the current facing without a walk
            js = ([0] if F == nd["face"] else []) + [F * j for j in range(2, n + 1)]
            Xs = np.array([nd["x"] + 1.5 * j for j in js])
            Xs = Xs[(Xs >= a) & (Xs <= b)]
            if not len(Xs):
                continue
            nX, H = len(Xs), len(HOLDS)
            V = np.broadcast_to(D[None], (nX, H, NI + 1)).copy()
            hs = None
            for ps in range(2):
                xi = np.clip(Xs[:, None, None] + F * np.cumsum(V, axis=2), 24, 236)        # (nX, H, 44)
                dx = jx[None, None, :] - xi
                fd = F * dx
                ok = (PJ <= YMAX)[None, None, :] & (fd >= 28) & (fd <= 58)
                if ps == 0:
                    # greedy swing rows (spacing >= 5, Down on s-1 and s must be air rows), then no direction on s-1, s
                    last = np.full((nX, H), nd["last"])
                    sw = np.zeros(ok.shape, bool)
                    for i in range(2, NI - 1):
                        c = ok[:, :, i] & (T + i - last >= 5)
                        last = np.where(c, T + i, last)
                        sw[:, :, i] = c
                    V[sw] = 0.0
                    V[:, :, :-1][sw[:, :, 1:]] = 0.0
            bad = np.any((PJ <= 121)[None, None, :] & (np.abs(dx) <= BODY), axis=2)
            hitm = sw & ok
            cnt = hitm.sum(axis=2)
            rowsi = np.arange(NI + 1)[None, None, :]
            lastrow = np.where(hitm, T + rowsi, -99).max(axis=2)
            lastrow = np.where(cnt > 0, lastrow, nd["last"])
            # kill row = row of the need-th hit within this jump
            cum = np.cumsum(hitm, axis=2)
            kill = np.where(np.any(cum >= need, axis=2), T + np.argmax(cum >= need, axis=2), 0)
            lx = xi[:, :, NI]
            lp = ped_of(lx)
            for xi_, h in zip(*np.nonzero(~bad)):
                out.append((T, float(Xs[xi_]), F, h, int(cnt[xi_, h]), int(lastrow[xi_, h]), int(kill[xi_, h]),
                            float(lx[xi_, h]), int(lp[xi_, h])))
    return out


def sim_jump(T, X, F, h, last):
    """one jump with the swing rule -> (swing rows, hit rows, x profile)"""
    V = D[h].copy()
    jx = JX[T:T + NI + 1]
    xi = np.clip(X + F * np.cumsum(V), 24, 236)
    fd = F * (jx - xi)
    ok = (PJ <= YMAX) & (fd >= 28) & (fd <= 58)
    sw = []
    for i in range(2, NI - 1):
        if ok[i] and T + i - last >= 5:
            sw.append(i)
            last = T + i
    for i in sw:
        V[i] = 0.0
        V[i - 1] = 0.0
    xi = np.clip(X + F * np.cumsum(V), 24, 236)
    fd = F * (jx - xi)
    ok = (PJ <= YMAX) & (fd >= 28) & (fd <= 58)
    return [T + i for i in sw], [T + i for i in sw if ok[i]], xi, V


def plan(tag, maxwait=60, beam=200):
    starts = []
    for T in range(1, 3):
        for k in [0] + list(range(2, 20)):
            X = 32 + 1.5 * k
            starts.append(dict(x=X, t=T + 19, face=1, hits=0, last=-99,
                               steps=[("floorjump", T, 32, 1, k)]))
    for n in range(40, 60, 2):
        X = 32 + 1.5 * n
        if ped_of(X) == 1:
            starts.append(dict(x=X, t=n + 1 + 19, face=1, hits=0, last=-99,
                               steps=[("floorwalk", 1, n), ("floorjump", n + 1, X, 1, 0)]))
    beamL = starts
    best = None
    for depth in range(9):
        kids = {}
        for nd in beamL:
            for (T, X, F, h, cnt, last, kill, lx, lp) in expand(nd, maxwait, NEED - nd["hits"]):
                tot = nd["hits"] + cnt
                st = ("jump", T, X, F, HOLDS[h], cnt)
                if tot >= NEED:
                    TOP.append(dict(kill=kill, steps=nd["steps"] + [st]))
                    if best is None or kill < best["kill"]:
                        best = dict(kill=kill, steps=nd["steps"] + [st])
                        print("KILL", kill, best["steps"], flush=True)
                    continue
                if lp < 0:
                    continue
                lt = T + NI
                if best and lt + 5 * (NEED - tot) >= best["kill"]:
                    continue
                key = (lp, round(lx / 3), F, tot)
                if key not in kids or kids[key]["t"] > lt or (kids[key]["t"] == lt and kids[key]["last"] > last):
                    kids[key] = dict(x=lx, t=lt, face=F, hits=tot, last=last, steps=nd["steps"] + [st])
        cand = sorted(kids.values(), key=lambda c: c["t"] - 11 * c["hits"])
        beamL = cand[:beam]
        print("depth", depth, "kids", len(kids), "beam", [(c["t"], c["hits"]) for c in beamL[:10]], flush=True)
        if not beamL:
            break
    (P / "logs" / "r4").mkdir(exist_ok=True, parents=True)
    (P / "logs" / "r4" / f"jq_plan_{tag}.json").write_text(json.dumps(best, default=float, indent=1))
    TOP.sort(key=lambda d: d["kill"])
    (P / "logs" / "r4" / f"jq_top_{tag}.json").write_text(json.dumps(TOP[:300], default=float))
    return best


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "p1"
    mw = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    bw = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    if len(sys.argv) > 4:
        BODY = int(sys.argv[4])
    b = plan(tag, mw, bw)
    print("BEST", b and b["kill"])
