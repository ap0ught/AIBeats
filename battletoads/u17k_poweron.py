"""Track K2 (copy of u16k_poweron.py with the chain as an argument): power-on check of a Level 6 segment: INTRO + <chain> +
<segment>, replayed twice from power-on.  Reports the Level 8 placement frame (level byte 7, toad hp 0 / x 0, then hp > 0 and
x > 0) and the RAM sha1 of both replays; saves states/<segment>_end0<suffix>.State after the second replay.
    python u17k_poweron.py <segment> <L4 segment: B4 | L4c5> [bookmark suffix]  -> logs/fix/u17k_poweron_<segment>_<L4>.txt"""
import hashlib, json, sys
from toads.emulator import BizHawk, LOGS_DIR
from assemble import INTRO

name, l4 = sys.argv[1], sys.argv[2]
suffix = sys.argv[3] if len(sys.argv) > 3 else ""
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
ins = []
for b, n, _ in INTRO:
    ins += [b] * n
starts = {}
for s in ["L1b", "L3u", "L3skipu", l4, name]:
    starts[s] = len(ins)
    ins += json.load(open(LOGS_DIR / f"pbeam_{s}.json"))["inputs"]
bad = [i for i, b in enumerate(ins[starts[name]:]) if "Start" in b or ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)]
out = [f"{name} behind {l4}: {len(ins)} inputs from power-on; segment starts at {starts[name]}; banned presses in the segment {len(bad)}; "
       f"inputs sha1 {hashlib.sha1(chr(10).join(ins).encode()).hexdigest()}"]
print(out[-1], flush=True)
res = []
for k in (1, 2):
    e = BizHawk(log_name=f"u17k_poweron_{name}_{l4}_{k}.log")
    stage, placed, minhp8 = 0, None, 99
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
        e.save(name + "_end0" + suffix)          # replay-exact entry bookmark for Level 8 (state after the last input)
        out.append(f"saved states/{name}_end0{suffix}.State (power-on replay behind {l4})")
        print(out[-1], flush=True)
    out.append(f"replay {k}: placement at frame {placed} (inputs end at {len(ins)}), min hp in Level 6 after the entry {minhp8}, end {t}, sha1 {h[:8]}")
    print(out[-1], flush=True)
    e.close()
ok = res[0] == res[1] and res[0][1] == len(ins)
out.append(f"power-on replays {'MATCH' if res[0][0] == res[1][0] else 'MISMATCH'}; placement on the last input: {res[0][1] == len(ins)}; VERIFIED {ok}")
print(out[-1])
open(LOGS_DIR / "fix" / f"u17k_poweron_{name}_{l4}.txt", "w").write("\n".join(out) + "\n")
