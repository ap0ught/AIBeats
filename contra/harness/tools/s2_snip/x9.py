F = bc.make_fields(extra={"ef14": 0x568+14})
def run(name, px_frames, presses, crouch):
    S = bc.Sess(e, fields=F)
    e.mload(G["s2_0"]); S.s = e.state(); S.rows=[]; S.pad=bc.Pad()
    out=[]
    for i in range(1, 262):
        row=set()
        if 34<=i<34+px_frames: row.add("Right")
        if any(p<=i<=p+1 for p in presses): row.add("B")
        elif crouch and i>=60 and not any(p-1<=i<=p+2 for p in presses): row.add("Down")
        s=S.step(S.pad.fix(tuple(row)))
        if i>=239: out.append(f"{i}:r{s['er14']}d{s['ed14']}f{s['ef14']}g{s['gbuf']}{'L' if s['lagged'] else ''}")
    print("==", name, "open@", next((o for o in out if 'r4' in o), None)); print(" ".join(out))
run("idle x128", 16, [], False)
run("crouch x128", 16, [], True)
run("crouch x128 press 238", 16, [238], True)
run("crouch x128 press 238,248", 16, [238,248], True)
run("stand x128 press 238,248", 16, [238,248], False)
run("crouch x128 press 228,248", 16, [228,248], True)
