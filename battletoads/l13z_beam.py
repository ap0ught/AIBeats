"""Dark Queen beam search, second generation (2026-10-09, track L13 of the timing fix).

Why a new engine (the old one is l4s.py 'ctr' mode driven by l13solve.py):
  * the real clock stops at the cut to PROFESSOR T. BIRD, not at the last hit. Measured (l13z_tailstat.py, l13z_tail1.py):
        T. Bird cut = kill frame + body flight + 1002
    where the body flight (kill -> her object 0x7E re-appears under the floor and $586 starts counting 207 down) is
    154 frames for a kill at floor height (h 44) and up to 169 for a kill at h 153; everything after it is fixed:
    207 (countdown) + 171 (she rises at x 128) + 122 + 11 (speech skipped with A from its 10th frame) + 491.
    One hazard: a toad standing near x 128 while she rises is killed by her (+27 frames) - walk away after the kill.
  * speed: own bridge (l13z_bridge.lua) with a batch command - one round trip expands a node with every action - and a
    private EmuHawk config with the display off: ~0.7 ms per 2-frame child instead of ~9 ms per 4-frame child.
  * 2-frame decisions (the old search decided every 4 frames), actions of different lengths land in time buckets;
    the state key holds the toad's animation and the queen's place/velocity (the old key was the toad's cell only, so a
    smash wind-up and a plain jump in the same cell collided); a share of the beam is reserved for lines one hit behind.

Used by l13solve2.py. Nothing here writes memory: inputs only.
"""
import json
import time
import types

import toads.emulator as E

E.BRIDGE_LUA = E.PROJECT / "l13z_bridge.lua"          # this process only: the batch-capable bridge
_loads = json.loads


def _loads_fast(s, *a, **k):
    d = _loads(s, *a, **k)
    if isinstance(d, dict) and "FrameSkip" in d:          # EmuHawk's config: draw nothing, never throttle
        d.update({"DispSpeedupFeatures": 0, "FrameSkip": 9, "Unthrottled": True, "DisplayMessages": False})
    return d


E.json = types.SimpleNamespace(loads=_loads_fast, dumps=json.dumps)

G = [0x10, 0x11, 0x0B, 0x586, 0x25, 0x26, 0x27, 0x28, 0x3FD, 0x3EE, 0x439, 0x475, 0x3B5, 0x4B1, 0x4A2, 0x565, 0x4C0, 0x4CF, 0x448, 0x51A]
S = [0x3C1, 0x3FD, 0x3EE, 0x439, 0x475, 0x4C0, 0x4CF, 0x565, 0x556, 0x4A2, 0x4FC, 0x50B, 0x4DE, 0x4ED, 0x3DF, 0x4B1, 0x51A]
NG = len(G)
QUEEN, BODY = 0x7E, 0x46
TAIL_FIXED = 1002          # (first measurement, the published ending: body gone -> T. Bird; the ending is NOT fixed, see l13z_tail.py)
TAIL_BEST = 207 + 171 + 122 + 9 + 410   # body gone -> T. Bird at best: countdown, rise, wait, speech load, last scene


