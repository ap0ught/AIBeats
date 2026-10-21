"""L12h: from a piece (cut at frame cutk) replay the TAS's inputs f0..f1 (banned Left+Right replaced) and report events + deviation.
    python l12h_tasrun.py <piece> <cutk> <f0> <f1> [out piece] [air=Left] [ground=] [edits: f:+n (insert n idle before TAS frame f) / f:-n (skip n TAS frames from f)]"""
import sys
from l12h_lib import *
def tasrun(e, k, f0, f1, air="Left", ground="", edits=None, verbose=0, stop_dead=True):
    """returns (seq, events, k). Prints per-frame rows when verbose (every `verbose` frames)."""
    T = tas(); edits = edits or {}; seq = []; ev = []; prev = rd(e); f = f0; dev = None
    def one(b, f):
        nonlocal k, prev, dev
        e.step(bt(b), 1); k += 1; seq.append(b); s = rd(e)
        t = T.get(f)
        if prev["z"] != 0 and s["z"] == 0: ev.append((k, f, f"land x={s['x']} H={s['H']}" + (f" (TAS x={t['x']} h={t['h']} z={t['z']})" if t else "")))
        for oid in (0x5c, 0x62):
            a = {d[4]: d[3] for d in prev["objs"] if d[0] == oid}; b2 = {d[4]: d[3] for d in s["objs"] if d[0] == oid}
            for q in b2:
                if q in a and b2[q] < a[q]: ev.append((k, f, f"HIT {oid:02x} {a[q]}->{b2[q]} toad=({s['x']},{s['H']})"))
                if q not in a: ev.append((k, f, f"SPAWN {oid:02x} {[d[1:4] for d in s['objs'] if d[4] == q]} cam={s['cam']}"))
            for q in a:
                if q not in b2: ev.append((k, f, f"GONE {oid:02x}"))
        if prev["faces"] != s["faces"]: ev.append((k, f, f"faces {prev['faces']}->{s['faces']} cam={s['cam']}"))
        if (prev["an"] in (94, 95, 96)) != (s["an"] in (94, 95, 96)): ev.append((k, f, f"pole {'grab' if s['an'] in (94, 95, 96) else 'leave'} x={s['x']} H={s['H']}"))
        if t and dev is None and (abs(dx(s["x"], t["x"])) > 8 or abs(s["h"] - t["h"]) > 8 and abs(s["h"] - t["h"]) < 248): dev = (k, f, (s["x"], s["h"], s["z"]), (t["x"], t["h"], t["z"]))
        if verbose and k % verbose == 0:
            print(k, f"{b or '-':9s} x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} cam={s['cam']} |", " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in s["objs"] if d[0] in (0x36, 0x34, 0x5c, 0x62, 0x60)),
                  (f"|| TAS {f} {t['p']:6s} x={t['x']} h={t['h']} z={t['z']} an={t['an']} cam={t['camy']} " + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in t["objs"] if d[0] in (0x36, 0x34, 0x5c, 0x62, 0x60))) if t else "", flush=True)
        prev = s
        return s
    while f < f1:
        n = edits.get(f, 0)
        if n > 0:
            for i in range(n):
                s = one("", None)
        if n < 0: f += -n; edits.pop(f + n, None); continue
        s = one(tbtn(f, air, ground), f); f += 1
        if stop_dead and not alive(s): ev.append((k, f, "DEAD/HURT")); break
    return seq, ev, k, dev
if __name__ == "__main__":
    pn, cutk, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    out = None; air = "Left"; ground = ""; edits = {}; verbose = 0
    for a in sys.argv[5:]:
        if a.startswith("air="): air = a[4:]
        elif a.startswith("ground="): ground = a[7:]
        elif a.startswith("v="): verbose = int(a[2:])
        elif ":" in a: f, n = a.split(":"); edits[int(f)] = int(n)
        else: out = a
    p = load_piece(pn); ins = p["inputs"][:cutk - p["base_k"]]
    e = BizHawk(log_name="fix_l12h_tasrun.log"); e.load(p["base"]); run(e, ins)
    s = rd(e); print("start", cutk, "x", s["x"], "H", s["H"], "z", s["z"], "| TAS", f0 - 1, {k: v for k, v in tas()[f0 - 1].items() if k != "objs"}, flush=True)
    seq, ev, k, dev = tasrun(e, cutk, f0, f1, air, ground, edits, verbose)
    for x in ev: print(x)
    print("first deviation > 8 px:", dev, "| end", k, {a: b for a, b in rd(e).items() if a not in ("objs",)})
    if out:
        save_piece(out, p["base"], p["base_k"], ins + seq); e.save("L12h_" + out); print("saved piece", out, "ending at", k)
    e.close()
