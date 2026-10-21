def rows(n, spec):
    r = [set() for _ in range(n)]
    for a, b, btn in spec:
        for i in range(a, b + 1):
            if i < n: r[i] |= set(btn.split("+"))
    return [tuple(x) for x in r]
presses=[238,248,265,270,275,280,292,297]
base=[(1,8,"Right")]+[(p,p+1,"B") for p in presses]
# crouch except around presses
down=[]
last=60
for p in presses:
    down.append((last,p-1,"Down")); last=p+2
base+=down
e.mload(G["s2_0"]); e.trace(True)
e.run(rows(330, base)); tr=e.last_trace
prev=tr[0]
for i,s in enumerate(tr):
    ev=[]
    for k in ("eh14","cores","cleared","death","elec","er14","x"):
        if s[k]!=prev[k]: ev.append(f"{k} {prev[k]}->{s[k]}")
    if ev and i>200: print(i, "; ".join(ev))
    prev=s
G["r1_killed"]=e.msave()   # i=330 state
def tail(name, spec, n=260):
    e.mload(G["r1_killed"]); e.run(rows(n, spec)); tr=e.last_trace
    prev=tr[0]; out=[]
    for i,s in enumerate(tr):
        ev=[]
        for k in ("cores","cleared","death","elec","adv","iscroll","scroll","screen","jflag","pseq","jump","loc","trans"):
            if s[k]!=prev[k]: ev.append(f"{k} {prev[k]}->{s[k]}")
        if s["lagged"]: ev.append("LAG")
        if ev: out.append(f"  {330+i} x={s['x']} y={s['y']} " + "; ".join(ev))
        prev=s
    print("==",name); print("\n".join(out))
    return tr
tr=tail("no input", [])
c1=next(i for i,s in enumerate(tr) if s["cleared"]==1)
print("cleared=1 at", 330+c1)
tail("Up held from frame after $80", [(c1+2, 400, "Up")])
