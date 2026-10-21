S = G["S4"]
S.restore(G["s4_snap_room1"])
i = 14
last = None; T = 0; out = []
while T < 230:
    row = []
    if 33 <= T < 49: row.append("Right")
    if T >= 28 and (S.pad.len["B"] == 1 or (S.pad.len["B"] == 0 and S.pad.can_press("B"))): row.append("B")
    s = S.step(S.pad.fix(tuple(row))); T += 1
    cur = (s[f"er{i}"], s[f"eh{i}"], s[f"es{i}"], s[f"ec{i}"] & 15)
    if cur != last: out.append(f"T{T}:r{cur[0]} hp{cur[1]} s{cur[2]:02x} c{cur[3]} nb{len(bc.bullets(s))}")
    last = cur
    if s["death"] & 1: out.append(f"DEATH T{T}"); break
print(" ".join(out))
