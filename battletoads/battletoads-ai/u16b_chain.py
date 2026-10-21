"""u16b (chain B): does a chain of OLD segments replay unchanged behind a NEW first segment?

    python u16b_chain.py <first segment> <segment> [<segment> ...]
The first segment is replayed from its own bookmark.  Every following segment is replayed twice: from its OWN bookmark (the
reference: the run it was made in) and behind the chain; RAM is compared after every frame (stack page excluded).
Prints for each segment: frames whose RAM differs, the first frame the toad's key (x, height, depth, z, health, level)
differs, and whether the end state is identical; then the sha1 of the final RAM.  Read-only: writes nothing but its log."""
import hashlib
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt

segs = sys.argv[1:]
e = BizHawk(log_name=f"u16b_chain_{segs[0]}.log")


def cut(m):
    return m[:0x100] + m[0x200:]


def key(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x41B], m[0x475], m[0x51A], m[0x10], m[0x11])


first = json.load(open(LOGS_DIR / f"pbeam_{segs[0]}.json"))
e.load(first["bookmark"])
for b in first["inputs"]:
    e.step(bt(b), 1)
m = e.ram(0, 0x800)
print(f"{segs[0]}: {len(first['inputs'])} inputs from {first['bookmark']}; end level {m[0x10]} toad {key(m)}", flush=True)
ok_all, total = True, len(first["inputs"])
for name in segs[1:]:
    j = json.load(open(LOGS_DIR / f"pbeam_{name}.json"))
    ins = [b.replace(",", "+") for b in j["inputs"]]
    here = e.msave()
    e.load(j["bookmark"])
    ref0 = cut(e.ram(0, 0x800))
    ref, refk = [], []
    for b in ins:
        e.step(bt(b), 1)
        mm = e.ram(0, 0x800)
        ref.append(hashlib.md5(cut(mm)).digest())
        refk.append(key(mm))
    e.mload(here)
    e.mfree(here)
    d0 = sum(1 for a, b in zip(cut(e.ram(0, 0x800)), ref0) if a != b)
    nd, firstd, firstk, lastd = 0, None, None, None
    for i, b in enumerate(ins):
        e.step(bt(b), 1)
        mm = e.ram(0, 0x800)
        if hashlib.md5(cut(mm)).digest() != ref[i]:
            nd += 1
            lastd = i + 1
            if firstd is None:
                firstd = i + 1
        if firstk is None and key(mm) != refk[i]:
            firstk = i + 1
    total += len(ins)
    end_same = lastd != len(ins)
    ok = firstk is None and end_same
    ok_all = ok_all and ok
    print(f"{name}: {len(ins)} inputs; entry RAM differs in {d0} bytes; frames with any RAM difference {nd} (first {firstd}, last {lastd}); "
          f"toad key first differs at {firstk}; end state {'IDENTICAL' if end_same else 'DIFFERENT'}; end {key(mm)} -> {'OK' if ok else 'BROKEN'}", flush=True)
    if firstk is not None:
        break
print(f"chain {'REPLAYS UNCHANGED' if ok_all else 'DOES NOT REPLAY'}: {total} inputs after the intro-less start; final RAM sha1 {hashlib.sha1(e.ram(0, 0x800)).hexdigest()[:8]}", flush=True)
e.close()
