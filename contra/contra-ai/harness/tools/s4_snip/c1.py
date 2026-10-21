e.set_fields(bc.make_fields())
for st in ("s1/s2_start_legal", "ref_s2", "s4/dbg_L"):
    s = e.load(st)
    print(st, {k: s[k] for k in ("frame", "frame_fc", "rng", "level", "lroutine", "weapon", "lives", "x", "y")})
