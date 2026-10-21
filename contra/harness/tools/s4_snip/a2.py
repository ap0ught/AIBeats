import importlib, sys, json
sys.path.insert(0, "tools")
import s4_lab as L; importlib.reload(L)
e.set_fields(L.fields())
rep = json.load(open("logs/s4/p0_report.json"))
rows = [tuple(r) for r in json.load(open("logs/s4/p0_rows.json"))]
b0 = rep["boss_load"]
s0 = e.load("s4/boss")
tr = L.trace(e, rows[b0:b0 + 240])
prev = s0
for i, s in enumerate(tr):
    ev = L.events(prev, s)
    nb = [b for b in bc.bullets(s) if not any(pb[0] == b[0] for pb in bc.bullets(prev))]
    if ev or nb:
        print(f"i={i+1:4d} fc={s['frame_fc']:3d} x={s['x']:3d} y={s['y']:3d} j={s['jump']:02x} aim={s['aim']} in={'+'.join(rows[b0+i])} " + "; ".join(ev) + (f" NEW{[(b[0], b[4], b[5]) for b in nb]}" if nb else ""))
    prev = s
print("last:", bc.fmt_enemies(tr[-1]))
e.save("s4/x_p0_240")
