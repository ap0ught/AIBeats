"""Round 4 Jaquio planner v2 = jqplan.py's model + the swing-cancel rule + Jaquio's homing fireballs (fbsim.py
rules, exact on the calibration traces). A candidate jump is dropped if a fireball would touch Ryu (hurt_ryu rule)
before a swing kills it. Spawns: rows 129, 249, 369 (J timer), x = J(prev row) +-32, y 64.
    python work/r4/jqplan2.py <tag> [maxwait] [beam]  -> logs/r4/jq_plan_<tag>.json, jq_top_<tag>.json"""
import json
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jqplan as M  # noqa
P = M.P
NI, PJ, JX, D, HOLDS, PEDS = M.NI, M.PJ, M.JX, M.D, M.HOLDS, M.PEDS
NEED = 16
import os
BOSS = os.environ.get("BOSS", "jaquio")
BLO, BHI, X0 = 28, 58, 32          # Jaquio: F*dx in [28, 58] (x radius 28), Ryu y <= 119, body |dx| <= 28 at y <= 121
YOK = PJ <= M.YMAX
HURTY = PJ <= 121
BODYR = M.BODY
if BOSS == "mdevil":               # 6-4a orb (slot 6, id 36): x 135, y 120, x radius 16, y radius 8, static
    JX = np.full(2000, 135.0)
    BLO, BHI, X0 = 16, 47, 33
    YOK = (PJ > 104) & (PJ < 144)   # sword_hit: R.y - 120 < $91 (24), 120 - R.y < $92 (16)
    HURTY = (PJ > 112) & (PJ < 145)
    BODYR = 15
    NEED = int(os.environ.get("NEED", "14"))
SPAWNS = (129, 249, 369, 489) if BOSS == "jaquio" else (99999,)
NE = 2 * len(SPAWNS)          # fireball entries: wave w side 0 (right, slot 5) / 1 (left, slot 6)
STALE0 = {0: (71, 228), 1: (0, 0)}
TOP = []
FROM1 = np.array([hd == "F" and a == 1 for (hd, a, b) in HOLDS])


def clean(V, downrows):
    """make the air direction rows legal-ish (Enforcer rules): no 1-row presses, no 1-row releases between presses
    of the same direction (except on Down rows, where no direction may be held). V (..., 44) edited in place."""
    nz = V != 0
    prv = np.zeros_like(nz); prv[..., 1:] = nz[..., :-1]
    nxt = np.zeros_like(nz); nxt[..., :-1] = nz[..., 1:]
    single = nz & ~prv & ~nxt
    V[single] = 0.0
    vp = np.zeros_like(V); vp[..., 1:] = V[..., :-1]
    vn = np.zeros_like(V); vn[..., :-1] = V[..., 1:]
    gap = (V == 0) & (vp != 0) & (vp == vn) & ~downrows
    V[gap] = vp[gap]
    return V


def fb_init():
    # per entry: alive, x, xs, vx, y, ys, vy
    return np.zeros((NE, 7), np.int64)


