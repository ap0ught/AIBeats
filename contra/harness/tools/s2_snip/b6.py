# timeline of the stage 4 boss attempt held in S4 (rows after the boss-room snapshot)
S = G["S4"]
rows = list(S.rows)
n0 = len(G["s4_snap_after"][1])
S.restore(G["s4_snap_after"])
last = None
out = []
for k, r in enumerate(rows[n0:]):
    s = S.step(r)
    hel = [(i, s[f"ex{i}"], s[f"ey{i}"], s[f"e4{i}"], s[f"es{i}"] >> 7, s[f"ed{i}"], s[f"er{i}"]) for i in range(16) if s[f"er{i}"] and s[f"et{i}"] == 0x1C]
    cur = (s["plates"], tuple((h[3], h[4], h[6]) for h in hel))
    if cur != last:
        out.append(f"{k + 1}: x{s['x']} y{s['y']} plates{s['plates']} helmets(slot,x,y,hp,invuln,delay,rt)={hel}")
        last = cur
print("\n".join(out[:60]))
