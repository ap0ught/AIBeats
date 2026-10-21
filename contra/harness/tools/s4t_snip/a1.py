import importlib, sys
sys.path.insert(0, "tools")
import s4t_lab as L
importlib.reload(L)

# stage 4 room 1 from the real state: the drop
tr = L.trace(e, "s4/real_c1", [()] * 70)
print("real_c1", {k: tr[0][k] for k in ("frame", "frame_fc", "rng", "lroutine", "screen", "x", "y", "weapon", "lives")})
L.show(tr, 0, 60)
print(bc.fmt_enemies(tr[40]))
# fire at every T from 8..34 (one press each, separate runs): where does the pellet group arrive, does it hit
for T in range(8, 36, 1):
    rows = [()] * 70
    rows[T] = ("B",)
    rows[T + 1] = ("B",)
    t2 = L.trace(e, "s4/real_c1", rows)
    h = L.hits(t2)
    nb = [b for b in bc.bullets(t2[T + 2])]
    print("press row", T, "bullets", [(b[4], b[5], b[2]) for b in nb][:5], "hits", h[:3])
