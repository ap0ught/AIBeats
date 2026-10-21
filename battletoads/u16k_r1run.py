"""Track K: room 1 probes.  Replay L6c[:n0] from L4c5_end0, then hand-written input scripts; compact trace every `every` frames.
    python u16k_r1run.py <n0> <every> <print from> <print to> "<n>:<buttons>;..." ["..." ...]
trace: idx:x,H(rel to head)/z/anim/spd/vy h=head x,H ; marks LEDGE when the toad stands at H 8120"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins0 = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
n0, every, p0, p1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
e = BizHawk(log_name="u16k_r1run.log")
e.load("L4c5_end0")
for b in ins0[:n0]:
    e.step(bt(b), 1)
root = e.msave()
for spec in sys.argv[5:]:
    ins = []
    for part in spec.split(";"):
        n, b = part.split(":")
        ins += [b] * int(n)
    e.mload(root)
    tr, ledge, prev_b = [], None, None
    for j, b in enumerate(ins):
        e.step(bt(b), 1)
        n = n0 + j + 1
        m = e.ram(0, 0x800)
        x, H, z, an, spd, hp = m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8, m[0x475], m[0x3B5], m[0x565], m[0x51A]
        hd = [(m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8) for q in range(1, 15) if m[0x3C1 + q] == 0x4C]
        vy = (m[0x4C0] if m[0x4C0] < 128 else m[0x4C0] - 256) + m[0x4CF] / 256
        if ledge is None and z == 0 and H == 8120:
            ledge = n
        if hp < 47:
            tr.append(f"{n}:HURT at {x},{H}")
            break
        if p0 <= n <= p1 and ((n - p0) % every == 0 or b != prev_b):
            rel = (H - hd[0][1]) if hd else None
            tr.append(f"{n}{('[' + b + ']') if b != prev_b else ''}:{x},{H}({rel})/z{z}/a{an}/s{spd}/v{vy:.1f} h={hd[0] if hd else None}")
        prev_b = b
    print(spec, f"\n   LEDGE at {ledge} (L6c: 1897..1900)\n   ", " ".join(tr), flush=True)
e.close()
