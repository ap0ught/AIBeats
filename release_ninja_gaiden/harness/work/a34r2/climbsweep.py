"""Single-wall climb sweep (agent a34 round 2).
    python work/a34r2/climbsweep.py <state name> <wall side: R|L> <Lmin> <Lmax> <frames> [out json]
From a state where Ryu clings to a wall (wall on his right: jump off with Left+A), every legal cyclic pattern of
length L (per frame: direction none/away/toward x A on/off; A one run of 2-3 frames per cycle, starting at frame 0)
is repeated for <frames> frames; reports the height gained (start y - min y over the last cycle) and the final y.
Legality = a34_core.Legal on the repeated rows (period 5, hold 2, release 2)."""
import sys, json, itertools, time
sys.path.insert(0, "ng/stages"); sys.path.insert(0, ".")
import a34_core as K
st, side, lmin, lmax, nf = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
out = sys.argv[6] if len(sys.argv) > 6 else None
PRE = [tuple(x.split("+")) if x else () for x in sys.argv[7].split(",")] if len(sys.argv) > 7 else []
AW, TO = ("Left", "Right") if side == "R" else ("Right", "Left")
pats = []
for L in range(lmin, lmax + 1):
    for dirs in itertools.product((None, AW, TO), repeat=L):
        for alen in (2, 3):
            rows = []
            for i, d in enumerate(dirs):
                r = []
                if d: r.append(d)
                if i < alen: r.append("A")
                rows.append(tuple(b for b in K.BTNS if b in r))
            if dirs[0] != AW:
                continue        # jump frame must hold the away direction
            seq = PRE + rows * (nf // L + 2)
            i, w = K.legal_list(seq)
            if i is None:
                pats.append(rows)
print(len(pats), "legal patterns", flush=True)
e = K.open_emu("a34r2_climb.log")
res = []
try:
    s0 = e.load(st)
    sid = e.msave()
    y0 = s0.y
    t = time.time()
    for k, p in enumerate(pats):
        e.mload(sid)
        seq = PRE + (p * (nf // len(p) + 2))[:nf]
        e.trace(True); e.run(seq); tr = e.last_trace; e.trace(False)
        ys = [x["y"] for x in tr]
        last = ys[-len(p):]
        res.append({"p": ["+".join(r) for r in p], "gain": y0 - min(last), "end_y": ys[-1], "end_x": tr[-1]["x"],
                    "rate": round((y0 - min(last)) / nf, 2), "coll": tr[-1]["coll"]})
        if k % 100 == 0:
            print(k, f"{time.time() - t:.0f}s", flush=True)
finally:
    e.close()
res.sort(key=lambda r: -r["gain"])
for r in res[:15]:
    print(r)
if out:
    json.dump(res, open(out, "w"))
