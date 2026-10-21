"""Track C: replay-exact entry bookmark by power-on replay (u16a_mkentry.py's method; same stepping as assemble.replay).

    python u17f_poweron.py <bookmark name (C...)> <segment> [<segment> ...] [--cmp <bookmark>] [--lvl <next level byte>]
        replays assemble.py's intro + the segments from power-on, saves states/<bookmark name>.State after the last input, prints the
        RAM sha1 and the toad there, the frame the toad is set down in the next level (--lvl), every level-byte change, health /
        lives / score when each level byte changes, and compares the RAM with --cmp's bookmark.
    -> logs/fix/u17f_poweron_<bookmark name>.txt"""
import hashlib
import sys

from u17f_lib import *

args = sys.argv[1:]
name = args[0]
assert name.startswith("Fk") or name.startswith("u17f_"), "final builder only writes F* / u17f_* bookmarks"
segs, cmp_bm, LVL = [], None, None
i = 1
while i < len(args):
    if args[i] == "--cmp":
        cmp_bm = args[i + 1]; i += 2
    elif args[i] == "--lvl":
        LVL = int(args[i + 1]); i += 2
    else:
        segs.append(args[i]); i += 1
log = Log(f"u17f_poweron_{name}.txt")
ins = route_inputs(segs)
lr, ud, st, sel = banned(ins[1917:])
log(f"{name}: intro + {' '.join(segs)} = {len(ins)} inputs; after the intro: Left+Right {lr}, Up+Down {ud}, Start {st}, Select frames {sel}")
e = BizHawk(log_name=f"u17f_poweron_{name}.log")
land, prev, prev_lv, stage, placed = None, None, None, 0, None
for n, b in enumerate(ins, 1):
    s = e.step(bt(b), 1)
    if land is None and s.level == 1 and prev == 5 and s.anim == 4:
        land = n
    prev = s.anim
    if n > 1917 and (s.level != prev_lv or n == len(ins)):
        m = e.ram(0, 0x800)
        t = toad(m)
        if s.level != prev_lv and prev_lv not in (254, 255, None):
            log(f"  frame {n}: level byte {prev_lv} -> {s.level}; health {t['hp']} lives {t['lives']} score {t['score']}")
    if LVL is not None and placed is None:
        m = e.ram(0, 0x800) if n > len(ins) - 400 else None
        if m is not None:
            stage = placed_stage(stage, m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, LVL)
            if stage == 3:
                placed = n
    prev_lv = s.level
m = bytes(e.ram(0, 0x800))
e.save(name)
log(f"landing (clock start) at {land}; after {len(ins)} inputs: {toad(m)}; RAM sha1 {hashlib.sha1(m).hexdigest()[:8]}; saved states/{name}.State"
    + (f"; toad set down in level byte {LVL} on frame {placed} (last input {len(ins)})" if LVL is not None else ""))
if cmp_bm:
    e.load(cmp_bm)
    m2 = bytes(e.ram(0, 0x800))
    d = diff(m, m2, skip_stack=False)
    log(f"against bookmark {cmp_bm}: {len(d)} RAM bytes differ {[hex(a) for a in d][:40]}")
e.close()
