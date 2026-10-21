def rows(n, spec):
    r = [set() for _ in range(n)]
    for a, b, btn in spec:
        for i in range(a, b + 1):
            if i < n: r[i] |= set(btn.split("+"))
    return [tuple(x) for x in r]
e.mload(G["s2_0"])
e.trace(True)
e.run(rows(420, [(33,48,"Right"), (100,420,"Down")]))
tr = e.last_trace
for i, s in enumerate(tr):
    if i < 126: continue
    en = [x for x in bc.enemies(s) if x[2] not in (0x14, 0x19)]
    print(f"i={i} fc={s['frame_fc']} x={s['x']} y={s['y']} d={s['death']} " + " ".join(f"[{k}:t{t:02x} r{r} ({x},{y}) s{st:02x} d{d} a{a:02x}]" for k, r, t, hp, x, y, st, d, a, v1, v4 in en))
