"""Mesen: play legal rows from a .mst; print Ryu + enemies (hitbox model) for rows a..b."""
import sys
sys.path.insert(0, '.')
from ng import fastcore as F
from ng.solve import common as C, hitbox as HB
mst, rf, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
k = int(sys.argv[5]) if len(sys.argv) > 5 else 1
rows = C.rows_of(rf)
with F.FastCore(boot_rows=None, ticks=False) as fc:
    fc.load_file(mst, 's')
    for i, r in enumerate(rows[:b]):
        fc.step([r])
        if i >= a and (i - a) % k == 0:
            m = fc.ram()
            ry = HB.ryu(m)
            en = HB.enemies(m)
            print(i, "+".join(r) or "-", f"R x{ry['x']} y{ry['y']} h{ry['h']} L{int(ry['left'])} air{int(ry['air'])} act{ry['action']} pose{ry['pose']} up{ry['up']} dn{ry['down']} hp{ry['hp']} np{ry['ninpo']}",
                  " | ".join(f"s{e['slot']} t{e['type']:02x} p{e['pose']} x{e['x']} y{e['y']} xr{e['xr']} yr{e['yr']} hp{e['hp']}{' SW' if HB.sword_hits(m,e) else ''}{' HURT' if HB.hurts(m,e) else ''}" for e in en if e['type'] in (0x19,)), "bossreal", m[0x497])
