"""Track TOWER1 (2026-10-10): helpers for the first 5,000 frames of the tower (Level 12, The Revolution).
Frame index k = inputs applied since bookmark A11r_end0 (the A12r/A12x index). Copy of l12h_lib.py's helpers
with this track's own piece prefix (logs/fix/tw1_*.json). Nothing here writes memory."""
import json, os, re
from toads.emulator import BizHawk, LOGS_DIR, PROJECT, STATES_DIR

FIX = LOGS_DIR / "fix"
FIX.mkdir(exist_ok=True)
BASE_BM = "A11r_end0"
TAS0 = 69570                # first row of logs/fix/tas_l12.ram / tas_l12_inputs.txt
TASP = 69603                # TAS placement frame (tas events are relative to it)
ORDER = ["Up", "Down", "Left", "Right", "Select", "Start", "B", "A"]

def seg(name):
    return [x.replace(",", "+") for x in json.load(open(LOGS_DIR / f"pbeam_{name}.json"))["inputs"]]

def bt(s): return tuple(v for v in s.split("+") if v)

def norm(b):
    return "+".join(sorted(set(v for v in b.split("+") if v), key=ORDER.index))

def banned(b):
    v = set(bt(b))
    return ("Left" in v and "Right" in v) or ("Up" in v and "Down" in v) or ("Start" in v)

def rdm(m):
    o = [(m[0x3C1 + q], m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8, m[0x51A + q], q) for q in range(2, 15) if m[0x3C1 + q]]
    cam = m[0x89] | m[0x8A] << 8
    return dict(x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, h=m[0x439], z=m[0x475], an=m[0x3B5], hp=m[0x51A], lives=m[0x11], lvl=m[0x10],
                cam=cam - 65536 if cam > 60000 else cam, t=m[0x0B], t2=m[0x0C], spd=m[0x565], sub=m[0x448], subx=m[0x457], face=m[0x4A2] & 0x40, objs=o,
                dep=m[0x41B], st=m[0x4B1], faces=sum(1 for d in o if d[0] == 0x60), wind=sum(1 for d in o if d[0] == 0x61),
                score=bytes(m[0x5F4:0x5FA]).hex(), rng=bytes(m[0x25:0x29]).hex())

def rd(e, m=None):
    return rdm(m if m is not None else e.ram(0, 0x800))

def ob(s, oid, H=None, tol=12):
    return [d[1] for d in s["objs"] if d[0] == oid and (H is None or abs(d[2] - H) <= tol)]

def run(e, seq):
    for b in seq: e.step(bt(b), 1)

def alive(s): return s["hp"] >= 47 and s["lives"] >= 4 and s["lvl"] == 5

def dx(a, b):
    return ((a - b + 256) % 512) - 256

def fmt(k, b, s, ids=(0x36, 0x34, 0x5c, 0x62, 0x5f, 0x60, 0x5d)):
    return (f"{k} {b:12s} x={s['x']} H={s['H']} z={s['z']} an={s['an']} spd={s['spd']} sub={s['sub']} cam={s['cam']} t={s['t']} hp={s['hp']} |"
            + " ".join(f"{d[0]:02x}:{d[1]},{d[2]},{d[3]}" for d in s["objs"] if d[0] in ids))

def atomic_json(path, obj):
    path = str(path); tmp = path + ".tmp"
    if os.path.exists(path):
        try:
            with open(path, "rb") as f: old = f.read()
            with open(path + ".backup", "wb") as f: f.write(old)
        except OSError: pass
    with open(tmp, "w", encoding="utf-8") as f: json.dump(obj, f)
    os.replace(tmp, path)

def save_piece(name, base_bm, base_k, inputs, **kw):
    p = FIX / f"tw1_{name}.json"
    atomic_json(p, dict(base=base_bm, base_k=base_k, inputs=inputs, **kw))
    return p

def load_piece(name):
    return json.load(open(FIX / f"tw1_{name}.json", encoding="utf-8"))

def write_seg(name, bookmark, inputs, note, **kw):
    assert name.startswith("T12") or name.startswith("T13"), name
    for b in inputs: assert not banned(b), b
    atomic_json(LOGS_DIR / f"pbeam_{name}.json", dict(bookmark=bookmark, inputs=[norm(b) for b in inputs], note=note, **kw))

_tasram = None
def tasram():
    global _tasram
    if _tasram is None: _tasram = open(FIX / "tas_l12.ram", "rb").read()
    return _tasram

def tasrow(r):
    """RAM row of the TAS at placement-relative frame r (events in logs/fix/tas_l12_events.txt use r)."""
    i = r + (TASP - TAS0); b = tasram()
    return b[i * 2048:(i + 1) * 2048]

_tasin = None
def tasin(r):
    """TAS pad on placement-relative frame r as our button string (banned combos kept as-is: caller decides)."""
    global _tasin
    if _tasin is None:
        _tasin = {}
        for l in open(FIX / "tas_l12_inputs.txt"):
            f, b = l.split(); _tasin[int(f[1:])] = b
    b = _tasin[r + TASP]
    names = ["Right", "Left", "Down", "Up", "Start", "Select", "B", "A"]
    return "+".join(sorted([n for n, c in zip(names, b) if c != "."], key=ORDER.index))
