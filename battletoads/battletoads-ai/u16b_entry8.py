"""u16b (chain B): Level 8 -> 9 entry-dice scan for a built Level 8 segment (u16b_build.py).

Behind a rebuilt Level 8 the old Level 9 segment replays unchanged when the first frames of Level 9 come out identical
(the level load zeroes the dice $25-$28; what can differ is where the CPU stands in the idle loop).  This measures, for
the segment as built and for variants of its tail (one extra harmless press on a frame after the killing blow, a longer
or shorter wait before the page mash, the mash starting on the other button), how many of the next segment's frames
8..NA are identical to that segment's own reference (whole RAM, stack page excluded).

    python u16b_entry8.py <segment> [next=L9heli_c2] [NA=240] [mode=base|scan] [out name]
        base: only the segment as built.   scan: also the variants; with an out name the shortest fully identical
        variant is written as logs/pbeam_<out>.json (bookmark <out>_end0)
No memory writes."""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, write_json, FIX, banned, F8

SEG = sys.argv[1]
NXT = sys.argv[2] if len(sys.argv) > 2 else "L9heli_c2"
NA = int(sys.argv[3]) if len(sys.argv) > 3 else 240
MODE = sys.argv[4] if len(sys.argv) > 4 else "base"
OUT = sys.argv[5] if len(sys.argv) > 5 else None
sj = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json"))
nj = json.load(open(LOGS_DIR / f"pbeam_{NXT}.json"))
seg = [b.replace(",", "+") for b in sj["inputs"]]
nxt = [b.replace(",", "+") for b in nj["inputs"]]
kill = sj["kill_frame"] - 12483                               # segment index after the killing blow
wait0, mash0 = sj["wait"], sj["mash"]
e = BizHawk(log_name=f"u16b_entry8_{SEG}.log", fields=F8)


def cut(m):
    return m[:0x100] + m[0x200:]


e.load(nj["bookmark"])
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
e.load(sj["bookmark"])
for b in seg[:kill]:
    e.step(bt(b), 1)
base = e.msave()


def variant(wait, mash, extra=None, off=0):
    """the tail from the killing blow: `wait` empty frames, then the mash, one extra press (frame offset, button)
    -> (tail inputs to the placement, identical frames among the next 8..NA, first differing frame)"""
    e.mload(base)
    ins, stage = [], 0
    for j in range(wait + 900):
        b = "" if j < wait else mash[(j - wait) % 2]
        if extra and extra[0] == j and extra[1] not in b.split("+"):
            b = (b + "+" + extra[1]).lstrip("+")
        s = e.step(bt(b), 1)
        ins.append(b)
        if stage == 0 and s.level == 11:
            stage = 1
        if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0:
            stage = 2
        if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0:
            break
    else:
        return None, 0, None
    if not (s.hp == 47 and s.lives == 3):
        return ins, 0, 0
    if off > 0:                                               # the next segment starts `off` frames later
        for _ in range(off):
            e.step((), 1)
            ins.append("")
    elif off < 0:                                             # ... or sooner: the cut is moved back
        ins = ins[:off]
        e.mload(base)
        for b in ins:
            e.step(bt(b), 1)
    same, first = 0, None
    for j in range(len(REF)):
        e.step(bt(nxt[j]), 1)
        if j < 7:
            continue
        if cut(e.ram(0, 0x800)) == REF[j]:
            same += 1
        elif first is None:
            first = j + 1
            break
    return ins, same, first


FULL = NA - 7
ins0, same0, first0 = variant(wait0, mash0)
print(f"{SEG} as built: tail {len(ins0)} inputs (segment {kill + len(ins0)}, built {len(seg)}); next-level frames 8..{NA} identical: {same0} of {FULL}"
      f"{'  -> IN SYNC' if same0 == FULL else f'  (first difference at frame {first0})'}", flush=True)
res = [(kill + len(ins0), same0, wait0, mash0, None, 0)]
if MODE in ("scan", "offs"):
    for off in (1, -1, 2, -2):
        ins, same, first = variant(wait0, mash0, None, off)
        res.append((kill + len(ins), same, wait0, mash0, None, off))
        print(f"  as built, next segment {off:+d} frame(s): identical {same} of {FULL}", flush=True)
if MODE == "scan":
    cands = []
    for w in (wait0, wait0 - 1, wait0 + 1, wait0 - 2, wait0 + 2, wait0 - 3, wait0 + 3):
        for m in (mash0, mash0[::-1]):
            if (w, m) != (wait0, mash0):
                cands.append((w, m, None))
    import os
    j0, j1, jstep = int(os.environ.get("U16B_J0", 20)), int(os.environ.get("U16B_J1", len(ins0) - 1)), int(os.environ.get("U16B_JSTEP", 3))
    for j in list(range(j1, j0, -jstep)):
        for btn in os.environ.get("U16B_BTNS", "Select,Up,Down").split(","):
            cands.append((wait0, mash0, (j, btn)))
    maxhits = int(os.environ.get("U16B_MAXHITS", 40))
    hits = 0
    for n_done, (w, m, ex) in enumerate(cands):
        ins, same, first = variant(w, m, ex)
        if ins is None:
            continue
        res.append((kill + len(ins), same, w, m, ex, 0))
        if same == FULL:
            hits += 1
            print(f"  IN SYNC: wait {w} mash {m} extra {ex} -> segment {kill + len(ins)} inputs", flush=True)
        if n_done % 50 == 49:
            print(f"    ... {n_done + 1} variants, {hits} in sync", flush=True)
        if hits >= maxhits and ex is not None:
            break
    print(f"variants {len(res)}; in sync {sum(1 for r in res if r[1] == FULL)}", flush=True)
write_json(FIX / f"u16b_entry8_{SEG}.json", {"segment": SEG, "next": NXT, "NA": NA, "results": res})
good = sorted(r for r in res if r[1] == FULL)
if OUT and good:
    ln, same, w, m, ex, off = good[0]
    ins, same, first = variant(w, m, ex, off)
    assert same == FULL
    full = seg[:kill] + ins
    e.load(sj["bookmark"])
    for b in full:
        e.step(bt(b), 1)
    e.save(OUT + "_end0")
    d = dict(sj)
    d.update(inputs=full, wait=w, mash=m, extra=ex, offset=off, built_from=SEG, placed=12483 + len(full))
    write_json(LOGS_DIR / f"pbeam_{OUT}.json", d)
    print(f"wrote pbeam_{OUT}.json: {len(full)} inputs (wait {w}, mash {m}, extra {ex}, offset {off}); bookmark {OUT}_end0; banned presses {sum(1 for x in full if banned(x))}", flush=True)
e.close()
