"""L12h stage 5: from the walker's death on the lower spring (piece w): pump at once, dash launch, face 3 spawns as the camera reaches 1112,
steer to a pole (x 32 or 96, H 4888).   python l12h_s5.py [piece=w] [out=s5]
-> piece s5 / bookmark L12h_s5 (hanging on the pole), with face3 = spawn frame."""
import sys, json
from l12h_lib import *
pn = sys.argv[1] if len(sys.argv) > 1 else "w"; out = sys.argv[2] if len(sys.argv) > 2 else "s5"
p = load_piece(pn); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name=f"fix_l12h_{out}.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
s = rd(e); print("start", k0, s["x"], s["H"], s["z"], s["an"], "spring", ob(s, 0x36, 4800, 40), "cam", s["cam"], flush=True)
res = []
for w0 in range(0, 30):
    e.mload(root); run(e, [""] * w0)
    if rd(e)["z"] != 0: continue
    e2 = e.msave(); L = None
    for i in range(45):
        e.step(("A",), 1)
        if rd(e)["z"] == 8: L = k0 + w0 + i + 1; break
    e.mload(e2); e.mfree(e2)
    if L is None: continue
    for d in ("Right", "Left", ""):
        for dash in ((True, False) if d else (False,)):
            e.mload(root); seq = [""] * w0; k = k0 + w0; run(e, seq)
            while k < L - 3: e.step(("A",), 1); k += 1; seq.append("A")
            tail = [d + "+A", "A", d + "+A"] if dash else ["A", "A", (d + "+A").strip("+")]
            for b in tail: e.step(bt(b), 1); k += 1; seq.append(b)
            s = rd(e)
            if s["z"] != 8: continue
            la = e.msave(); kl = k; seql = list(seq)
            for hd in ([0] if not d else [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 70]):
                for rel in ("A", ""):                       # after hd frames: keep A (full height) or release everything
                    e.mload(la); k = kl; seq = list(seql); face = None; pole = None
                    for i in range(110):
                        b = (d + "+A").strip("+") if i < hd else rel
                        e.step(bt(b), 1); k += 1; seq.append(b); s = rd(e)
                        if not alive(s): break
                        if s["faces"] and face is None: face = k
                        if s["an"] in (94, 95, 96): pole = (k, s["x"], s["H"]); break
                        if s["z"] == 0: break
                    if pole and face:
                        res.append((face, pole[0], pole, dict(w0=w0, L=L, d=d, dash=dash, hd=hd, rel=rel), list(seq)))
            e.mfree(la)
    print("w0", w0, "launch", L, "results so far", len(res), flush=True)
res.sort(key=lambda r: (r[0], r[1]))
for r in res[:12]: print("face3", r[0], "pole", r[2], r[3])
if res:
    for i, r in enumerate([res[0]] + [x for x in res if x[2][1] != res[0][2][1]][:1]):       # the best, and the best on the other pole
        name = out if i == 0 else out + "b"
        save_piece(name, p["base"], p["base_k"], p["inputs"] + r[4], face3=r[0], pole=r[2][0], polex=r[2][1])
        e.load(p["base"]); run(e, p["inputs"] + r[4]); e.save("L12h_" + name); print("saved", name, "face3", r[0], "pole", r[2])
e.close()
