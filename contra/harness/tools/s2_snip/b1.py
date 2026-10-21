import json
S = G["S"]; S.e.set_fields(bc.make_fields())
snapB = G["snap_after"]
G["rows_to_boss"] = list(S.rows)
json.dump(S.rows, open("logs/s2/v0_rows_to_boss.json", "w"))
S.restore(snapB)
S.e.save("s2/v0_boss")
prev = S.s
print({k: S.s[k] for k in ("frame","screen","x","y","cores","loc","jump","aim","pseq")})
print(bc.fmt_enemies(S.s))
for T in range(1, 420):
    s = S.step(())
    ev = []
    for k in ("cores","plates","loc","death","jump","bossdef","lroutine","pseq","aim","y"):
        if k=="y":
            continue
        if s[k] != prev[k]: ev.append(f"{k} {prev[k]}->{s[k]}")
    for i in range(16):
        if s[f"er{i}"] and not prev[f"er{i}"]: ev.append(f"+e{i} t{s[f'et{i}']:02x} hp{s[f'eh{i}']} ({s[f'ex{i}']},{s[f'ey{i}']}) s{s[f'es{i}']:02x}")
        elif s[f"er{i}"] and (s[f"eh{i}"] != prev[f"eh{i}"] or (s[f"es{i}"] ^ prev[f"es{i}"]) & 0x81 or s[f"er{i}"] != prev[f"er{i}"]):
            ev.append(f"e{i}(t{s[f'et{i}']:02x}) r{s[f'er{i}']} hp{s[f'eh{i}']} s{s[f'es{i}']:02x} v1={s[f'e1{i}']}")
    if s["lagged"]: ev.append("LAG")
    if ev: print(T, f"x={s['x']} y={s['y']}", "; ".join(ev))
    prev = s
    if s["death"] & 1: break
