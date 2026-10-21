"""Final builder's copy of chain A's u16a_syncnext.py (only the log / env names changed; python u17f_syncnext.py ...).
Chain A: put the END of a (re-fitted) segment "in sync" with the old run, so that the OLD next segment replays unchanged
behind it - bit for bit - and nothing behind it has to be re-fitted or re-solved (the Queen above all).

Why it can work (knowledge/heli_savings.md section 5, knowledge/u16b_notes.md, knowledge/early_savings.md section 6): after a
re-fit the next level's entry RAM equals the old run's; the dice are zeroed by the level load; what still differs is the
hidden CPU phase inside the idle loop, and ONE extra Select on a quiet frame near the end of the segment moves it.  Some
frames give the old phase.  This tool tries every frame of the last S and keeps the variants behind which the next old
segment's first NA frames have the old run's RAM.

    python u16a_syncnext.py <segment> <next old segment> <out> [S=300] [NA=400] [F0=16] [buttons=Select]
        segment            logs/pbeam_<segment>.json, replayed from its own bookmark
        next old segment   logs/pbeam_<next>.json; its bookmark is the OLD entry state (the reference run starts there)
        S                  how many of the segment's last frames get the extra press, one at a time
        NA, F0             in sync = frames F0..NA of the next segment have identical RAM (stack page $100-$1FF excluded);
                           the first frames may differ (level timers of the level that is loading)
    -> prints every in-sync variant; the shortest (ties: the latest press) is then proved over the WHOLE next segment
       (every frame compared with the reference run) and written as logs/pbeam_<out>.json + bookmark <out>_end0.
       logs/fix/u17f_syncnext_<out>.txt.  Exit 1 when no variant is in sync.
No memory writes.  The extra press is Select (does nothing in play); pass e.g. "Select,Up,Down" to try more.
"""
import hashlib
import os
import sys

from u16a_lib import *

segn, nxtn, out = sys.argv[1], sys.argv[2], sys.argv[3]
S = int(sys.argv[4]) if len(sys.argv) > 4 else 300
NA = int(sys.argv[5]) if len(sys.argv) > 5 else 400
F0 = int(sys.argv[6]) if len(sys.argv) > 6 else 16
BTNS = sys.argv[7].split(",") if len(sys.argv) > 7 else ["Select"]
logf = open(FIX / f"u17f_syncnext_{out}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n"); logf.flush()


def cut(m):
    return bytes(m[:0x100]) + bytes(m[0x200:])


def ekey(m):
    t = toad(m)
    return tuple(t[q] for q in ("level", "x", "h", "depth", "z", "hp", "lives", "score"))


sj, nj = segj(segn), segj(nxtn)
ins, nxt = seg(segn), seg(nxtn)
n = len(ins)
NA = min(NA, len(nxt))
e = BizHawk(log_name=f"u17f_syncnext_{out}.log")

# ---- the reference: the next segment from the OLD entry
e.load(nj["bookmark"])
ENTRY = bytes(e.ram(0, 0x800))
EK = ekey(ENTRY)
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
log(f"reference: {nxtn}[:{NA}] from {nj['bookmark']}; old entry {toad(ENTRY)}")

# ---- the segment up to S frames before its end
e.load(sj["bookmark"])
for b in ins[:n - S]:
    e.step(bt(b), 1)
base = e.msave()


def inp(i):
    """the segment's input i; past its end the last two inputs go on alternating (a mash) or the last one is held"""
    return ins[i] if i < n else (ins[n - 2], ins[n - 1])[(i - n) % 2]


def run(k=None, btn=None):
    """the last S frames with `btn` added on frame index k (0-based); the segment ends on the first frame (from n-8 on) whose
    toad / health / lives / score / level equal the old entry's.  -> (segment inputs' tail, length, identical frames F0..NA,
    first differing frame of the next segment)"""
    e.mload(base)
    tail = []
    end = None
    for i in range(n - S, n + 16):
        b = inp(i)
        if i == k and btn not in b.split("+"):
            b = (b + "+" + btn).lstrip("+")
        e.step(bt(b), 1)
        tail.append(b)
        if i >= n - 9 and ekey(e.ram(0, 0x800)) == EK:
            end = i + 1
            break
    if end is None:
        return None, None, 0, None
    same, firstd = 0, None
    for j in range(NA):
        e.step(bt(nxt[j]), 1)
        if j + 1 < F0:
            continue
        if cut(e.ram(0, 0x800)) == REF[j]:
            same += 1
        else:
            firstd = j + 1
            break
    return tail, end, same, firstd


FULL = NA - F0 + 1
tail0, end0, same0, firstd0 = run()
log(f"{segn} as it is: {n} inputs, ends at {end0}; {nxtn} frames {F0}..{NA} identical {same0}/{FULL}" + ("  IN SYNC ALREADY" if same0 == FULL else f" (first difference at {firstd0})"))
res = []
if same0 == FULL:
    res.append((end0, 0, None, None))
