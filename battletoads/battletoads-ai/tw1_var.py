"""TOWER1: from a piece standing for old row r0, play old (A12r) inputs with given replacements up to row r1 and list
the events (hits, landings) against the old run's.   python tw1_var.py <piece> <r1> <repl 'row:Btn;row:Btn'> ..."""
import sys
from tw1_lib import *
src, r1 = sys.argv[1], int(sys.argv[2])
A = seg("A12r"); buf = open(FIX / "tw1_a.ram", "rb").read()
p = load_piece(src); r0 = p["rn"] - 1
e = BizHawk(log_name="tw1_var.log"); e.load(p["base"]); run(e, p["inputs"]); root = e.msave()
def events(states):
    out = []; prev = None
    for r, s in states:
        if prev is not None:
            if prev["z"] != 0 and s["z"] == 0: out.append(f"{r}:land({s['x']},{s['H']})")
            for d in s["objs"]:
                if d[0] in (0x5c, 0x62):
                    for d0 in prev["objs"]:
                        if d0[0] == d[0] and d0[4] == d[4] and d[3] < d0[3]: out.append(f"{r}:HIT{d0[3]}->{d[3]}@toad({s['x']},{s['H']})en({d[1]},{d[2]})")
            if any(d[0] in (0x5c, 0x62) for d in prev["objs"]) and not any(d[0] in (0x5c, 0x62) for d in s["objs"]): out.append(f"{r}:GONE")
            if s["hp"] < prev["hp"]: out.append(f"{r}:HURT{s['hp']}")
        prev = s
    return " ".join(out)
print("old :", events([(r, rdm(buf[(r + 1) * 2048:(r + 2) * 2048])) for r in range(r0, r1 + 1)]))
for spec in sys.argv[3:] or [""]:
    repl = {}
    for t in spec.split(";"):
        if t: a, b = t.split(":"); repl[int(a)] = b
    e.mload(root); st = [(r0, rd(e))]
    for r in range(r0 + 1, r1 + 1):
        e.step(bt(repl.get(r, A[r])), 1); st.append((r, rd(e)))
    print(f"{spec or 'plain'} :", events(st), "| end", st[-1][1]["x"], st[-1][1]["H"], st[-1][1]["z"])
e.close()