def sim_rows(fb, t0, RX, RY, SW, FACE):
    """vectorised fireball sim. fb: (N, NE, 7) int64; rows t0 .. t0+L-1 with Ryu int x RX (N, L), height RY
    (L,), swing mask SW (N, L), facing FACE (scalar). Returns (fb, hurt (N,) bool)."""
    N, L = RX.shape
    act = [e for e in range(NE) if fb[:, e, 0].any() or (SPAWNS[e // 2] >= t0 and SPAWNS[e // 2] < t0 + L)]
    if not act:
        return fb.copy(), np.zeros(N, bool)
    full = fb.copy()
    fb = full[:, act, :].copy()
    emap = {e: k for k, e in enumerate(act)}
    hurt = np.zeros(N, bool)
    RY = np.broadcast_to(RY, (N, L))
    for k in range(L):
        r = t0 + k
        if r in SPAWNS:
            w = SPAWNS.index(r)
            jprev = int(JX[r - 1])
            for side in (0, 1):
                e = emap[2 * w + side]
                if w == 0:
                    xs, ys = STALE0[side]
                    xs = np.full(N, xs)
                    ys = np.full(N, ys)
                else:
                    pe = 2 * (w - 1) + side
                    src = fb[:, emap[pe]] if pe in emap else full[:, pe]
                    dead = src[:, 0] == 0
                    xs = np.where(dead, src[:, 2], 0)
                    ys = np.where(dead, src[:, 5], 0)
                fb[:, e, 0] = 1
                fb[:, e, 1] = jprev + (32 if side == 0 else -32)
                fb[:, e, 2] = xs
                fb[:, e, 3] = 0
                fb[:, e, 4] = 64
                fb[:, e, 5] = ys
                fb[:, e, 6] = 0
        al = fb[:, :, 0] == 1
        if not al.any():
            continue
        rx = RX[:, k][:, None]
        ry = RY[:, k][:, None]
        x, xs, vx, y, ys, vy = (fb[:, :, j] for j in range(1, 7))
        vx = vx + np.where(x >= rx, -16, 16)
        vy = vy + np.where(ry - 8 - y >= 0, 16, -16)
        t = xs + (vx & 0xFF)
        nxs = t & 0xFF
        nx = x + (vx >> 8) + (t >> 8)
        t = ys + (vy & 0xFF)
        nys = t & 0xFF
        ny = y + (vy >> 8) + (t >> 8)
        gone = (nx < 8) | (nx >= 248) | (ny < 48) | (ny >= 248)
        for j, v in ((1, nx), (2, nxs), (3, vx), (4, ny), (5, nys), (6, vy)):
            fb[:, :, j] = np.where(al, v, fb[:, :, j])
        al2 = al & ~gone
        d = ry - ny
        h = al2 & (np.abs(nx - rx) < 16) & (((d >= 0) & (d < 25)) | ((d < 0) & (-d < 8)))
        hurt |= h.any(axis=1)
        u = FACE * (nx - rx) - 16
        dd = ny - ry
        kill = al2 & SW[:, k][:, None] & (u >= 0) & (u <= 31) & (((dd >= 0) & (dd < 16)) | ((dd < 0) & (-dd < 24)))
        fb[:, :, 0] = np.where(al2 & ~kill, 1, 0)
    full[:, act, :] = fb
    return full, hurt


def expand(nd, maxwait, need):
    a, b = PEDS[int(M.ped_of(nd["x"]))]
    out = []
    fbrel = bool(nd["fb"][:, 0].any()) or any(nd["t"] <= q <= nd["t"] + maxwait + NI for q in SPAWNS)
    for T in range(nd["t"], nd["t"] + maxwait + 1):
        n = T - nd["t"]
        jx = JX[T:T + NI + 1]
        for F in (1, -1):
            js = ([0] if F == nd["face"] else []) + [F * j for j in range(2, n + 1)]
            Xs = np.array([nd["x"] + 1.5 * j for j in js])
            jarr = np.array(js)
            keep = (Xs >= a) & (Xs <= b)
            # no 1-row release between the previous press of a direction and a walk in the same direction
            ws = T - np.abs(jarr)
            keep &= ~((jarr != 0) & (np.sign(jarr) == nd.get("pd", 0)) & (ws - nd.get("pe", -99) == 2))
            Xs, jarr = Xs[keep], jarr[keep]
            if not len(Xs):
                continue
            nX, H = len(Xs), len(HOLDS)
            for mode in ((0, 1) if fbrel else (0,)):
              amode = mode if mode < 2 else 1
              sl = None if mode < 2 else (mode - 2) * 4      # ground slash: B at T-8-sl, blade at T-2-sl
              if sl is not None and (T - 8 - sl < nd["t"] or T - 8 - sl - nd["last"] < 5 or 0 not in jarr):
                  continue
              V = np.broadcast_to(D[None], (nX, H, NI + 1)).copy()
              # walking into the jump with the hold in the same direction: the direction stays held through the
              # takeoff row, which then moves 1.5 px too (measured)
              V[(jarr != 0)[:, None] & FROM1[None, :], 0] = 1.5
              for ps in range(2):
                  xi = np.clip(Xs[:, None, None] + F * np.cumsum(V, axis=2), 24, 236)
                  dx = jx[None, None, :] - xi
                  fd = F * dx
                  ok = YOK[None, None, :] & (fd >= BLO) & (fd <= BHI)
                  if ps == 0:
                      last = np.full((nX, H), nd["last"])
                      sw = np.zeros(ok.shape, bool)
                      for i in range(2, NI - 1):
                          c = ok[:, :, i] & (T + i - last >= 5)
                          last = np.where(c, T + i, last)
                          sw[:, :, i] = c
                      if amode == 1:
                          # defensive fill: extra swings (fireballs) wherever spacing allows, 5 rows apart
                          nxt = np.full((nX, H), 999)
                          nxa = np.zeros(ok.shape, int)
                          for i in range(NI, -1, -1):
                              nxa[:, :, i] = nxt
                              nxt = np.where(sw[:, :, i], i, nxt)
                          last = np.full((nX, H), nd["last"] - T)
                          for i in range(2, NI - 1):
                              c = ~sw[:, :, i] & (i - last >= 5) & (nxa[:, :, i] - i >= 5)
                              sw[:, :, i] |= c
                              last = np.where(sw[:, :, i], i, last)
                      V[sw] = 0.0
                      V[:, :, :-1][sw[:, :, 1:]] = 0.0
                      dr = sw.copy()
                      dr[:, :, :-1] |= sw[:, :, 1:]
                      clean(V, dr)
              bad = np.any(HURTY[None, None, :] & (np.abs(dx) <= BODYR), axis=2)
              hitm = sw & ok
              cnt = hitm.sum(axis=2)
              rowsi = np.arange(NI + 1)[None, None, :]
              lastrow = np.where(sw, T + rowsi, -99).max(axis=2)
              lastrow = np.where(sw.any(axis=2), lastrow, nd["last"])
              cum = np.cumsum(hitm, axis=2)
              kill = np.where(np.any(cum >= need, axis=2), T + np.argmax(cum >= need, axis=2), 0)
              lx = xi[:, :, NI]
              lp = M.ped_of(lx)
              pre = np.zeros((nX, n))
              for q in range(nX):
                  jj = int(jarr[q])
                  xs_ = np.full(n, nd["x"])
                  if jj:
                      sgn = 1 if jj > 0 else -1
                      for k in range(abs(jj)):
                          xs_[n - abs(jj) + k] = nd["x"] + 1.5 * sgn * (k + 1)
                  pre[q] = xs_
              idx = np.argwhere(~bad)
              if sl is not None:
                  idx = idx[jarr[idx[:, 0]] == 0]
              if not len(idx):
                  continue
              Nn = len(idx)
              RX = np.floor(np.concatenate([pre[idx[:, 0]], xi[idx[:, 0], idx[:, 1], :NI]], axis=1)).astype(np.int64)
              RY = np.concatenate([np.full(n, 160), PJ[:NI]]).astype(np.int64)
              SWm = np.concatenate([np.zeros((Nn, n), bool), sw[idx[:, 0], idx[:, 1], :NI]], axis=1)
              if sl is not None:
                  SWm[:, n - 2 - sl] = True
              fb0 = np.broadcast_to(nd["fb"][None], (Nn, NE, 7))
              fb1, hurt = sim_rows(fb0, nd["t"], RX, RY, SWm, F)
              nzv = V != 0
              lastnz = np.where(nzv.any(axis=2), NI - np.argmax(nzv[:, :, ::-1], axis=2), -1)
              for m, (xq, h) in enumerate(idx):
                  if hurt[m]:
                      continue
                  li = int(lastnz[xq, h])
                  if li >= 0:
                      pe, pd = T + li, int(np.sign(V[xq, h, li]) * F)
                  elif jarr[xq] != 0:
                      pe, pd = T - 1, int(np.sign(jarr[xq]))
                  else:
                      pe, pd = nd.get("pe", -99), nd.get("pd", 0)
                  out.append((T, float(Xs[xq]), F, int(h) + 1000 * mode, int(cnt[xq, h]), int(lastrow[xq, h]),
                              int(kill[xq, h]), float(lx[xq, h]), int(lp[xq, h]), fb1[m], pe, pd))
    return out


def sim_jump(T, X, F, h, last, mode, walked=False):
    """one jump (same rules as expand) -> (swing rows, hit rows, x profile, velocity rows)"""
    V = D[h].copy()
    if walked and FROM1[h]:
        V[0] = 1.5
    jx = JX[T:T + NI + 1]
    xi = np.clip(X + F * np.cumsum(V), 24, 236)
    ok = YOK & (F * (jx - xi) >= BLO) & (F * (jx - xi) <= BHI)
    sw = np.zeros(NI + 1, bool)
    ls = last
    for i in range(2, NI - 1):
        if ok[i] and T + i - ls >= 5:
            sw[i] = True
            ls = T + i
    if mode == 1:
        hits = [i for i in range(NI + 1) if sw[i]]
        ls = last - T
        for i in range(2, NI - 1):
            nx = min([j for j in hits if j > i] + [999])
            if not sw[i] and i - ls >= 5 and nx - i >= 5:
                sw[i] = True
            if sw[i]:
                ls = i
    dr = np.zeros(NI + 1, bool)
    for i in range(NI + 1):
        if sw[i]:
            V[i] = 0.0
            V[i - 1] = 0.0
            dr[i] = dr[i - 1] = True
    clean(V, dr)
    xi = np.clip(X + F * np.cumsum(V), 24, 236)
    ok = YOK & (F * (jx - xi) >= BLO) & (F * (jx - xi) <= BHI)
    return [T + i for i in range(NI + 1) if sw[i]], [T + i for i in range(NI + 1) if sw[i] and ok[i]], xi, V


def slash_children(nd, maxwait):
    """ground slash on the pedestal (B at r, blade on r+6), optionally after a 2-row turn tap. Measured: Ryu is locked
    until r+16 (a jump before r+16 cancels the slash but that jump cannot attack at all), so the child node is r+16."""
    if not nd["fb"][:, 0].any():
        return []
    a, b = PEDS[int(M.ped_of(nd["x"]))]
    out = []
    for f in (1, -1):
        turn = f != nd["face"]
        x = nd["x"] + (3.0 * f if turn else 0.0)
        if not (a <= x <= b):
            continue
        rs = [r for r in range(nd["t"] + (2 if turn else 0), nd["t"] + maxwait + 1) if r - nd["last"] >= 5]
        if not rs:
            continue
        N = len(rs)
        L = rs[-1] + 16 - nd["t"]
        RX = np.full((N, L), int(x), np.int64)
        if turn:
            for q, r in enumerate(rs):
                RX[q, :r - 2 - nd["t"]] = int(nd["x"])
                RX[q, r - 2 - nd["t"]] = int(nd["x"] + 1.5 * f)
        SW = np.zeros((N, L), bool)
        for q, r in enumerate(rs):
            SW[q, r + 6 - nd["t"]] = True
        # simulate each candidate only up to its own r+8: run the full length and re-run per candidate end
        for q, r in enumerate(rs):
            Lq = r + 16 - nd["t"]
            fb1, hurt = sim_rows(nd["fb"][None], nd["t"], RX[q:q + 1, :Lq], np.full(Lq, 160), SW[q:q + 1, :Lq], f)
            if hurt[0]:
                continue
            out.append((r, f, turn, x, fb1[0]))
    return out


def plan(tag, maxwait=50, beam=80):
    starts = []
    for T in range(1, 3):
        for k in [0] + list(range(2, 20)):
            X = X0 + 1.5 * k
            starts.append(dict(x=X, t=T + 19, face=1, hits=0, last=-99, fb=fb_init(), pe=(T + k if k else -99), pd=1,
                               steps=[("floorjump", T, X0, 1, k)]))
    beamL = starts
    best = None
    for depth in range(12):
        kids = {}
        for nd in beamL:
            for (T, X, F, h, cnt, last, kill, lx, lp, fb, pe, pd) in expand(nd, maxwait, NEED - nd["hits"]):
                tot = nd["hits"] + cnt
                st = ("jump", T, X, F, HOLDS[h % 1000], cnt, h // 1000)
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
                key = (lp, round(lx / 3), F, tot, int(fb[:, 0].sum()))
                if key not in kids or kids[key]["t"] > lt or (kids[key]["t"] == lt and kids[key]["last"] > last):
                    kids[key] = dict(x=lx, t=lt, face=F, hits=tot, last=last, fb=fb, pe=pe, pd=pd, steps=nd["steps"] + [st])
        for nd in beamL:
            for (r, f, turn, x, fb) in slash_children(nd, maxwait):
                if int(fb[:, 0].sum()) >= int(nd["fb"][:, 0].sum()):
                    continue                       # only slashes that kill something
                key = (int(M.ped_of(x)), round(x / 3), f, nd["hits"], int(fb[:, 0].sum()))
                lt = r + 16
                if key not in kids or kids[key]["t"] > lt:
                    kids[key] = dict(x=x, t=lt, face=f, hits=nd["hits"], last=r, fb=fb,
                                     pe=(r - 1 if turn else nd.get("pe", -99)), pd=(f if turn else nd.get("pd", 0)),
                                     steps=nd["steps"] + [("slash", r, f, int(turn))])
        cand = sorted(kids.values(), key=lambda c: c["t"] - 11 * c["hits"] + 12 * int(c["fb"][:, 0].sum()))
        beamL = cand[:beam]
        print("depth", depth, "kids", len(kids), "beam", [(c["t"], c["hits"]) for c in beamL[:10]], flush=True)
        if not beamL:
            break
    (P / "logs" / "r4" / f"jq_plan_{tag}.json").write_text(json.dumps(best, default=float, indent=1))
    TOP.sort(key=lambda d: d["kill"])
    (P / "logs" / "r4" / f"jq_top_{tag}.json").write_text(json.dumps(TOP[:300], default=float))
    return best


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "q1"
    mw = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    bw = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    b = plan(tag, mw, bw)
    print("BEST", b and b["kill"])
