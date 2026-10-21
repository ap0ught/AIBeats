"""Track K: power-on check of a Level 6 segment: INTRO + L1b L3u L3skipu L4c5 + <segment>, replayed twice from power-on.
Reports the Level 8 placement frame (level byte 7, toad hp 0 / x 0, then hp > 0 and x > 0) and the RAM sha1 of both replays.
    python u16k_poweron.py <segment> [reference segment=L6c] -> logs/fix/u16k_poweron_<segment>.txt"""
import hashlib, json, sys
from toads.emulator import BizHawk, LOGS_DIR
from assemble import INTRO

name = sys.argv[1]
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins = []
for b, n, _ in INTRO:
    ins += [b] * n
starts = {}
for s in ["L1b", "L3u", "L3skipu", "L4c5", name]:
    starts[s] = len(ins)
    ins += json.load(open(LOGS_DIR / f"pbeam_{s}.json"))["inputs"]
out = [f"{name}: {len(ins)} inputs from power-on; segment starts at {starts[name]}"]
res = []
for k in (1, 2):
    e = BizHawk(log_name=f"u16k_poweron_{name}_{k}.log")
    stage, placed, minhp8, lives = 0, None, 99, None
    for i, b in enumerate(ins):
        e.step(bt(b), 1)
        if i >= starts[name] - 5:
            m = e.ram(0, 0x800)
            lv, hp, x = m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8
            if lv == 8 and i >= starts[name] + 300:
                minhp8 = min(minhp8, hp)
            if stage == 0 and lv == 7:
                stage = 1
            if stage == 1 and hp == 0 and x == 0:
                stage = 2
            if stage == 2 and hp > 0 and x > 0 and placed is None:
                placed = i + 1
    m = bytes(e.ram_all())
    h = hashlib.sha1(m).hexdigest()
    t = dict(level=m[0x10], x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, hp=m[0x51A], lives=m[0x11], score="".join(str(d) for d in m[0x5F4:0x5FA]))
    res.append((h, placed))
    if k == 2 and res[0] == res[1] and placed == len(ins):
        e.save(name + "_end0")          # replay-exact entry bookmark for the next level (state after the last input)
        cmp = None
        try:
            e.load(name + "_end0b")
            e.step((), 0) if False else None
            m2 = bytes(e.ram_all())
            cmp = [hex(i) for i in range(0x800) if m[i] != m2[i]]
        except Exception as ex:
            cmp = f"n/a ({ex})"
        out.append(f"saved states/{name}_end0.State (power-on replay); RAM bytes differing from the bookmark replay {name}_end0b: {cmp}")
        print(out[-1], flush=True)
    out.append(f"replay {k}: placement at frame {placed} (inputs end at {len(ins)}), min hp in Level 6 after the entry {minhp8}, end {t}, sha1 {h[:8]}")
    print(out[-1], flush=True)
    e.close()
ok = res[0] == res[1] and res[0][1] == len(ins)
out.append(f"power-on replays {'MATCH' if res[0][0] == res[1][0] else 'MISMATCH'}; placement on the last input: {res[0][1] == len(ins)}; VERIFIED {ok}")
print(out[-1])
open(LOGS_DIR / "fix" / f"u16k_poweron_{name}.txt", "w").write("\n".join(out) + "\n")
