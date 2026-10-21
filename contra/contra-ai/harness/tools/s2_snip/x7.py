# kill room-1 core from px=128 (no-split plan), then test the walk-in timing variants
S = bc.Sess(e)
e.mload(G["s2_0"]); S.s = e.state(); S.rows=[]; S.pad=bc.Pad()
presses=[p+1 for p in [238,248,265,270,275,280,292,297]]
log=[]
for i in range(1, 330):
    row=set()
    if 34<=i<50: row.add("Right")
    if any(p<=i<=p+1 for p in presses): row.add("B")
    elif i>=60 and not any(p-1<=i<=p+2 for p in presses): row.add("Down")
    row = S.pad.fix(tuple(row))
    prev=S.s; s=S.step(row)
    if s["eh14"]!=prev["eh14"] or s["death"]!=prev["death"]: log.append((i, s["eh14"], s["death"], s["x"]))
print(log)
snap=S.snapshot()
G["x7snap"]=snap[0]
def tail(name, fn, n=230):
    S.restore(snap); out=[]; prev=S.s
    for j in range(n):
        i=330+j
        s=S.step(S.pad.fix(fn(i, S.s)))
        ev=[f"{k} {prev[k]}->{s[k]}" for k in ("cores","cleared","death","adv","iscroll","scroll","screen","jflag","jump","loc") if s[k]!=prev[k]]
        if s["elec"] and not prev["elec"]: ev.append("ELEC")
        if s["lagged"]: ev.append("LAG")
        if ev: out.append(f"{i} x={s['x']} y={s['y']}: " + "; ".join(ev))
        prev=s
    print("==",name); print(" | ".join(out))
tail("down only", lambda i,s: ("Down",))
tail("Up when cleared==0x80 seen (frame after)", lambda i,s: ("Up",) if s["cleared"]==0x80 else ("Down",) if s["cleared"]==0 else ())
tail("Up when cleared==1 seen", lambda i,s: ("Up",) if s["cleared"] else ("Down",))
for k in (340,360,370,372,373,374,375,376):
    tail(f"Up from {k}", lambda i,s,k=k: ("Up",) if i>=k else ("Down",))
