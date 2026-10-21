"""A fight, redone hit by hit (2026-10-02).

The old "kill sections" were a damage-ranked beam over walking/jumping actions: they wandered (Level 12's nine
fights take ~2,250 frames; the record spends about 90 on each Hornhead). This does one thing: from the old run's
state at frame a, find the fastest series of hits that kills the enemy, then walk back to the exact spot and facing
the old run has at frame b, so that the old inputs from b on can be re-fitted (rngfit.py) behind it.

  kill    beam over hits: at every wait w (0..) try a few lead-ins (step/dash/jump toward the enemy) + B and see
          whether the enemy's health drops within 26 frames with the toad unhurt and still on its platform
  return  breadth-first over {nothing, Left, Right} per frame to the old run's state at b (x, height, facing, idle)

    python fightbeam.py <segment> <a> <b0-b1> <enemy ids, hex> [out]
        the return may join the old run at ANY frame b in b0..b1 (same x, height, facing, speed), e.g. the frames
        of a run-up; -> knowledge/fight_<out>.json {a, b, inputs}: new inputs replace old[a:b]; bookmark fight_<out>_end
    env FB_WIDTH (4), FB_WAIT (70), FB_WAIT1 (220: the first hit - the enemy may still be flying in), FB_WRAP (512)
"""
import json
import os
import sys

from toads.emulator import BizHawk, LOGS_DIR

WIDTH = int(os.environ.get("FB_WIDTH", 3))
WAIT = int(os.environ.get("FB_WAIT", 60))
WAIT1 = int(os.environ.get("FB_WAIT1", 200))
WRAP = int(os.environ.get("FB_WRAP", 512))
# T = toward the enemy, W = away, J = jump (A); a trailing "!" = the blow is direction+B (the boot out of a dash: 24-frame
# wind-up, kills a Hornhead that has been hit once - the TAS's two-blow kill), otherwise B alone
LEADS = ["", "T", "T!", "T|T", "T|T|T|T", "T||T", "T||T!", "T||T|T|T", "T||T|T|T!", "T||T|T|T|T|T!", "T||T|T|T|T|T|T|T",
         "T||T|T|T|T|T|T|T!", "T||T|T|T|T|T|T|T|T|T|T|T!", "W|T", "W||W|W|W",
         "J|J|J|J", "J|J|J|J|J|J|J|J", "T+J|T+J|T+J|T+J", "T+J|T+J|T+J|T+J|T+J|T+J|T+J|T+J", "T+J|T+J|T+J|T+J!", "T+J|T+J|T+J|T+J|T+J|T+J|T+J|T+J!",
         "T||T+J|T+J|T+J|T+J|T+J|T+J", "T||T+J|T+J|T+J|T+J|T+J|T+J!"]
if os.environ.get("FB_LONG"):                                   # the big boot: a run-up of 28-44 frames toward the foe, then direction+B (47 damage when the lunge lands on a Hornhead in flight)
    LEADS += ["|".join(["T"] * n) + "!" for n in (28, 32, 36, 40, 44)]
    LEADS += ["|".join(["W"] * k) + "|" + "|".join(["T"] * n) + "!" for k in (8, 16) for n in (32, 40)]


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def th(m):
    return m[0x439] | m[0x42A] << 8


def foes(m, ids):
    return [(q, m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x51A + q]) for q in range(2, 15) if m[0x3C1 + q] in ids]


def tot(m, ids):
    return sum(hp for q, x, h, hp in foes(m, ids))


