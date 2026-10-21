"""Track C: does a chain of OLD segments replay unchanged behind a NEW first segment?  (u16b_chain.py / u16a_chk.py's method)

    python u17c_chain.py <tag> <first segment>[@bookmark] <segment>[@refbookmark] ...
The first segment is replayed from its own bookmark (or the one given).  Every following segment is replayed twice: from its OWN
bookmark (the reference) and behind the chain; RAM compared after every frame (stack page excluded).  -> logs/fix/u17c_chain_<tag>.txt"""
import hashlib
import sys

from u17c_lib import *

tag, segs = sys.argv[1], sys.argv[2:]
log = Log(f"u17c_chain_{tag}.txt")
e = BizHawk(log_name=f"u17c_chain_{tag}.log")
name0, _, bm0 = segs[0].partition("@")
first = segj(name0)
e.load(bm0 or first["bookmark"])
for b in seg(name0):
    e.step(bt(b), 1)
m = e.ram(0, 0x800)
log(f"{name0}: {len(first['inputs'])} inputs from {bm0 or first['bookmark']}; end {toad(m)}")
ok_all, total = True, len(first["inputs"])
for spec in segs[1:]:
    name, _, rbm = spec.partition("@")
    j = segj(name)
    ins = seg(name)
    here = e.msave()
    e.load(rbm or j["bookmark"])
    ref0 = bytes(e.ram(0, 0x800))
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
    m0 = bytes(e.ram(0, 0x800))
    d0 = [(hex(i), ref0[i], m0[i]) for i in diff(ref0, m0)]
    nd, firstd, lastd, nk, firstk, lastk, cuts, prev = 0, None, None, 0, None, None, [], None
    dl = []
    for i, b in enumerate(ins):
        e.step(bt(b), 1)
        mm = e.ram(0, 0x800)
        if hashlib.md5(cut(mm)).digest() != ref[i]:
            nd += 1
            lastd = i + 1
            if len(dl) < 40:
                dl.append(i + 1)
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
    log(f"{name}: {len(ins)} inputs (reference from {rbm or j['bookmark']}); entry RAM differs in {len(d0)} bytes {d0[:12]}; frames with any RAM difference {nd} "
        f"(first {firstd}, last {lastd}; {dl[:24]}); frames where the toad key differs {nk} (first {firstk}, last {lastk}); "
        f"end RAM {'IDENTICAL' if end_same else 'DIFFERENT'}; end: level {t_end['level']} toad ({t_end['x']},{t_end['h']}) health {t_end['hp']} lives {t_end['lives']} "
        f"score {t_end['score']} - the reference end: {ref_end} -> {'SAME' if end_ok else 'NOT THE SAME'}"
        + (f"; level-byte 13 -> 254 at {cuts} (old {j.get('cut1_at')}, {j.get('tbird_at')})" if cuts else ""))
log(f"chain {'ENDS EVERY LEVEL LIKE THE REFERENCE' if ok_all else 'DIFFERS FROM THE REFERENCE AT A LEVEL END'}: {total} inputs from the first segment bookmark on; "
    f"final RAM sha1 {hashlib.sha1(bytes(e.ram(0, 0x800))).hexdigest()[:8]}")
e.close()
