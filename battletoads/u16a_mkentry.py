"""Chain A: the replay-exact entry bookmark (journal 014, 'The 2-frame lesson': a segment's root must be a state reached by
INPUT REPLAY from power-on, never a savestate taken inside a tool run).

    python u16a_mkentry.py <bookmark name> <segment> [<segment> ...] [--cmp <bookmark>] [--at <n>=<bookmark> ...]
        replays assemble.py's intro + the segments from power-on (same stepping as assemble.replay), saves
        states/<bookmark name>.State after the last input, prints the RAM sha1 and the toad there, and compares the RAM
        with --cmp's bookmark (e.g. the tool-made <seg>_end0b).  --at n=name also saves a bookmark after n inputs.
    -> logs/fix/u16a_mkentry_<bookmark name>.txt, logs/<bookmark name>.pre.inputs.txt (the input list replayed)
"""
import hashlib
import sys

from u16a_lib import *

args = sys.argv[1:]
name = args[0]
segs, cmp_bm, at = [], None, {}
i = 1
while i < len(args):
    if args[i] == "--cmp":
        cmp_bm = args[i + 1]; i += 2
    elif args[i] == "--at":
        n, bm = args[i + 1].split("="); at[int(n)] = bm; i += 2
    else:
        segs.append(args[i]); i += 1
logf = open(FIX / f"u16a_mkentry_{name}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n"); logf.flush()


ins = route_inputs(segs)
(LOGS_DIR / f"{name}.pre.inputs.txt").write_text(f"# frames={len(ins)}\n" + "\n".join(ins) + "\n")
lr, ud, st, sel = banned(ins[1917:])
log(f"{name}: intro + {' '.join(segs)} = {len(ins)} inputs; after the intro: Left+Right {lr}, Up+Down {ud}, Start {st}, Select frames {sel}")
e = BizHawk(log_name=f"u16a_mkentry_{name}.log")
land = None
prev = None
for n, b in enumerate(ins, 1):
    s = e.step(bt(b), 1)
    if land is None and s.level == 1 and prev == 5 and s.anim == 4:
        land = n
    prev = s.anim
    if n in at:
        e.save(at[n])
        log(f"  saved {at[n]} after {n} inputs: {toad(e.ram(0, 0x800))}")
m = bytes(e.ram(0, 0x800))
e.save(name)
log(f"landing (clock start) at {land}; after {len(ins)} inputs: {toad(m)}; RAM sha1 {hashlib.sha1(m).hexdigest()[:8]}; saved states/{name}.State")
if cmp_bm:
    e.load(cmp_bm)
    m2 = bytes(e.ram(0, 0x800))
    d = diff(m, m2, skip_stack=False)
    log(f"against bookmark {cmp_bm}: {len(d)} RAM bytes differ {[hex(a) for a in d][:40]}")
e.close()
