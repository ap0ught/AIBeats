import importlib, sys
sys.path.insert(0, "tools")
import s4_lab as L; importlib.reload(L)
e.set_fields(L.fields())
s0 = e.load("s4/boss")
print("start", {k: s0[k] for k in ("frame", "frame_fc", "rng", "screen", "loc", "x", "y", "jump", "weapon", "lives", "aim")})
print(bc.fmt_enemies(s0))
tr = L.trace(e, [()] * 420)
prev = s0
for i, s in enumerate(tr):
    ev = L.events(prev, s)
    if ev or i < 3 or (60 < i < 82):
        print(f"i={i+1:4d} fc={s['frame_fc']:3d} x={s['x']:3d} y={s['y']:3d} j={s['jump']:02x} aim={s['aim']} " + "; ".join(ev))
    prev = s
print("last:", bc.fmt_enemies(tr[-1]))