PRESS = os.environ.get("U17F_PRESS")                        # "frame,button": prove and write exactly this variant, no scan
S0 = int(os.environ.get("U17F_S0", 0))                     # skip the last S0 frames (already scanned)
if PRESS:
    k, btn = int(PRESS.split(",")[0]), PRESS.split(",")[1]
    tail, end, same, firstd = run(k, btn)
    log(f"  given: {btn} on frame {k}: segment {end}; identical {same}/{FULL}" + ("  IN SYNC" if same == FULL else f", first difference at {firstd}"))
    if end is not None and same == FULL:
        res.append((end, -k, k, btn))
for k in ([] if PRESS else range(n - 1 - S0, n - S - 1, -1)):
    for btn in BTNS:
        tail, end, same, firstd = run(k, btn)
        if end is None:
            continue
        if same == FULL:
            res.append((end, -k, k, btn))
            log(f"  {btn} on frame {k} (index, {n - k} before the end): segment {end}; IN SYNC")
        elif same > 30:
            log(f"  {btn} on frame {k}: segment {end}; identical {same}/{FULL}, first difference at {firstd}")
log(f"scan done: {len(res)} variants in sync of {S * len(BTNS)}; lengths {sorted(set(r[0] for r in res))}")
if not res:
    log("NO variant in sync")
    e.close()
    sys.exit(1)
res.sort()
write_json(FIX / f"u17f_syncnext_{out}.json", {"segment": segn, "next": nxtn, "S": S, "NA": NA, "F0": F0, "in_sync": [[r[0], r[2], r[3]] for r in res]})

# ---- proof over the whole next segment, candidates in order, from the bookmark in one piece
e.load(nj["bookmark"])
REFH = []
prev, cuts_ref = None, []
for i, b in enumerate(nxt):
    e.step(bt(b), 1)
    m = e.ram(0, 0x800)
    REFH.append(hashlib.md5(cut(m)).digest())
    if prev == 13 and m[0x10] == 254:
        cuts_ref.append(i + 1)
    prev = m[0x10]
m_ref_end = bytes(m)
done = False
for end, _, k, btn in res[:12]:
    new = list(ins[:n - S])
    for i in range(n - S, end):
        b = inp(i)
        if k is not None and i == k and btn not in b.split("+"):
            b = (b + "+" + btn).lstrip("+")
        new.append(b)
    e.load(sj["bookmark"])
    for b in new:
        e.step(bt(b), 1)
    m_end = bytes(e.ram(0, 0x800))
    sid = e.msave()
    bad, firstb, prev, cuts = 0, None, None, []
    for i, b in enumerate(nxt):
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        if i + 1 >= F0 and hashlib.md5(cut(m)).digest() != REFH[i]:
            bad += 1
            firstb = firstb or i + 1
        if prev == 13 and m[0x10] == 254:
            cuts.append(i + 1)
        prev = m[0x10]
    lr, ud, st, sel = banned(new)
    log(f"proof, {btn} on {k}: {out} = {len(new)} inputs ({len(new) - n:+d}); entry {toad(m_end)}; entry RAM differs from the old entry in "
        f"{[hex(a) for a in diff(m_end, ENTRY)]}; {nxtn}: {len(nxt)} frames, frames {F0}.. with any RAM difference: {bad}"
        + (f" (first {firstb})" if bad else "") + (f"; level-byte 13 -> 254 at {cuts} (old run {cuts_ref})" if cuts or cuts_ref else "")
        + f"; end RAM identical: {cut(m) == cut(m_ref_end)}; Left+Right {lr} Up+Down {ud} Start {st}")
    exact = bad == 0 and cut(m) == cut(m_ref_end)
    # a Queen segment: also good when everything up to the first cut (fight, kill, rise, the speech cut) is identical and both
    # cuts fall on the old frames - the ending behind the speech re-rolls its own dice (assemble.py is the judge of the run)
    queen_ok = bool(cuts_ref) and cuts == cuts_ref and (firstb is None or firstb > cuts_ref[0]) and cuts[-1] == len(nxt)
    if (exact or queen_ok) and lr == ud == 0:
        log(f"  accepted: {'identical to the end' if exact else 'identical through the first cut; both cuts on the old frames'}")
        e.mload(sid)
        e.save(out + "_end0")
        d = dict(sj)
        d["inputs"] = new
        d["sync"] = {"next": nxtn, "press": btn, "frame": k, "from": segn, "exact_to_the_end": exact}
        write_seg(out, d)
        log(f"wrote pbeam_{out}.json ({len(new)} inputs) and bookmark {out}_end0: {nxtn} replays unchanged behind it")
        done = True
        e.mfree(sid)
        break
    e.mfree(sid)
e.close()
sys.exit(0 if done else 1)
