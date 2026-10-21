"""Chain A: does a chain of OLD segments replay unchanged behind a NEW first segment?  (same method as chain B's u16b_chain.py)

    python u16a_chk.py <first segment> <segment> [<segment> ...]
The first segment is replayed from its own bookmark.  Every following segment is replayed twice: from its OWN bookmark (the
reference: the run it was made in) and behind the chain; RAM is compared after every frame (stack page excluded).
Prints per segment: frames whose RAM differs, the first frame the toad's key differs, whether the end state is identical;
for a last segment that carries 'tbird_at' also the frame of the second level-byte 13 -> 254 change behind the chain.
-> logs/fix/u16a_chain_<first>.txt.  Writes nothing else."""
import hashlib
import sys

from u16a_lib import *

segs = sys.argv[1:]
logf = open(FIX / f"u16a_chk_{segs[0]}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n"); logf.flush()


def cut(m):
    return bytes(m[:0x100]) + bytes(m[0x200:])


def key(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x41B], m[0x475], m[0x51A], m[0x10], m[0x11])


e = BizHawk(log_name=f"u16a_chk_{segs[0]}.log")
first = segj(segs[0])
e.load(first["bookmark"])
for b in seg(segs[0]):
    e.step(bt(b), 1)
m = e.ram(0, 0x800)
log(f"{segs[0]}: {len(first['inputs'])} inputs from {first['bookmark']}; end {toad(m)}")
ok_all, total = True, len(first["inputs"])
for name in segs[1:]:
    j = segj(name)
    ins = seg(name)
    here = e.msave()
    e.load(j["bookmark"])
    ref0 = cut(e.ram(0, 0x800))
    ref, refk = [], []
    for b in ins:
        e.step(bt(b), 1)
        mm = e.ram(0, 0x800)
        ref.append(hashlib.md5(cut(mm)).digest())
        refk.append(key(mm))
    tr = toad(mm)
    ref_end = (tr["hp"], tr["lives"], tr["score"], tr["level"], tr["x"], tr["h"])
    e.mload(here)
    e.mfree(here)
    d0 = sum(1 for a, b in zip(cut(e.ram(0, 0x800)), ref0) if a != b)
    nd, firstd, lastd, nk, firstk, lastk, cuts, prev = 0, None, None, 0, None, None, [], None
    for i, b in enumerate(ins):
        e.step(bt(b), 1)
        mm = e.ram(0, 0x800)
        if hashlib.md5(cut(mm)).digest() != ref[i]:
            nd += 1
            lastd = i + 1
            if firstd is None:
                firstd = i + 1
        if key(mm) != refk[i]:
            nk += 1
            lastk = i + 1
            if firstk is None:
                firstk = i + 1
        if prev == 13 and mm[0x10] == 254:
            cuts.append(i + 1)
        prev = mm[0x10]
    total += len(ins)
    end_same = lastd != len(ins)
    t_end = toad(mm)
    end_ok = (t_end["hp"], t_end["lives"], t_end["score"], t_end["level"], t_end["x"], t_end["h"]) == ref_end
    ok = end_ok and (nk == 0 or lastk < len(ins))
    ok_all = ok_all and ok
    log(f"{name}: {len(ins)} inputs; entry RAM differs in {d0} bytes; frames with any RAM difference {nd} (first {firstd}, last {lastd}); "
        f"frames where the toad's key (x, height, depth, z, health, level, lives) differs {nk} (first {firstk}, last {lastk}); "
        f"end RAM {'IDENTICAL' if end_same else 'DIFFERENT'}; end: level {t_end['level']} toad ({t_end['x']},{t_end['h']}) health {t_end['hp']} lives {t_end['lives']} "
        f"score {t_end['score']} - the old chain's end: {ref_end} -> {'SAME' if end_ok else 'NOT THE SAME'}"
        + (f"; level-byte 13 -> 254 at {cuts} (old {j.get('cut1_at')}, {j.get('tbird_at')})" if cuts else ""))
log(f"chain {'ENDS EVERY LEVEL LIKE THE OLD CHAIN' if ok_all else 'DIFFERS FROM THE OLD CHAIN AT A LEVEL END'}: {total} inputs from the first segment's bookmark on; "
    f"final RAM sha1 {hashlib.sha1(bytes(e.ram(0, 0x800))).hexdigest()[:8]}")
e.close()
