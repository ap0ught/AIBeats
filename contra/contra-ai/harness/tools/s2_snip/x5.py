def rows(n, spec):
    r = [set() for _ in range(n)]
    for a, b, btn in spec:
        for i in range(a, b + 1):
            if i < n: r[i] |= set(btn.split("+"))
    return [tuple(x) for x in r]
presses=[238,248,265,270,275,280,292,297]
base=[(1,8,"Right")]+[(p,p+1,"B") for p in presses]
down=[]; last=60
for p in presses:
    down.append((last,p-1,"Down")); last=p+2
base+=down
e.mload(G["s2_0"]); e.trace(True)
R=rows(330, base)
e.run(R); tr=e.last_trace
for i in range(262,310):
    s=tr[i]
    en=[x for x in bc.enemies(s) if x[2] not in (0x19,)]
    print(i, "+".join(R[i]), f"x={s['x']} pseq={s['pseq']} pad={s['pad']:02x} hp={s['eh14']} d={s['death']}", bc.fmt_bullets(s), "|", " ".join(f"{t:02x}@{x},{y}" for k,r,t,hp,x,y,st,d,a,v1,v4 in en))
