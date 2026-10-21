"""A faster way through a stretch of our own route (2026-10-02).

The old beam searches walked where they could have dashed and hopped where they could have run. This one takes
a stretch [a, b] of a segment and looks for a shorter line that ENDS in one of the old run's own states (any frame
of the window b0..b1: same x, height, z, facing, speed), so the old inputs continue from there, earlier.

  beam    one action per MACRO frames; per layer every distinct (x, h, z, facing, speed, anim) state is kept once,
          ranked by how far along the old track it is (the furthest old frame within R pixels)
  goal    a node equal to an old state at frame j: saving = (j - a) - frames used

    python shortcut.py <segment> <a> <b0-b1> [out]   -> knowledge/short_<out>.json {a, b, inputs} (a virtual.py piece)
    env SC_ACTS (comma list, default ",Right,Left,A,Right+A,Left+A,Down"), SC_MACRO (2), SC_WIDTH (150), SC_R (10),
        SC_WRAP (0: x wraps at this value, 512 in The Revolution), SC_MAXLAYERS
"""
import json
import os
import sys

from toads.emulator import BizHawk, LOGS_DIR

ACTS = os.environ.get("SC_ACTS", ",Right,Left,A,Right+A,Left+A,Down").split(",")
MACRO = int(os.environ.get("SC_MACRO", 2))
WIDTH = int(os.environ.get("SC_WIDTH", 150))
R = int(os.environ.get("SC_R", 10))
WRAP = int(os.environ.get("SC_WRAP", 0))


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def th(m):
    return m[0x439] | m[0x42A] << 8


def k5(m):
    return (tx(m), th(m), m[0x475], m[0x4A2] & 0x40, m[0x565], m[0x51A], m[0x41B])   # (health too: a join after a planned hit is no join; depth for the beat-em-up levels)


def col(m):
    """the toad's column of every object table (animation, timers, velocities): a join must match all of it"""
    return tuple(m[0x3C1 + 15 * j] for j in range(-1, 32)) + (m[0x3B5], m[0x457])


def dx(a, b):
    d = a - b
    if WRAP:
        d = (d + WRAP // 2) % WRAP - WRAP // 2
    return d


def main(seg, a, b, out=None):
    a = int(a)
    b0, b1 = (int(v) for v in (b.split("-") if "-" in b else (b, b)))
    out = out or f"{seg}_{a}"
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    old = [x.replace(",", "+") for x in d["inputs"]]
    e = BizHawk(log_name=f"shortcut_{out}.log")
    e.load(d["bookmark"])
    track, targets, sa = [], {}, None
    for i, x in enumerate(old[:b1]):
        if i == a:
            sa = e.msave()
        e.step(tuple(v for v in x.split("+") if v), 1)
        m = e.ram(0, 0x800)
        if i + 1 >= a:
            track.append((i + 1, tx(m), th(m)))
        if i + 1 >= b0 and m[0x475] == 0:                        # join on the ground only, and on the toad's whole state column
            targets.setdefault(k5(m) + col(m), i + 1)
    e.mload(sa)
    m = e.ram(0, 0x800)
    hp0, lives0 = m[0x51A], m[0x11]
    print(f"{seg} [{a}, {b0}..{b1}]: old {b0 - a}..{b1 - a} frames; {len(targets)} join states; start x {tx(m)} h {th(m)}", flush=True)

    def progress(x, h):
        best, dist = a, 10 ** 9
        for j, px, ph in track:
            dd = abs(dx(x, px)) + abs(h - ph)
            if dd <= R and j > best:
                best = j
            if dd < dist:
                dist = dd
        return best, dist

    # beam: node = (score, sid or (parent sid, action), inputs)
    layer = [((a, 0), sa, [])]
    found = None
    maxl = int(os.environ.get("SC_MAXLAYERS", (b1 - a) // MACRO + 1))
    for t in range(1, maxl + 1):
        cand = {}
        for score, sid, ins in layer:
            for act in ACTS:
                e.mload(sid)
                e.step(tuple(v for v in act.split("+") if v), MACRO)
                m = e.ram(0, 0x800)
                if m[0x51A] < hp0 or m[0x11] != lives0:
                    continue
                k = k5(m)
                key = k + (m[0x3B5],)
                if key in cand:
                    continue
                p, dist = progress(k[0], k[1])
                cand[key] = ((p, -dist), sid, act, ins + [act] * MACRO, k + col(m))
        if not cand:
            print("  layer", t, "dead", flush=True)
            break
        nodes = sorted(cand.values(), key=lambda n: n[0], reverse=True)
        joins = [(targets[n[4]] - a - t * MACRO, targets[n[4]], n) for n in nodes if n[4] in targets]
        if os.environ.get("SC_GOAL"):                           # "x,h": done when standing at x >= X on height H (no exact join)
            gx, gh = (int(v) for v in os.environ["SC_GOAL"].split(","))
            joins = [((b1 - a) - t * MACRO, b1, n) for n in nodes if n[4][0] >= gx and abs(n[4][1] - gh) <= 2 and n[4][2] == 0 and n[4][4] == 0]
        if joins:
            sv, j, n = max(joins, key=lambda q: q[0])
            if found is None or sv > found[0]:
                found = (sv, j, n[3])
                print(f"  layer {t}: joins the old run at {j} after {t * MACRO} frames (old {j - a}): saves {sv}", flush=True)
        if found and found[0] >= (b1 - a) - t * MACRO:          # nothing later can beat it
            break
        keep = nodes[:WIDTH]
        if os.environ.get("SC_BUCKETS"):                        # keep a few of the laggards too (states that crouch, wait, dodge)
            seenb, extra = {}, []
            for n in nodes[WIDTH:]:
                bkt = (n[4][0] // 16, n[4][2] > 0)
                if seenb.get(bkt, 0) < 3:
                    seenb[bkt] = seenb.get(bkt, 0) + 1; extra.append(n)
            keep = keep + extra[:400]
        new = []
        for sc, psid, act, ins, k in keep:                      # make the kept states again (only these get a savestate)
            e.mload(psid)
            e.step(tuple(v for v in act.split("+") if v), MACRO)
            new.append((sc, e.msave(), ins))
        for n in layer:
            if n[1] != sa:
                e.mfree(n[1])
        layer = new
        if t % 20 == 0:
            print(f"  layer {t}: {len(cand)} states, best progress {keep[0][0][0]} (old frame), {len(joins)} joins", flush=True)
    e.close()
    if found and found[0] > 0:
        json.dump({"segment": seg, "a": a, "b": found[1], "inputs": found[2]}, open(f"knowledge/short_{out}.json", "w"))
        print(f"saved knowledge/short_{out}.json: {len(found[2])} frames for old {found[1] - a} (saves {found[0]})", flush=True)
    else:
        print("no faster line found", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
