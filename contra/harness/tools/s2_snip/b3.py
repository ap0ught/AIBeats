S = G["S"]
rows = list(S.rows)
n0 = len(G["rows_to_boss"])
S.restore(G["snap_after"])
def plates(s):
    return [(i, s[f"ex{i}"], s[f"ey{i}"], s[f"eh{i}"]) for i in range(16) if s[f"er{i}"] and s[f"et{i}"] == 0x0A]
last = None
for k, r in enumerate(rows[n0:]):
    s = S.step(r)
    p = [x[3] for x in plates(s)]
    if p != last and k > 100:
        print(k, "x", s["x"], "y", s["y"], "plates", plates(s), "nplates", s["plates"], "bul", len(bc.bullets(s)))
        last = p
print(bc.fmt_enemies(s))
