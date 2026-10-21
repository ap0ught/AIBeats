"""L12h stage 4: the walker (0x62, 79 hp = five 16-point blows) fought at the LEFT end of its platform so that the kill ends where the
lower spring (0x36, H 4800) leaves the platform on its first lap. Hit-by-hit beam (after fightbeam.py): at every wait frame try lead-ins + B;
while waiting the toad drifts toward x = XT (sprint Left when far). Select variants re-roll the walker's dice.
    python l12h_walker.py <piece> <out tag> [XT=24] [WIDTH=4] [OPEN=20]
-> logs/fix/L12h_w<tag>.json (best kills), pieces w<tag>_0.. / bookmarks L12h_w<tag>_0.. (state at the kill landing)"""
import json, os, sys
from l12h_lib import *
pn, tag = sys.argv[1], sys.argv[2]
XT = int(sys.argv[3]) if len(sys.argv) > 3 else 24
WIDTH = int(sys.argv[4]) if len(sys.argv) > 4 else 4
OPEN = int(sys.argv[5]) if len(sys.argv) > 5 else 20
WAIT = int(os.environ.get("W_WAIT", 70)); SEL = os.environ.get("W_SEL", "1") == "1"
LEADS = ["", "T", "T|T", "T|T|T|T", "T||T", "T||T|T|T", "T||T|T|T|T|T|T|T", "W|T", "J|J|J|J", "J|J|J|J|J|J|J|J", "T+J|T+J|T+J|T+J",
         "T+J|T+J|T+J|T+J|T+J|T+J|T+J|T+J", "T||T+J|T+J|T+J|T+J|T+J|T+J", "J|J|J|J|J|J|J|J|J|J|J|J", "T+J|T+J", "J|J"]
def foe(s): return [(d[1], d[2], d[3]) for d in s["objs"] if d[0] == 0x62]
def hpw(s): return sum(d[2] for d in foe(s))
def toward(s):
    f = foe(s)
    if not f: return "Left"
    return "Right" if dx(f[0][0], s["x"]) >= 0 else "Left"
def expand(lead, t):
    w = "Left" if t == "Right" else "Right"; out = []
    for tok in (lead.split("|") if lead else []):
        out.append("+".join({"T": t, "W": w, "J": "A"}[q] for q in tok.split("+") if q))
    return out + ["B"]
p = load_piece(pn); k0 = p["base_k"] + len(p["inputs"])
e = BizHawk(log_name=f"fix_l12h_walker_{tag}.log"); e.load(p["base"]); run(e, p["inputs"])
class Line:
    def __init__(self): self.k = k0; self.seq = []
    def st(self, b):
        e.step(bt(b), 1); self.k += 1; self.seq.append(b); return rd(e)
L = Line()
# opening: hop Left to pull the camera to 1226 (the walker spawns), keep going Left
for i in range(OPEN): s = L.st("Left+A")
while not foe(s) and L.k < k0 + 60: s = L.st("Left")
print("walker spawned at", L.k, foe(s), "toad", s["x"], s["H"], flush=True)
spawn_k = L.k
def drift(s, phase):
    """what to press while waiting: sprint Left toward XT (tap, gap, hold), stand when there. phase = frames since the wait began."""
    d = dx(s["x"], XT)
    if s["z"] != 0: return "Left" if d > 6 else ""
    if d > 10: return "" if phase == 1 else "Left"
    return ""
def safe(s): return alive(s) and s["H"] >= 4700
beam = [(L.k, e.msave(), list(L.seq), 79)]
done = []; hitno = 0
while beam and not done:
    nxt = []
    for f, sid, seq, left in beam:
        for sel in ((False, True) if SEL else (False,)):
            e.mload(sid); L.k = f; L.seq = list(seq); found = set()
            for w in range(WAIT):
                s = rd(e)
                if not safe(s): break
                cur = hpw(s)
                if cur < left: left = cur
                if cur == 0 and foe(s) == [] and left == 0: break
                here = e.msave(); nk = L.k; nh = len(L.seq)
                t = toward(s)
                for lead in LEADS:
                    if lead in found: continue
                    e.mload(here); L.k = nk; del L.seq[nh:]
                    for x in expand(lead, t): s2 = L.st(x)
                    got = None
                    for _ in range(26):
                        if not safe(s2): break
                        c2 = hpw(s2)
                        if c2 < cur: got = c2; break
                        s2 = L.st("")
                    if got is None: continue
                    for _ in range(70):
                        if (s2["z"] == 0 and s2["an"] not in (35, 38, 39, 49)) or not safe(s2): break
                        s2 = L.st("Left" if dx(s2["x"], XT) > 6 and s2["z"] != 0 else "")
                    if s2["z"] != 0 or not safe(s2): continue
                    got = min(got, hpw(s2)); found.add(lead)
                    nxt.append((L.k, e.msave(), list(L.seq), got, lead, w, s2["x"], sel))
                e.mload(here); e.mfree(here); L.k = nk; del L.seq[nh:]
                b = drift(s, w)
                if sel and w == 0: b = (b + "+Select").strip("+")
                L.st(b)
    for n in beam: e.mfree(n[1])
    if not nxt: print("no next hit from any beam state", flush=True); break
    hitno += 1
    nxt.sort(key=lambda n: (n[3], n[0] + max(0, dx(n[6], XT) - 20) / 3))
    keep = []; seenx = set()
    for n in nxt:
        key = (n[6] // 6, n[3], n[0] // 2)
        if key in seenx or len(keep) >= WIDTH: e.mfree(n[1]); continue
        seenx.add(key); keep.append(n)
    print(f"hit {hitno} ->", [(n[0], n[3], n[4], n[5], n[6], "S" if n[7] else "") for n in keep], flush=True)
    done = [n for n in keep if n[3] == 0]
    beam = [n[:4] for n in keep]
res = []
for i, n in enumerate(sorted(done, key=lambda n: n[0])[:3]):
    e.mload(n[1]); s = rd(e)
    print("KILL", i, "landed at", n[0], "(spawn +%d)" % (n[0] - spawn_k), "toad", s["x"], s["H"], "spring", ob(s, 0x36, 4800, 40), flush=True)
    save_piece(f"w{tag}_{i}", p["base"], p["base_k"], p["inputs"] + n[2], kill_landed=n[0], spawn=spawn_k)
    e.save(f"L12h_w{tag}_{i}")
    res.append(dict(landed=n[0], x=s["x"], spring=ob(s, 0x36, 4800, 40)))
json.dump(res, open(FIX / f"L12h_w{tag}.json", "w"))
e.close()
