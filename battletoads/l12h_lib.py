"""L12h track (2026-10-09): shared helpers for rebuilding the tower from face 2 on, in the 1-player TAS's phase.
Frame index k = inputs applied since bookmark L11r_end0 (same as the L12g index up to the divergence).
While in sync with the TAS: TAS log frame f = k + OFF (OFF = 68873 at the pre-face-2 Hornhead)."""
import json, re
from toads.emulator import BizHawk, LOGS_DIR, PROJECT

OFF = 68873
KEY = {"le": "Left", "ri": "Right", "up": "Up", "do": "Down", "A": "A", "B": "B", "se": "Select", "st": "Start"}
FIX = LOGS_DIR / "fix"
FIX.mkdir(exist_ok=True)

def seg(name):
    return [x.replace(",", "+") for x in json.load(open(LOGS_DIR / f"pbeam_{name}.json"))["inputs"]]

_tas = None
def tas():
    """{f: dict(p, x, h, z, an, camy, objs=[(id, x, h, hp)])} for Level 12 of the 1-player TAS."""
    global _tas
    if _tas is None:
        _tas = {}
        for l in open(PROJECT / "tas" / "watch_1p_l12.txt"):
            if " x=" not in l: continue
            f = int(l.split()[0][1:])
            if f < 69574: continue
            m = re.search(r" x=(-?\d+) h=(-?\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+) cp=(\d+) p1=(\S+)", l)
            o = []
            if "|" in l:
                for t in l.split("|")[1].split():
                    d, r = t.split(":"); v = r.split(",")
                    if len(v) >= 3 and v[2] != "": o.append((int(d, 16), int(v[0]), int(v[1]), int(v[2])))
            _tas[f] = dict(p=m.group(10), x=int(m.group(1)), h=int(m.group(2)), z=int(m.group(3)), st=int(m.group(4)), an=int(m.group(5)), camy=int(m.group(8)), objs=o)
    return _tas

def tbtn(f, air="Left", ground=""):
    """The TAS's input on log frame f as our input string; a banned Left+Right becomes `air` when the TAS toad is airborne, `ground` when it stands."""
    r = tas()[f]; p = r["p"]
    if p == "-": return ""
    k = re.findall(r"le|ri|up|do|se|st|A|B", p)
    if "le" in k and "ri" in k:
        k = [x for x in k if x not in ("le", "ri")]
        sub = air if r["z"] == 8 else ground
        b = [KEY[x] for x in k] + ([sub] if sub else [])
    else:
        b = [KEY[x] for x in k]
    if "Up" in b and "Down" in b: b = [x for x in b if x not in ("Up", "Down")]
    order = ["Up", "Down", "Left", "Right", "Select", "Start", "B", "A"]
    return "+".join(sorted(set(b), key=order.index))

def bt(s): return tuple(v for v in s.split("+") if v)

def rd(e, m=None):
    m = m if m is not None else e.ram(0, 0x800)
    o = [(m[0x3C1 + q], m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x51A + q], q) for q in range(2, 15) if m[0x3C1 + q]]
    cam = m[0x89] | m[0x8A] << 8
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, h=m[0x439], z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], lvl=m[0x10],
                cam=cam - 65536 if cam > 60000 else cam, t=m[0x0B], t2=m[0x0C], spd=m[0x565], sub=m[0x448], face=m[0x4A2] & 0x40, objs=o,
                faces=sum(1 for d in o if d[0] == 0x60), wind=sum(1 for d in o if d[0] == 0x61), score=bytes(m[0x5F4:0x5FA]).hex())

def ob(s, oid, H=None, tol=12):
    """x positions of objects with this id (near height H if given)."""
    return [d[1] for d in s["objs"] if d[0] == oid and (H is None or abs(d[2] - H) <= tol)]

def run(e, seq):
    for b in seq: e.step(bt(b), 1)

def alive(s): return s["hp"] >= 47 and s["lives"] >= 4 and s["lvl"] == 5

def dx(a, b):
    """signed x distance a-b on the 512-px ring."""
    return ((a - b + 256) % 512) - 256

def save_piece(name, base_bm, base_k, inputs, **kw):
    p = FIX / f"L12h_{name}.json"
    json.dump(dict(base=base_bm, base_k=base_k, inputs=inputs, **kw), open(p, "w"))
    return p

def load_piece(name):
    return json.load(open(FIX / f"L12h_{name}.json"))
