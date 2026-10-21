"""One Level 12 fight on the TAS's path (2026-10-03): old inputs to the sync frame a, the TAS's inputs k0.. until
the enemy spawns, then a hit-beam kill of our own (fightbeam's recipe), then a walk back onto a TAS log state in
rows [r0, r1] (x, h, z, anim), then the TAS's inputs again to row rend (= old frame b). Output: a piece for
tasvirtual-style stitching: knowledge/tasfight_<out>.json {a, b, inputs}.
    python tasfight.py <out> <a> <b> <k0> <rowa> <ids hex> <r0> <r1> <rend>"""
import json, re, sys, os
from toads.emulator import BizHawk, LOGS_DIR
from fightbeam import foes, tot, toward, expand, LEADS, tx, th, Line
out = sys.argv[1]; a, b, k0, rowa = map(int, sys.argv[2:6]); ids = sys.argv[6]; r0, r1, rend = map(int, sys.argv[7:10])
ids = {int(v, 16) for v in ids.split(",")}
rows = [l for l in open("tas/watch_1p_l12.txt") if " x=" in l]
def xy(l): m = re.search(r"x=(\d+) h=(\d+) z=(\d+) st=\d+ an=(\d+)", l); return tuple(int(v) for v in m.groups())
tas = [x.replace(",", "+") for x in json.load(open("knowledge/tas1p_l12_inputs.json"))]
d = json.load(open(LOGS_DIR / "pbeam_L12a.json")); old = [x.replace(",", "+") for x in d["inputs"]]
e = BizHawk(log_name=f"tasfight_{out}.log"); e.load(d["bookmark"])
L = Line(e)
for x in old[:a]: L.st(x)
L.ins = []
m = e.ram(0, 0x800)
k = k0
while not foes(m, ids):                                      # the TAS's own approach until the enemy is there
    m = L.st(tas[k]); k += 1
print(f"enemy spawns after TAS input {k - 1} (piece frame {len(L.ins)}); toad {tx(m)},{th(m)}", flush=True)
hp0, lives0, h0 = m[0x51A], m[0x11], th(m)
def safe(m): return m[0x51A] >= hp0 and m[0x11] == lives0 and th(m) >= h0 - 60
WIDTH, WAIT = 3, 60
beam = [(len(L.ins), e.msave(), list(L.ins), None, True)]
done = []
while beam and not done:
    nxt = []
    for f, sid, ins, left, seen in beam:
        found = set(); e.mload(sid); L.ins = list(ins)
        for w in range(WAIT):
            m = e.ram(0, 0x800)
            if not safe(m): break
            cur = tot(m, ids)
            if left is not None and cur < left: left = cur
            if cur == 0: nxt.append((len(L.ins), e.msave(), list(L.ins), 0, "(none)", w, tx(m))); break
            here = e.msave(); nh = len(L.ins); t = toward(m, ids)
            for lead in LEADS:
                if lead in found: continue
                e.mload(here); del L.ins[nh:]
                for x in expand(lead, t): m = L.st(x)
                got = None
                for _ in range(40 if lead.endswith("!") else 26):
                    if not safe(m): break
                    c2 = tot(m, ids)
                    if c2 < cur: got = c2; break
                    m = L.st("")
                if got is None: continue
                for _ in range(70):
                    if m[0x475] == 0 or not safe(m): break
                    m = L.st("")
                if m[0x475] != 0 or not safe(m): continue
                found.add(lead); nxt.append((len(L.ins), e.msave(), list(L.ins), min(got, tot(m, ids)), lead, w, tx(m)))
            e.mload(here); e.mfree(here); del L.ins[nh:]; m = L.st("")
            if left is None: left = tot(m, ids)
    for n in beam: e.mfree(n[1])
    if not nxt: print("no next hit", flush=True); break
    nxt.sort(key=lambda n: (n[3], n[0])); keep, seenx = [], set()
    for n in nxt:                                               # one state per kind of blow: a flying kick stuns, the boot then kills
        kk = n[4]
        if kk in seenx or len(keep) >= 10: e.mfree(n[1]); continue
        seenx.add(kk); keep.append(n)
    print("hit ->", [(n[0], n[3], n[4], n[5], n[6]) for n in keep], flush=True)
    done = [n for n in keep if n[3] == 0]; beam = [n[:5] for n in keep]
if not done: e.close(); sys.exit(1)
# walk back onto the TAS's track: any row in [r0, r1] with the same (x, h, z, an), toad standing
targets = {}
for r in range(r0, r1 + 1):
    x, h, z, an = xy(rows[r])
    if z == 0: targets.setdefault((x, h, z, an), r)
best = None
for f, sid, ins, left, seen, *_ in sorted(done, key=lambda n: n[0])[:2]:
    e.mload(sid); frontier = [(e.msave(), [])]; seenk = set(); goal = None
    for depth in range(360):
        new = []
        for st, path in frontier:
            for act in ("", "Left", "Right", "A", "Left+A", "Right+A"):
                e.mload(st); e.step(tuple(v for v in act.split("+") if v), 1); m = e.ram(0, 0x800)
                if not safe(m): continue
                key = (tx(m), m[0x439], m[0x475], m[0x3B5])
                kk = key + (m[0x565], m[0x457])
                if kk in seenk: continue
                seenk.add(kk); p2 = path + [act]
                if key in targets: goal = (e.msave(), p2, targets[key]); break
                new.append((e.msave(), p2, min(abs(key[0] - xy(rows[r])[0]) for r in (r0, r1))))
            if goal: break
        for st, _ in frontier: e.mfree(st)
        if goal:
            for st, _, _ in new: e.mfree(st)
            break
        new.sort(key=lambda n: n[2]); frontier = [(s, p) for s, p, _ in new[:300]]
        for s, _, _ in new[300:]: e.mfree(s)
        if not frontier: break
    if goal:
        sid2, path, r = goal
        e.mload(sid2); seq = list(ins) + path
        # the TAS's inputs from row r+1 to rend; input index for row q = q - 24 (inputs[k] produced row k+24)
        okend = None
        for q in range(r + 1, rend + 1):
            e.step(tuple(v for v in tas[q - 24].split("+") if v), 1); seq.append(tas[q - 24])
            m = e.ram(0, 0x800)
            if not safe(m): okend = ("hurt", q); break
        m = e.ram(0, 0x800); endk = (tx(m), m[0x439], m[0x475])
        want = xy(rows[rend])[:3]
        print(f"kill {f} + back {len(path)} (joins TAS row {r}) + TAS to row {rend}: {len(seq)} frames (old {b - a}); end {endk} vs TAS {want} {okend or ''}", flush=True)
        if okend is None and abs(endk[0] - want[0]) <= 1 and abs(endk[1] - want[1]) <= 1 and (best is None or len(seq) < len(best)):
            best = seq
    else:
        print(f"kill {f}: no way back onto the TAS track", flush=True)
if best:
    json.dump({"segment": "L12a", "a": a, "b": b, "inputs": best}, open(f"knowledge/tasfight_{out}.json", "w"))
    print(f"saved knowledge/tasfight_{out}.json: {len(best)} frames for old {b - a} (saves {b - a - len(best)})", flush=True)
e.close()
