"""Ending experiments on the published fight (L13y0): which inputs change the frames between the kill and the cut to T. Bird?
E1 speech-skip patterns from cut 1; E2 inputs during the last tower scene; E3 inputs during the body flight / countdown / rise.
Baseline: cut1 at input 1694, tower again 1705, T. Bird 2196."""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR
e = BizHawk(log_name="l13z_tail1.log")
out = open(LOGS_DIR / "fix" / "l13z_tail1.txt", "a")
def P(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); out.write(s + "\n"); out.flush()

def run(n0, pat_fn, limit=1400, want=2):
    """from the current state (after n0 inputs): step with pat_fn(k) until `want` 13->254 transitions (counting from level now)"""
    prev = e.byte(0x10); n = n0; ev = []; cuts = 0; hpmin = 99
    for k in range(limit):
        e.step(pat_fn(k), 1); n += 1
        r = e.ram(0x10, 1)[0]
        if r != prev:
            ev.append((n, prev, r))
            if prev == 13 and r == 254:
                cuts += 1
                if cuts >= want: break
            prev = r
        if k % 8 == 0:
            hpmin = min(hpmin, e.byte(0x51A))
    return n, ev, hpmin

# ---- E1: speech skip, from cut1 (input 1694; level 254)
e.load("L13z_y0_cut1"); base = e.msave()
pats = {"none": lambda k: (), "A_even": lambda k: ("A",) if k % 2 == 0 else (), "A_odd": lambda k: ("A",) if k % 2 == 1 else (),
        "A_hold": lambda k: ("A",), "B_even": lambda k: ("B",) if k % 2 == 0 else (), "Sel_even": lambda k: ("Select",) if k % 2 == 0 else (),
        "AB_even": lambda k: ("A", "B") if k % 2 == 0 else ()}
for j in range(0, 14):
    pats[f"A_once@{j}"] = (lambda j: lambda k: ("A",) if k == j else ())(j)
for name, fn in pats.items():
    e.mload(base)
    n, ev, hp = run(1694, fn, limit=1300, want=1)
    P("E1", name, "events", ev, "end", n)
# ---- E2: last tower scene. get the state right when level returns to 13 (A_even)
e.mload(base)
n = 1694; k = 0
while True:
    e.step(("A",) if k % 2 == 0 else (), 1); n += 1; k += 1
    if e.byte(0x10) == 13: break
P("tower again at", n)
tower = e.msave()
pats2 = {"none": lambda k: (), "A_even(cont)": lambda k: ("A",) if k % 2 == 1 else (), "Left": lambda k: ("Left",), "Right": lambda k: ("Right",),
         "Right+A": lambda k: ("Right", "A") if (k // 20) % 2 == 0 else ("Right",), "B_alt": lambda k: ("B",) if k % 2 == 0 else (), "Select_alt": lambda k: ("Select",) if k % 2 == 0 else (),
         "Down": lambda k: ("Down",), "Up": lambda k: ("Up",), "A_hold": lambda k: ("A",), "B_hold": lambda k: ("B",)}
for name, fn in pats2.items():
    e.mload(tower)
    n2, ev, hp = run(n, fn, limit=1300, want=1)
    r = e.ram_all()
    P("E2", name, "events", ev, "end", n2, "toad x", r[0x3FD], "hpmin", hp)
# ---- E3: from 12 frames after the kill (input 1040): toad inputs until cut 1
e.load("L13z_y0_i1040"); k1040 = e.msave()
pats3 = {"none": lambda k: (), "Left": lambda k: ("Left",), "Right 40 (to x~128)": lambda k: ("Right",) if 30 <= k < 70 else (), "Right all": lambda k: ("Right",),
         "A_alt": lambda k: ("A",) if k % 2 == 0 else (), "B_alt": lambda k: ("B",) if k % 2 == 0 else (), "Select_alt": lambda k: ("Select",) if k % 2 == 0 else (),
         "Right+A jumps": lambda k: ("Right", "A") if (k // 16) % 2 == 0 else ("Right",), "Down": lambda k: ("Down",)}
for name, fn in pats3.items():
    e.mload(k1040)
    n3, ev, hp = run(1040, fn, limit=1500, want=1)
    r = e.ram_all()
    P("E3", name, "events", ev, "cut1", n3, "toad x", r[0x3FD] + 256 * r[0x3EE], "hpmin", hp)
e.close()
