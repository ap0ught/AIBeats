# core hit timing, crouch shots, slot free after hit
def rows(n, spec):
    r = [set() for _ in range(n)]
    for a, b, btn in spec:
        for i in range(a, b + 1):
            if i < n: r[i] |= set(btn.split("+"))
    return [tuple(x) for x in r]
e.load("ref_s2")
G["s2_0"] = e.msave()
e.trace(True)
for name, spec in [
    ("stand fire 237", [(1,16,"Right"), (237,238,"B")]),
    ("stand fire 238", [(1,16,"Right"), (238,239,"B")]),
    ("crouch fire 238", [(1,16,"Right"), (100,300,"Down"), (238,239,"B")]),
    ("stand 238,243,248..", [(1,16,"Right"), (238,239,"B"), (243,244,"B"), (265,266,"B"), (270,271,"B")]),
]:
    e.mload(G["s2_0"])
    r = rows(300, spec)
    e.run(r)
    tr = e.last_trace
    print("==", name, "x", tr[60]["x"])
    prev = None
    for i, s in enumerate(tr):
        if i < 236: prev = s; continue
        ev = []
        if prev and s["eh14"] != prev["eh14"]: ev.append(f"core hp {prev['eh14']}->{s['eh14']}")
        if prev and s["es14"] != prev["es14"]: ev.append(f"core st {prev['es14']:02x}->{s['es14']:02x}")
        if prev and s["death"] != prev["death"]: ev.append("DEATH")
        b = bc.fmt_bullets(s)
        if ev or (b and i < 300):
            print(f" i={i} x={s['x']} pseq={s['pseq']} {'; '.join(ev)} | {b}")
        prev = s