class F:
    """one state's features"""
    __slots__ = ("lvl", "lives", "t0b", "ctr", "rng", "tx", "th", "tz", "tan", "tst", "tface", "tspd", "tvy", "tdirv", "thp",
                 "slot", "qid", "qx", "qh", "qz", "qvy", "qkb", "qdir", "qface", "qt1", "qt2", "qe1", "qe2", "qa", "qst", "qhp")

    def __init__(self, hexs):
        b = bytes.fromhex(hexs)
        self.lvl, self.lives, self.t0b, self.ctr = b[0], b[1], b[2], b[3]
        self.rng = b[4:8]
        self.tx = b[8] + 256 * b[9]
        self.th, self.tz, self.tan, self.tst, self.tface, self.tspd = b[10], b[11], b[12], b[13], b[14], b[15]
        self.tvy = ((b[16] << 8 | b[17]) + 32768) % 65536 - 32768
        self.tdirv, self.thp = b[18], b[19]
        self.slot = b[NG]
        if self.slot != 255:
            s = b[NG + 1:]
            self.qid = s[0]
            self.qx = s[1] + 256 * s[2]
            self.qh, self.qz = s[3], s[4]
            self.qvy = ((s[5] << 8 | s[6]) + 32768) % 65536 - 32768
            self.qkb, self.qdir, self.qface, self.qt1, self.qt2, self.qe1, self.qe2, self.qa, self.qst, self.qhp = s[7:17]
        else:
            self.qid = 0
            self.qx, self.qh, self.qz, self.qvy, self.qkb, self.qdir, self.qface = 88, 44, 0, 0, 0, 0, 0
            self.qt1 = self.qt2 = self.qe1 = self.qe2 = self.qa = self.qst = self.qhp = 0

    @property
    def killed(self):
        return self.qid == BODY and self.ctr >= 240

    @property
    def hits(self):
        return 21 if self.killed else self.ctr // 12


class Emu(E.BizHawk):
    def __init__(self, log_name):
        super().__init__(log_name=log_name)
        self.cmd("xg " + ",".join(str(a) for a in G))
        self.cmd("xs " + ",".join(str(a) for a in S))
        self.cmd(f"xi {QUEEN},{BODY}")

    def xp(self, sid, acts, save=False):
        """acts: list of tuples of frame strings ('-' or 'Right,A'). -> [(newsid|None, F)]"""
        r = self.cmd(f"xp {sid or '-'} {1 if save else 0} " + "|".join(";".join(a) for a in acts))
        out = []
        for part in r.split("|"):
            i, _, h = part.partition(":")
            out.append((None if i == "-" else i, F(h)))
        return out

    def feat(self):
        b = self.ram_all()
        h = bytes(b[a] for a in G)
        slot = next((s for s in range(2, 15) if b[0x3C1 + s] in (QUEEN, BODY)), 255)
        h += bytes([slot]) + (bytes(b[a + slot] for a in S) if slot != 255 else b"")
        return F(h.hex())

    def xfree(self, ids):
        ids = [i for i in ids if i]
        for k in range(0, len(ids), 60):
            self.cmd("xfree " + ",".join(ids[k:k + 60]))


def mk(*btn, n=2):
    return tuple([",".join(btn) if btn else "-"] * n)


def actions(M, select=1):
    """(ground set, air set, air A-continue set, frozen set); every action is a tuple of per-frame button strings"""
    R, L, A, B, SEL = "Right", "Left", "A", "B", "Select"
    ground = [mk(n=M), mk(R, n=M), mk(L, n=M), mk(A, n=M), mk(R, A, n=M), mk(L, A, n=M), mk(B, n=M), mk(R, B, n=M), mk(L, B, n=M),
              (R, "-", R, R), (L, "-", L, L), (R, "-", R, R + "," + A), (L, "-", L, L + "," + A)]
    air = [mk(n=M), mk(R, n=M), mk(L, n=M), mk(B, n=M), mk(R, B, n=M), mk(L, B, n=M)]
    aira = [mk(A, n=M), mk(R, A, n=M), mk(L, A, n=M)]
    frozen = [mk(n=M)]
    if select >= 1:
        ground.append(mk(SEL, n=M)); air.append(mk(SEL, n=M)); frozen.append(mk(SEL, n=M))
    if select >= 2:
        for lst in (ground, air):
            lst += [mk(R, SEL, n=M), mk(L, SEL, n=M), mk(B, SEL, n=M)]
    return ground, air, aira, frozen


def flight_est(h):
    """frames from the kill to the body's despawn, by her height at the kill (measured: 44 -> 154 ... 153 -> 169)"""
    return 154 + 0.14 * max(0, h - 44)