def toward(m, ids):
    live = [f for f in foes(m, ids) if f[3] > 0]
    if not live:
        return "Right"
    x = tx(m)
    q, ex, eh, hp = min(live, key=lambda f: abs((f[1] - x + WRAP // 2) % WRAP - WRAP // 2))
    return "Right" if (ex - x + WRAP // 2) % WRAP - WRAP // 2 >= 0 else "Left"


def expand(lead, t):
    """-> the lead-in presses and the blow itself"""
    w = "Left" if t == "Right" else "Right"
    blow = "B"
    if lead.endswith("!"):
        lead, blow = lead[:-1], t + "+B"
    out = []
    for tok in (lead.split("|") if lead else []):
        out.append("+".join({"T": t, "W": w, "J": "A"}[p] for p in tok.split("+") if p))
    return out + [blow]


class Line:
    def __init__(self, e):
        self.e = e
        self.ins = []

    def st(self, b, n=1):
        for _ in range(n):
            self.e.step(tuple(v for v in b.split("+") if v), 1)
            self.ins.append(b)
        return self.e.ram(0, 0x800)


def k5(m):
    return (tx(m), th(m), m[0x475], m[0x4A2] & 0x40, m[0x565])


def camk(m):
    return 0 if os.environ.get("FB_CAMTOL") else m[0x89] | m[0x8A] << 8      # (our camera rests 1 px off the old's: FB_CAMTOL=1 ignores it)



def main(seg, a, b, ids, out=None):
    a = int(a)
    b0, b1 = (int(v) for v in (b.split("-") if "-" in b else (b, b)))
    ids = {int(v, 16) for v in ids.split(",")}
    out = out or f"{seg}_{a}"
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    old = [x.replace(",", "+") for x in d["inputs"]]
    e = BizHawk(log_name=f"fightbeam_{out}.log")
    e.load(d["bookmark"])
    L = Line(e)
    sa = None
    targets = {}                                                 # state -> old frames already played (b)
    for i, x in enumerate(old[:b1]):
        if i == a:
            sa = e.msave()
        m = L.st(x)
        if i + 1 >= b0 and m[0x475] == 0:
            targets.setdefault(k5(m) + (camk(m), bool(foes(m, ids))), i + 1)   # same camera, the body gone (it holds the camera)
    txs = sorted(k[0] for k in targets)
    hts = min(k[1] for k in targets)
    print(f"old run at {b0}..{b1}: {len(targets)} states, x {txs[0]}..{txs[-1]}, h {hts}; foes {foes(m, ids)}", flush=True)
    if os.environ.get("FB_START"):                               # start from this bookmark instead of the old run's state at a
        e.mfree(sa); e.load(os.environ["FB_START"]); sa = e.msave()
    e.mload(sa)
    L.ins = []
    m = e.ram(0, 0x800)
    k = a
    while not foes(m, ids) and k < b1:                           # the enemy spawns with the camera: the old run's own moves bring it
        m = L.st(old[k])
        k += 1
    if k > a:
        print(f"the enemy appears after the old run's inputs {a}..{k - 1} (kept as the piece's prefix)", flush=True)
        e.mfree(sa)
        sa = e.msave()
    hp0, lives0, h0 = m[0x51A], m[0x11], th(m)
    print(f"start at {a}: toad x {tx(m)} h {h0} foes {foes(m, ids)}", flush=True)

    def safe(m):
        return m[0x51A] >= hp0 and m[0x11] == lives0 and th(m) >= min(h0, hts) - 30

    # ---- kill
    beam = [(len(L.ins), sa, list(L.ins), None, False)]           # frames, state, inputs, foe health left (None = not seen), seen
    hitno = 0
    done = []
    while beam and not done:
        nxt = []
        for f, sid, ins, left, seen in beam:
            found = set()
            e.mload(sid)
            L.ins = list(ins)
            for w in range(WAIT if seen else WAIT1):
                m = e.ram(0, 0x800)
                if not safe(m):
                    break
                cur = tot(m, ids)
                sn = seen or bool(foes(m, ids))
                if sn and left is not None and cur < left:        # a late hit of the last blow: take it as it is
                    left = cur
                if sn and cur == 0:
                    nxt.append((len(L.ins), e.msave(), list(L.ins), 0, True, "(none)", w, tx(m)))
                    break
                if sn:
                    here = e.msave()
                    nh = len(L.ins)
                    t = toward(m, ids)
                    for lead in LEADS:
                        if lead in found:
                            continue
                        e.mload(here)
                        del L.ins[nh:]
                        for x in expand(lead, t):
                            m = L.st(x)
                        got = None
                        for _ in range(40 if lead.endswith("!") else 26):
                            if not safe(m):
                                break
                            c2 = tot(m, ids)
                            if c2 < cur:
                                got = c2
                                break
                            m = L.st("")
                        if got is None:
                            continue
                        for _ in range(70):                       # the blow must end on the ground (a kick off the ledge is no use)
                            if m[0x475] == 0 or not safe(m):
                                break
                            m = L.st("")
                        if m[0x475] != 0 or not safe(m):
                            continue
                        got = min(got, tot(m, ids))
                        found.add(lead)
                        nxt.append((len(L.ins), e.msave(), list(L.ins), got, True, lead, w, tx(m)))
                    e.mload(here)
                    e.mfree(here)
                    del L.ins[nh:]
                m = L.st("")
                seen = sn
                if left is None and sn:
                    left = tot(m, ids)
        for n in beam:
            if n[1] != sa:
                e.mfree(n[1])
        if not nxt:
            print("no next hit from any beam state", flush=True)
            break
        hitno += 1
        nxt.sort(key=lambda n: (n[3], n[0] + min(abs(n[7] - txs[0]), abs(n[7] - txs[-1])) / 3))   # (the way back counts)
        keep, seenx = [], set()
        for n in nxt:
            k = (n[7], n[3])
            if k in seenx or len(keep) >= WIDTH:
                e.mfree(n[1])
                continue
            seenx.add(k)
            keep.append(n)
        print(f"hit {hitno} ->", [(n[0], n[3], n[5], n[6], n[7]) for n in keep], flush=True)
        done = [n for n in keep if n[3] == 0]
        beam = [n[:5] for n in keep]
    if not done:
        e.close()
        return None

    # ---- return: join the old run at any frame of the window
    best = None
    for f, sid, ins, left, seen, *_ in sorted(done, key=lambda n: n[0])[:3]:
        e.mload(sid)
        frontier = [(e.msave(), [], tx(e.ram(0, 0x800)))]
        seenk = set()
        goal = None
        for depth in range(int(os.environ.get("FB_RETDEPTH", 420))):
            new = []
            for st, path, _ in frontier:
                for act in ("", "Left", "Right", "A", "Left+A", "Right+A"):
                    e.mload(st)
                    e.step(tuple(v for v in act.split("+") if v), 1)
                    m = e.ram(0, 0x800)
                    if not safe(m):
                        continue
                    k = k5(m) + (camk(m), bool(foes(m, ids)))
                    kk = k + (m[0x3B5], m[0x457]) + tuple(m[0x3C1 + 15 * j] for j in range(-1, 32))   # the toad's whole column (timers too)
                    if kk in seenk:
                        continue
                    seenk.add(kk)
                    p2 = path + [act]
                    if os.environ.get("FB_SPRING"):              # goal: standing on the lower circling spring (0x36 at H 4800)
                        H = m[0x439] | m[0x42A] << 8
                        if m[0x475] == 0 and 4800 <= H <= 4810 and any(m[0x3C1 + q] == 0x36 and (m[0x439 + q] | m[0x42A + q] << 8) == 4800 for q in range(2, 15)):
                            goal = (e.msave(), p2, a + len(ins) + len(p2))
                            break
                    elif k in targets:
                        goal = (e.msave(), p2, targets[k])
                        break
                    new.append((e.msave(), p2, min(abs(k[0] - txs[0]), abs(k[0] - txs[-1]))))
                if goal:
                    break
            for st, _, _ in frontier:
                e.mfree(st)
            if goal:
                for st, _, _ in new:
                    e.mfree(st)
                break
            if os.environ.get("FB_DEBUG") and depth % 20 == 0:
                e.mload(new[0][0]) if new else None
                print(f"   return depth {depth}: {len(new)} states, nearest {min((n[2] for n in new), default=None)}, seen {len(seenk)}", flush=True)
            new.sort(key=lambda n: n[2])                          # keep the frontier small: nearest the window first
            for st, _, _ in new[300:]:
                e.mfree(st)
            frontier = new[:300]
            if not frontier:
                break
        if goal:
            total = list(ins) + goal[1]
            print(f"kill in {f} frames + return in {len(goal[1])} = {len(total)}, joins the old run at {goal[2]} (old {goal[2] - a})", flush=True)
            if best is None or len(total) - goal[2] < len(best[0]) - best[2]:
                best = (total, goal[0], goal[2])
                json.dump({"segment": seg, "a": a, "b": best[2], "inputs": best[0]}, open(f"knowledge/fight_{out}.json", "w"))   # (saved at once: the other returns may crawl)
        else:
            print(f"kill in {f} frames, but no way back to the old run found", flush=True)
    if best is None:
        e.close()
        return None
    e.mload(best[1])
    e.save(f"fight_{out}_end")
    json.dump({"segment": seg, "a": a, "b": best[2], "inputs": best[0]}, open(f"knowledge/fight_{out}.json", "w"))
    print(f"saved knowledge/fight_{out}.json: {len(best[0])} frames for old {best[2] - a} (saves {best[2] - a - len(best[0])})", flush=True)
    e.close()
    return best[0]


if __name__ == "__main__":
    main(*sys.argv[1:])
