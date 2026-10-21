"""Wide-platform Hornhead (0x5c) from a bookmark: hit 1 (lead-in x wait scan), then the big boot (walk away n / toward n, then
toward+B). Keeps the earliest kill with the toad unhurt; then idles until the toad stands. -> knowledge/wpkill_<out>.json, bookmark WPK_<out>
    python wpkill.py <bookmark> <out>"""
import json, sys
from toads.emulator import BizHawk
BM, OUT = sys.argv[1], sys.argv[2]
e=BizHawk(log_name=f"wpkill_{OUT}.log"); e.load(BM)
def rd():
    m=e.ram(0,0x800)
    foe=[(m[0x3FD+q]|m[0x3EE+q]<<8, m[0x439+q]|m[0x42A+q]<<8, m[0x51A+q], m[0x4B1+q]) for q in range(2,15) if m[0x3C1+q]==0x5c]
    return dict(x=m[0x3FD]|m[0x3EE]<<8, H=m[0x439]|m[0x42A]<<8, z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], spd=m[0x565], foe=foe)
def tow(s):
    if not s["foe"]: return "Right"
    d=(s["foe"][0][0]-s["x"]+256)%512-256; return "Right" if d>=0 else "Left"
def away(t): return "Left" if t=="Right" else "Right"
ins=[]; n=0
while not rd()["foe"] and n<300: e.step((),1); ins.append(""); n+=1
s=rd(); print("Hornhead at", n, s, flush=True); root=e.msave(); hp0=s["foe"][0][2]
LEADS=[[], ["T"], ["T"]*4, ["T"]*8, ["T","","T"], ["J"]*4, ["T+J"]*4, ["T+J"]*8, ["W"], ["T"]*12, ["T"]*16]
hits=[]
for w in range(0, 80, 2):
    for li, lead in enumerate(LEADS):
        e.mload(root); seq=[""]*w
        for i in range(w): e.step((),1)
        t=tow(rd())
        for tok in lead:
            b="+".join({"T":t,"W":away(t),"J":"A"}[p] for p in tok.split("+") if p) if tok else ""
            e.step(tuple(v for v in b.split("+") if v),1); seq.append(b)
        e.step(("B",),1); seq.append("B"); got=None
        for i in range(30):
            s=rd()
            if s["hp"]<47 or s["lives"]<4: break
            if s["foe"] and s["foe"][0][2]<hp0: got=i; break
            e.step((),1); seq.append("")
        if got is not None and s["hp"]>=47:
            hits.append((len(seq), seq, e.msave()))
    if len(hits) >= 6: break
hits.sort(key=lambda h:h[0]); print("hit 1 options:", [h[0] for h in hits[:6]], flush=True)
best=None; dmg_seen=set()
for hlen, hseq, hsid in hits[:4]:
    for mode in ("toward", "sprint", "away", "awaysprint"):
        for nwalk in range(0, 48, 3):
            for wt in (0, 8, 16):
                e.mload(hsid); seq=list(hseq)
                for i in range(wt): e.step((),1); seq.append("")
                s=rd()
                if not s["foe"]: continue
                t=tow(s); d=t if mode in ("toward","sprint") else away(t)
                if "sprint" in mode:
                    for b in ((d,),(),(d,)): e.step(b,1); seq.append("+".join(b))
                for i in range(nwalk): e.step((d,),1); seq.append(d)
                t=tow(rd()); hpb=rd()["foe"][0][2] if rd()["foe"] else 0
                e.step((t,"B"),1); seq.append(t+"+B")
                for i in range(12): e.step((t,),1); seq.append(t)
                kill=None
                for i in range(60):
                    s=rd()
                    if s["hp"]<47 or s["lives"]<4: break
                    if s["foe"] and s["foe"][0][2]<hpb: dmg_seen.add(hpb-s["foe"][0][2])
                    if s["foe"] and s["foe"][0][2]==0: kill=len(seq); break
                    if not s["foe"]: break
                    e.step((),1); seq.append("")
                if kill and (best is None or kill<best[0]): best=(kill, list(seq)); print("KILL at +", kill, mode, nwalk, wt, "hit1 len", hlen, flush=True)
    print("after hit option", hlen, "damage values seen", sorted(dmg_seen), flush=True)
if best:
    e.load(BM)
    for b in ins+best[1]: e.step(tuple(v for v in b.split("+") if v),1)
    full=ins+best[1]
    while True:
        s=rd()
        if not s["foe"] and s["z"]==0: break
        e.step((),1); full.append("")
        if len(full) > len(ins)+best[0]+200: break
    e.save(f"WPK_{OUT}"); s=rd()
    print("RESULT kill +", len(ins)+best[0], "standing +", len(full), s, flush=True)
    json.dump({"bookmark": BM, "inputs": full, "kill": len(ins)+best[0]}, open(f"knowledge/wpkill_{OUT}.json","w"))
e.close()
