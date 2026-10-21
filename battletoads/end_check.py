"""Check end_model.simulate against every captured ending (logs/fix/endcap_*.bin from end_var.py): feed it the timer, angle
and step at the last hit plus the random reloads the game actually rolled; the predicted hit -> T. Bird cut must match."""
import glob
import json
import os
import sys

import end_model as M
from end_an import load, FIX

s8 = M.s8
ok = n = 0
rows_out = []
tags = sys.argv[1:] or [os.path.basename(p)[7:-5] for p in sorted(glob.glob(str(FIX / "endcap_*.json")))]
for tag in tags:
    idx, rows = load(tag)
    if not idx.get("cut2") or "hit21" not in idx or not idx.get("hit21"):
        continue
    f0 = idx["first_frame"]
    R = lambda f: rows[f - f0]
    s = idx["slot"]
    hit, resp, cut1, back, cut2 = (idx[k] for k in ("hit21", "resp", "cut1", "back", "cut2"))
    g = lambda f, t: R(f)[t + s]
    h = lambda f: s8(g(f, 0x42A)) * 256 + g(f, 0x439)
    rh = M.read_hit(R(hit))
    h0 = h(resp)
    flight = resp - hit
    n1_rule = 171 if (R(hit)[0x0B] + flight) % 2 == 0 else 172
    n1 = cut1 - resp - 207 - 122
    draws = []
    frozen = 0
    for f in range(resp + 200, cut2 + 1):
        if R(f)[0x10] != 13 or g(f, 0x3C1) != 0x7E:
            continue
        if h(f) != h(f - 1):
            if g(f, 0x4ED) != (g(f - 1, 0x4ED) - 1) % 256 and 0 <= h(f) <= 127:
                draws.append((g(f, 0x4ED), s8(g(f, 0x4DE))))
    r = M.simulate(rh["a"], rh["theta"], rh["d"], h0, n1, draws=draws)
    pred = None if r["open"] else M.tail_frames(flight, n1, r["wait"], back - cut1)
    n += 1
    good = pred == cut2 - hit
    ok += good
    fl = M.flight_of(idx.get("qh", 0))
    rows_out.append((tag, rh["a"], rh["theta"], rh["d"], idx.get("qh"), h0, flight, fl[0], n1_rule, n1, draws, r.get("K"),
                     r.get("wait"), back - cut1, pred, cut2 - hit, good, idx.get("tx")))
    print(f"{tag:10s} a={rh['a']:3d} th={rh['theta']:3d} d={rh['d']:2d} qh={idx.get('qh')} h0={h0} flight={flight} (table {fl[0]}) "
          f"n1 rule {n1_rule} actual {n1} draws={draws} K={r.get('K')} wait={r.get('wait')} skip={back - cut1} "
          f"tail model {pred} actual {cut2 - hit} {'OK' if good else 'MISMATCH'} toad_x={idx.get('tx')}")
print(ok, "/", n, "match")
