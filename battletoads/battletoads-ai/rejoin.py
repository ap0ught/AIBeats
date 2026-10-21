"""Rejoin the old route from OUR state (2026-10-04): a beam from our bookmark that ends in one of the old run's own
ground states in a window of old frames (same x, height, z, facing, speed, health, depth AND the toad's whole
object column), so the old inputs continue from there. shortcut.py with a foreign start.
    python rejoin.py <our bookmark> <old segment> <old bookmark> <old frame of that bookmark> <b0-b1> <out>
      -> knowledge/rejoin_<out>.json {inputs, join (old frame)}, bookmark RJ_<out>
    env SC_ACTS, SC_MACRO (2), SC_WIDTH (150), SC_R (10), SC_WRAP (512), SC_MAXLAYERS, RJ_FROM (old frame our state is at, for progress)"""
import json, os, sys
from toads.emulator import BizHawk, LOGS_DIR
import shortcut as sc
ACTS = os.environ.get("SC_ACTS", ",Right,Left,A,Right+A,Left+A,Down").split(",")
MACRO = int(os.environ.get("SC_MACRO", 2)); WIDTH = int(os.environ.get("SC_WIDTH", 150)); R = int(os.environ.get("SC_R", 10))
sc.WRAP = int(os.environ.get("SC_WRAP", 512))
def jkey(m):
    return sc.k5(m) + ((m[0x3B5], m[0x457]) + ((m[0x448], m[0x466], m[0x3DF]) if os.environ.get("RJ_FRAC") else ()) if os.environ.get("RJ_LOOSE") else sc.col(m))
def main(bm, seg, obm, of0, b, out):
    of0 = int(of0); b0, b1 = (int(v) for v in b.split("-"))
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json")); old = [x.replace(",", "+") for x in d["inputs"]]
    a = int(os.environ.get("RJ_FROM", b0))
    e = BizHawk(log_name=f"rejoin_{out}.log"); e.load(obm)
    track, targets = [], {}
    for i in range(of0, b1):
        e.step(tuple(v for v in old[i].split("+") if v), 1); m = e.ram(0, 0x800)
        if i + 1 >= a: track.append((i + 1, sc.tx(m), sc.th(m)))
        if i + 1 >= b0 and m[0x475] == 0: targets.setdefault(jkey(m), i + 1)
    e.load(bm); sa = e.msave(); m = e.ram(0, 0x800); hp0, lives0 = m[0x51A], m[0x11]
    print(f"rejoin {out}: old window {b0}..{b1}, {len(targets)} join states; start x {sc.tx(m)} h {sc.th(m)}", flush=True)
    def progress(x, h):
        best, dist = a, 10 ** 9
        for j, px, ph in track:
            dd = abs(sc.dx(x, px)) + abs(h - ph)
            if dd <= R and j > best: best = j
            if dd < dist: dist = dd
        return best, dist
    layer = [((a, 0), sa, [])]; found = None
    maxl = int(os.environ.get("SC_MAXLAYERS", (b1 - a) // MACRO + 1))
    for t in range(1, maxl + 1):
        cand = {}
        for score, sid, ins in layer:
            for act in ACTS:
                e.mload(sid); e.step(tuple(v for v in act.split("+") if v), MACRO); m = e.ram(0, 0x800)
                if m[0x51A] < hp0 or m[0x11] != lives0: continue
                k = sc.k5(m); key = k + (m[0x3B5],)
                if key in cand: continue
                p, dist = progress(k[0], k[1])
                cand[key] = ((p, -dist), sid, act, ins + [act] * MACRO, jkey(m))
        if not cand: print("  layer", t, "dead", flush=True); break
        nodes = sorted(cand.values(), key=lambda n: n[0], reverse=True)
        joins = [(n[4] in targets and targets[n[4]], n) for n in nodes if n[4] in targets]
        if os.environ.get("RJ_GOAL"):                           # "x,h,oldframe": standing within 1 px of (x,h) counts as joining at oldframe
            gx, gh, gj = (int(v) for v in os.environ["RJ_GOAL"].split(","))
            joins += [(gj, n) for n in nodes if abs(n[4][0] - gx) <= 1 and n[4][1] % 256 == gh and n[4][2] == 0 and n[4][4] == 0]
        if joins:
            j, n = min(joins, key=lambda q: q[0] - 0)       # earliest old frame joined (the rest of the old inputs is longest)
            cost = t * MACRO - (j - a)
            if found is None or cost < found[0]:
                found = (cost, j, n[3]); print(f"  layer {t}: joins the old run at {j} after {t * MACRO} frames (old {j - a}; cost {cost})", flush=True)
        if found and found[0] <= 0: break
        if found and t * MACRO > (found[1] - a) + 60: break
        keep = nodes[:WIDTH]; new = []
        for scr, psid, act, ins, k in keep:
            e.mload(psid); e.step(tuple(v for v in act.split("+") if v), MACRO); new.append((scr, e.msave(), ins))
        for n in layer:
            if n[1] != sa: e.mfree(n[1])
        layer = new
        if t % 20 == 0: print(f"  layer {t}: {len(cand)} states, best progress {keep[0][0][0]}, joins so far {found}", flush=True)
    if found:
        e.mload(sa)
        for b_ in found[2]: e.step(tuple(v for v in b_.split("+") if v), 1)
        e.save(f"RJ_{out}"); json.dump({"bookmark": bm, "inputs": found[2], "join": found[1], "cost": found[0]}, open(f"knowledge/rejoin_{out}.json", "w"))
        print(f"saved knowledge/rejoin_{out}.json: {len(found[2])} frames, joins old {found[1]} (cost {found[0]})", flush=True)
    else: print("no join found", flush=True)
    e.close(); return found
if __name__ == "__main__": main(*sys.argv[1:])
