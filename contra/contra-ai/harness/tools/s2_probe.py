"""Probe: load a state, play a simple scripted input, print room events and enemy tables.

    python tools/s2_probe.py <state> <frames> [script]

script: comma list of "<from>-<to>:<buttons>" (frame offsets from the state), e.g. "0-50:Right,200-202:B"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import BizHawk  # noqa: E402
from contra.stages.base_common import make_fields, fmt_enemies, fmt_bullets, enemies  # noqa: E402

state, n = sys.argv[1], int(sys.argv[2])
script = sys.argv[3] if len(sys.argv) > 3 else ""
verbose = "-v" in sys.argv
rows = [() for _ in range(n)]
for part in script.split(","):
    if not part:
        continue
    rng, btn = part.split(":")
    a, b = rng.split("-")
    for i in range(int(a), int(b) + 1):
        if i < n:
            rows[i] = tuple(set(rows[i]) | set(x for x in btn.split("+") if x))
F = make_fields()
with BizHawk(log_name="s2_probe.log", fields=F) as e:
    s0 = e.load(state)
    print("start", {k: s0[k] for k in ("frame", "frame_fc", "rng", "lroutine", "level", "screen", "x", "y", "weapon", "lives")})
    e.trace(True)
    e.run(rows)
    tr = e.last_trace
prev = s0
keys = ("lroutine", "screen", "scroll", "cleared", "cores", "plates", "atkcount", "loc", "pstate", "death", "adv",
        "iscroll", "bossdef", "attack", "jflag", "pseq", "jump", "elr")
for i, s in enumerate(tr):
    ev = []
    for k in keys:
        if s[k] != prev[k]:
            ev.append(f"{k} {prev[k]}->{s[k]}")
    if s["elec"] and not prev["elec"]:
        ev.append("ELEC")
    if s["lagged"]:
        ev.append("LAG")
    pe = {x[0]: x for x in enemies(prev)}
    ce = {x[0]: x for x in enemies(s)}
    for k in ce:
        if k not in pe:
            ev.append(f"+e{k} t{ce[k][2]:02x} hp{ce[k][3]} ({ce[k][4]},{ce[k][5]}) s{ce[k][6]:02x} a{ce[k][8]:02x}")
        else:
            a, b = pe[k], ce[k]
            if a[2] != b[2]:
                ev.append(f"e{k} type {a[2]:02x}->{b[2]:02x}")
            if a[3] != b[3]:
                ev.append(f"e{k}(t{b[2]:02x}) hp {a[3]}->{b[3]}")
            if a[6] != b[6]:
                ev.append(f"e{k}(t{b[2]:02x}) st {a[6]:02x}->{b[6]:02x}")
            if a[1] != b[1]:
                ev.append(f"e{k}(t{b[2]:02x}) rt {a[1]}->{b[1]}")
    for k in pe:
        if k not in ce:
            ev.append(f"-e{k} t{pe[k][2]:02x}")
    if ev or verbose:
        print(f"i={i:4d} f={s['frame']:5d} fc={s['frame_fc']:3d} x={s['x']:3d} y={s['y']:3d} in={'+'.join(rows[i]) or '.':10s} "
              + "; ".join(ev) + (("  B: " + fmt_bullets(s)) if verbose else ""))
    prev = s
print("last enemies:", fmt_enemies(tr[-1]))
