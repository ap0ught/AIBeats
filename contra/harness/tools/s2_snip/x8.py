S = bc.Sess(e)
e.mload(G["s2_0"]); S.s = e.state(); S.rows=[]; S.pad=bc.Pad()
presses=[238,248,265,270,275,280,292,297]
for i in range(1, 262):
    row=set()
    if 34<=i<50: row.add("Right")
    if any(p<=i<=p+1 for p in presses): row.add("B")
    elif i>=60 and not any(p-1<=i<=p+2 for p in presses): row.add("Down")
    row = S.pad.fix(tuple(row))
    s=S.step(row)
    if i>=235 and (i<242 or i>255): print(i, row, f"pad={s['pad']:02x} new={s['padnew']:02x} pseq={s['pseq']} hp={s['eh14']} st={s['es14']:02x}", bc.fmt_bullets(s))
