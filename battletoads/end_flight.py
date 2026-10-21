"""Track END probe (snapshot + debug poke, never part of a run): how long is the dead Queen's flight as a function of the
height she was hit at? On up14's last-hit frame (46085, id already 0x46, velocity 7 set, 9 frozen frames ahead) her height byte
is overwritten with each value 44..230; frames until the id is 0x7e again (the respawn) and her height there.
    -> logs/fix/end_flight.json {height: [flight frames, respawn height]}, logs/fix/end_flight.tsv"""
import json

from toads.emulator import BizHawk, LOGS_DIR

lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
HIT = 46085
S = 3
e = BizHawk(log_name="end_flight.log")
e.load("cap14_f46000")
for i in range(46000, HIT):
    e.step(bt(lines[i]), 1)
base = e.msave()
s8 = lambda v: v - 256 if v > 127 else v
out = {}
rows = []


def run(qh, sub=None):
    e.mload(base)
    e.poke(0x439 + S, qh & 0xFF)
    e.poke(0x42A + S, 0)
    if sub is not None:
        e.poke(0x466 + S, sub)
    f = HIT
    bounce = None
    while f < HIT + 400:
        e.step((), 1)
        f += 1
        m = e.ram(0x3C0, 0x1E0)                  # $3C0..$59F
        g = lambda a: m[a - 0x3C0]
        if bounce is None and g(0x592 + S) == 0xF1:
            bounce = f
        if g(0x3C1 + S) == 0x7E:
            return f - HIT, g(0x439 + S) + 256 * s8(g(0x42A + S)), (bounce - HIT) if bounce else None
    return None, None, None


print("natural (130):", run(130), flush=True)
for qh in range(44, 231):
    fl, h0, b = run(qh)
    out[qh] = [fl, h0, b]
    rows.append((qh, fl, h0, b))
    print(qh, fl, h0, b, flush=True)
for sub in (0, 64, 128, 192, 255):
    print("qh 44 sub-pixel", sub, run(44, sub), "qh 130 sub", sub, run(130, sub), flush=True)
(LOGS_DIR / "fix" / "end_flight.json").write_text(json.dumps(out))
(LOGS_DIR / "fix" / "end_flight.tsv").write_text("queen_height\tflight\trespawn_height\tbounce_at\n" + "\n".join("\t".join(map(str, r)) for r in rows) + "\n")
e.close()