class Node:
    __slots__ = ("sid", "parent", "act", "t", "f", "aheld", "frozen", "key", "rank")

    def __init__(self, parent, act, t, f):
        self.sid, self.parent, self.act, self.t, self.f = None, parent, act, t, f
        self.aheld = bool(act) and "A" in act[-1].split(",")
        self.frozen = parent is not None and f.t0b == parent.f.t0b

    def inputs(self):
        out, n = [], self
        while n is not None and n.act is not None:
            out.append(n.act); n = n.parent
        res = []
        for a in reversed(out):
            res += ["" if fr == "-" else fr.replace(",", "+") for fr in a]
        return res


def make_key(n):
    f = n.f
    return (f.hits, f.tx // 4, f.th // 4, f.tz > 0, n.aheld and f.tz > 0, f.tan, f.tspd >= 160, f.tface & 0x40, f.tdirv // 64,
            f.qid, f.qx // 8, f.qh // 8, f.qvy >> 8, f.qkb // 64, n.frozen)


ATK_BONUS = {38: 12.0, 87: 12.0, 25: 6.0, 29: 8.0, 35: 4.0}


FD = 0.25                  # rank: weight of the toad-queen distance (px) against 1000 per hit


def make_rank(n, fd=None):
    fd = FD if fd is None else fd
    f = n.f
    dx = abs(f.tx - f.qx)
    dh = abs(f.th - f.qh)
    r = -f.hits * 1000 + fd * (dx + dh)
    if dx + dh < 64:
        r -= ATK_BONUS.get(f.tan, 0.0)
    return r


def search(e, root_sid, root_f, width=400, M=2, select=1, max_frames=1400, log=print, quota=(0.72, 0.23, 0.05), cellcap=None,
           stop_hits=21, ck_path=None, t0_frames=0, hp0=47, hp_from=12, extra=40, max_cands=600):
    """Time-bucketed beam from the in-memory state root_sid. Returns (candidates, stats): candidates = kill nodes
    [(est score, node)] with node.sid saved; score = kill time + estimated body flight (search-relative frames).
    The search runs on for `extra` frames after the first kill: the ending's length depends on the queen's state at the
    kill (height, leftover timer), so a kill a few frames later can give an earlier cut to T. Bird (l13z_tail.py)."""
    GROUND, AIR, AIRA, FROZEN = actions(M, select)
    lives0 = root_f.lives
    root = Node(None, None, 0, root_f)
    root.sid = root_sid
    root.key, root.rank = make_key(root), make_rank(root)
    buckets = {0: {root.key: root}}
    alive = {}                      # t -> [nodes with sid] (kept until t+4 has been materialised)
    cands = []
    cand_keys = set()
    t_first_kill = None
    best = None
    t_start = time.time()
    evals = 0
    first_hit_t = {}
    cellcap = cellcap or max(3, width // 50)
    t = 0
    while buckets:
        t = min(buckets)
        if t > max_frames:
            break
        if t_first_kill is not None and t > t_first_kill + extra:
            break
        cur = list(buckets.pop(t).values())
        # ---- truncate: quotas per hit level (the lowest level shown takes what is left), a cap per coarse cell for diversity
        levels = sorted({n.f.hits for n in cur}, reverse=True)[:len(quota)]
        keep = []
        remaining = width
        cnt = {}
        for n in cur:
            cnt[n.f.hits] = cnt.get(n.f.hits, 0) + 1
        for i, lv in enumerate(levels):
            reserved = sum(min(int(round(width * quota[j])), cnt[levels[j]]) for j in range(i + 1, len(levels)))   # the shares of the levels behind
            q = max(0, remaining - reserved)
            grp = sorted((n for n in cur if n.f.hits == lv), key=lambda n: n.rank)
            took, cells, rest = [], {}, []
            for n in grp:
                c = (n.f.tx // 16, n.f.th // 16, n.f.qx // 32, n.f.qh // 32, n.f.tz > 0)
                if cells.get(c, 0) < cellcap and len(took) < q:
                    cells[c] = cells.get(c, 0) + 1; took.append(n)
                else:
                    rest.append(n)
            if len(took) < q:
                took += rest[:q - len(took)]
            remaining -= len(took)
            keep += took
        # ---- materialise the kept nodes (re-run parent + act with a save), grouped by parent
        if t > 0:
            bypar = {}
            for n in keep:
                bypar.setdefault(id(n.parent), (n.parent, []))[1].append(n)
            for par, ns in bypar.values():
                res = e.xp(par.sid, [n.act for n in ns], save=True)
                evals += len(ns)
                for n, (sid, f) in zip(ns, res):
                    n.sid = sid
                    if f.rng != n.f.rng or f.tx != n.f.tx or f.ctr != n.f.ctr:
                        raise RuntimeError(f"re-simulation mismatch at t {t}: {n.act}")
        alive[t] = keep
        for told in [k for k in alive if k <= t - 5]:
            e.xfree([n.sid for n in alive.pop(told) if n is not root and not getattr(n, "_keep", False)])
        # ---- expand
        for n in keep:
            f = n.f
            if n.frozen:
                acts = FROZEN + ([mk("A", n=M)] if n.aheld else [])     # hit-stop: inputs are not read (a held A stays held)
            elif f.tz > 0:
                acts = AIR + (AIRA if n.aheld else [])
            else:
                acts = GROUND
            res = e.xp(n.sid, acts, save=False)
            evals += len(acts)
            for act, (_, cf) in zip(acts, res):
                if cf.lvl != 13 or cf.lives < lives0 or (cf.thp < hp0 and t0_frames + t + len(act) >= hp_from):
                    continue
                c = Node(n, act, t + len(act), cf)
                if cf.killed:
                    sc = c.t + flight_est(cf.qh)
                    ck = (c.t, cf.qh, cf.qx, cf.qe1, cf.qe2, cf.tx // 8)
                    if ck in cand_keys or len(cands) >= max_cands:
                        continue
                    cand_keys.add(ck)
                    sid = e.xp(n.sid, [act], save=True)[0][0]
                    c.sid = sid
                    cands.append((sc, c))
                    if t_first_kill is None:
                        t_first_kill = c.t
                    if best is None or sc < best:
                        best = sc
                        log(f"  KILL candidate at t {c.t} (her h {cf.qh}, timer {cf.qe1}/{cf.qe2}, toad x {cf.tx}): body gone at ~{sc:.0f}")
                    continue
                if cf.hits >= stop_hits:
                    continue
                c.key, c.rank = make_key(c), make_rank(c)
                b = buckets.setdefault(c.t, {})
                o = b.get(c.key)
                if o is None or c.rank < o.rank:
                    b[c.key] = c
                if cf.hits not in first_hit_t:
                    first_hit_t[cf.hits] = c.t
                    log(f"  hit {cf.hits} first reached at t {c.t} ({time.time() - t_start:.0f}s, {evals} evals)")
        if (t // M) % 25 == 0:
            lv = {}
            for n in keep:
                lv[n.f.hits] = lv.get(n.f.hits, 0) + 1
            b0 = min(keep, key=lambda n: n.rank) if keep else None
            log(f"  t {t}: kept {len(keep)} {dict(sorted(lv.items(), reverse=True))} best toad ({b0.f.tx},{b0.f.th}) an {b0.f.tan} queen ({b0.f.qx},{b0.f.qh}) "
                f"({time.time() - t_start:.0f}s, {evals} evals)" if b0 else f"  t {t}: empty")
            if ck_path and keep:
                ck = {"t": t, "t0_frames": t0_frames, "lines": [n.inputs() for n in sorted(keep, key=lambda n: n.rank)[:width]]}
                tmp = str(ck_path) + ".tmp"
                json.dump(ck, open(tmp, "w"))
                __import__("os").replace(tmp, ck_path)
        if not keep:
            log(f"  died out at t {t}")
            break
    stats = {"evals": evals, "seconds": time.time() - t_start, "first_hit_t": first_hit_t, "t_end": t}
    return sorted(cands, key=lambda c: c[0]), stats
