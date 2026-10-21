"""The corridor's mine at (705,220) (2026-10-04): the TAS's inputs carry our toad to within 1 px of the TAS up to TAS frame 59673, where a
drifting mine (0x72) that the TAS passes clips us. Local scan: insert d idle frames before TAS input p (the following TAS inputs shift by d)
or drop d frames of a held Right there, then keep following the TAS's inputs (time-shifted) and see whether the toad passes unhurt and reaches
the corridor's exit (x >= 1115)."""
import json, re, os
from toads.emulator import BizHawk, LOGS_DIR
rows = {}
for l in open("tas/watch_1p_log.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = json.load(open("knowledge/tas1p_l9_inputs.json")); ANCHOR = 51652
seg = json.load(open(LOGS_DIR / "pbeam_L9m.json")); ours = [x.replace(",", "+") for x in seg["inputs"]]
def legal(b): return tuple(v for v in b.split("+") if v and not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def st(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x475], m[0x565], m[0x3B5])
e = BizHawk(log_name="l9fix.log"); e.load(seg["bookmark"])
for b in ours[:8403]: e.step(tuple(v for v in b.split("+") if v), 1)
t0 = 59565; T_END = 59990
def play(variant):
    """variant: (p, d, kind) kind 'idle' = d idle frames before TAS input p; 'drop' = TAS inputs p..p+d-1 replaced by idle; 'hold' = d extra frames of input p"""
    e.mload(base); ins = []; p, d, kind = variant; shift = 0; hurt = None; out = None
    t = t0 + 1
    while t < T_END:
        j = t - ANCHOR
        if t == p and kind == "idle":
            for _ in range(d): e.step((), 1); ins.append("")
        b = legal(tas[j])
        if kind == "drop" and p <= t < p + d: b = ()
        e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        if t == p and kind == "hold":
            for _ in range(d): e.step(b, 1); ins.append("+".join(b))
            m = e.ram(0, 0x800)
        r = rows.get(t)
        if r and r[3] == 0 and rows[t - 1][3] != 0:
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(b, 1); ins.append("+".join(b)); m = e.ram(0, 0x800)
        if m[0x51A] < 47 or m[0x11] < 3: hurt = t; break
        if (m[0x3FD] | m[0x3EE] << 8) >= 1115 and out is None: out = t
        if out and t > out + 30: break
        t += 1
    return hurt, out, st(m), ins
base = e.msave()
best = None
variants = [(p, d, k) for p in (59651, 59653, 59654, 59658, 59662, 59666, 59668, 59670) for d in (1, 2, 3, 4, 6) for k in ("idle", "drop", "hold")]
for v in variants:
    hurt, out, s, ins = play(v)
    print(f"{v}: hurt {hurt}, exit {out}, end {s[:4]}, {len(ins)} frames", flush=True)
    if out and not hurt and (best is None or len(ins) < best[0]):
        best = (len(ins), v, ins); e.save("L9T_out"); json.dump({"segment": "L9m", "from": 8403, "variant": v, "tas_t0": t0, "inputs": ins}, open("knowledge/l9_corridor_tas.json", "w"))
print("best", best[:2] if best else None, flush=True)
e.close()
