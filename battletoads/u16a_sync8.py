"""Chain A: build the Level 8 segment so that the OLD Level 9 segment replays unchanged behind it (no refit, no new Queen).

Chain B's finding (knowledge/u16b_notes.md): the level load zeroes the dice and resets the level timers; what can still
differ behind a rebuilt Level 8 is the hidden CPU phase in the idle loop, and that depends on the tail of Level 8 (what is
pressed during the boss's death and on the page).  Some tails come out in the old phase: then L9heli_c2 and everything
behind it are bit-identical from Level 9's frame 8 on.

    python u16a_sync8.py <out segment> <fight json> [NA=240] [arrival json]
        segment = L8c[0:3113] + arrival + fight + tail;  tail = idle, then A,B (or B,A) on alternate frames to the placement
        variants of the tail: the mash start (every frame near the level change, a coarse grid before), who presses first,
        and - if none of those is in sync at the shortest length - one extra Select/Up/Down on one frame of the tail
        in sync = frames 8..NA of L9heli_c2 behind it have the same RAM as behind L8c (stack page excluded)
    -> logs/pbeam_<out>.json = the shortest in-sync variant (ties: the latest mash start), bookmark <out>_end0b,
       logs/fix/u16a_sync8_<out>.txt / .json (every variant: length, identical frames)
No memory writes."""
import json
import os
import sys

from u16a_lib import *

out = sys.argv[1]
fj = json.load(open(sys.argv[2]))
NA = int(sys.argv[3]) if len(sys.argv) > 3 else 240
aj = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
arrival = list(aj["inputs"]) if aj else list(fj.get("arrival_prefix", []))
fight = list(fj["inputs"])
CUT = 3113
NXT = os.environ.get("U16A_NEXT", "L9heli_c2")            # the segment that must replay behind the new Level 8 (its bookmark = the reference entry)
logf = open(FIX / f"u16a_sync8_{out}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    logf.write(s + "\n"); logf.flush()


def cut(m):
    return bytes(m[:0x100]) + bytes(m[0x200:])


old = seg("L8c")
nxt = seg(NXT)
e = BizHawk(log_name=f"u16a_sync8_{out}.log")

# ---- the reference: L9heli_c2's first NA frames behind L8c, and L8c's end state
e.load(segj(NXT)["bookmark"])
m_ref = bytes(e.ram(0, 0x800))
T_REF = toad(m_ref)
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
log(f"reference: {NXT}[:{NA}] behind {segj(NXT)['bookmark']}; L8c ends {T_REF}")

# ---- the new line to the kill
e.load("L6c_end0")
pre = old[:CUT] + arrival + fight
for b in pre:
    e.step(bt(b), 1)
m = e.ram(0, 0x800)
t = toad(m)
log(f"new line: {len(pre)} inputs to the last fight input (L8c's kill is at 4394); state {t}")
assert t["level"] == 7 and t["score"] == T_REF["score"] and t["hp"] == 47 and t["lives"] == T_REF["lives"], "the fight does not end like L8c's"
base = e.msave()
KEYS = ("level", "x", "h", "depth", "z", "hp", "lives", "score")
FULL = NA - 7


def run(start, first, extra=None, compare=True):
    """tail: idle `start` frames, then (first, other) alternating; extra = (tail frame, button) pressed on top.
    -> (segment length or None, identical frames among 8..NA, first differing frame, tail inputs)"""
    e.mload(base)
    pat = ("A", "B") if first == "A" else ("B", "A")
    tail, stage = [], 0
    for k in range(1200):
        b = "" if k < start else pat[(k - start) % 2]
        if extra and extra[0] == k and extra[1] not in b.split("+"):
            b = (b + "+" + extra[1]).lstrip("+")
        s = e.step(bt(b), 1)
        tail.append(b)
        if stage == 0 and s.level == 11:
            stage = 1
        if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0:
            stage = 2
        if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0:
            break
    else:
        return None, 0, None, tail
    tt = toad(e.ram(0, 0x800))
    if not all(tt[q] == T_REF[q] for q in KEYS):
        return None, 0, None, tail
    same, firstd = 0, None
    if compare:
        for j in range(NA):
            e.step(bt(nxt[j]), 1)
            if j < 7:
                continue
            if cut(e.ram(0, 0x800)) == REF[j]:
                same += 1
            else:
                firstd = j + 1
                break
    return len(pre) + len(tail), same, firstd, tail


# ---- where the level byte leaves 7 (for the variant grid)
e.mload(base)
left = None
for k in range(700):
    s = e.step((), 1)
    if s.level != 7:
        left = k + 1
        break
log(f"the level byte leaves 7 {left} frames after the last fight input (input {len(pre) + left})")

res = []
RK = lambda r: (r[0], r[1], r[2], str(r[3]))               # sort key (extra is None or a tuple)


def try_(start, first, extra=None):
    ln, same, firstd, tail = run(start, first, extra)
    res.append((ln if ln else 10 ** 9, -start, first, extra, same, firstd))
    return ln, same, firstd


# stage 1: the mash start and the first button.  Presses on the page itself do not move the hidden phase (measured on fight
# s14: 114 variants with the mash starting in the last 70 frames, all out of sync alike); presses during the boss's
# death do (the toad hops or punches: other CPU time).  So: a few late starts, then a grid over the whole wait.
VAR = os.environ.get("U16A_VARIANT")                       # "start,first[,k,button]": build exactly this tail, no scan
STEP = int(os.environ.get("U16A_STEP", 3))
starts = list(range(left + 10, left - 12, -2)) + list(range(left - 12, -1, -STEP))
if VAR:
    v = VAR.split(",")
    starts = []
    ln, same, firstd = try_(int(v[0]), v[1], (int(v[2]), v[3]) if len(v) > 3 else None)
    log(f"  given variant {VAR}: segment {ln}; {NXT} frames 8..{NA} identical {same}/{FULL}")
for n_done, st in enumerate(starts):
    for first in ("A", "B"):
        ln, same, firstd = try_(st, first)
        log(f"  mash +{st} {first} first: segment {ln}; {NXT} frames 8..{NA} identical {same}/{FULL}" + ("  IN SYNC" if same == FULL else f" (first difference at {firstd})"))
lens = sorted(set(r[0] for r in res))
good = sorted((r for r in res if r[4] == FULL), key=RK)
log(f"stage 1: {len(res)} variants; lengths {lens[:6]}; in sync {len(good)}: {[(r[0], -r[1], r[2]) for r in good][:20]}")
# stage 2: one extra press, on top of the shortest variants, until an in-sync variant of the shortest length is in hand
if not VAR and os.environ.get("U16A_STAGE2", "1") != "0" and (not good or good[0][0] > lens[0]):
    tops = [r for r in sorted(res, key=RK) if r[0] == lens[0]][:3]
    done = False
    for ln0, nst, first, _, _, _ in tops:
        for k in range(left - 1, -1, -1):                  # (frames of the death wait: page frames do not move the phase)
            for btn in ("Select", "Up", "Down"):
                ln, same, firstd = try_(-nst, first, (k, btn))
                if same == FULL:
                    log(f"  mash +{-nst} {first} first + {btn} on tail frame {k}: segment {ln}  IN SYNC")
                    if ln == lens[0]:
                        done = True
                        break
            if done:
                break
        if done:
            break
    good = sorted((r for r in res if r[4] == FULL), key=RK)
    log(f"stage 2: {len(res)} variants in all; in sync {len(good)}; best {good[0] if good else None}")
write_json(FIX / f"u16a_sync8_{out}.json", {"fight": sys.argv[2], "NA": NA, "left": left, "pre": len(pre),
                                            "results": [[r[0], -r[1], r[2], r[3], r[4], r[5]] for r in sorted(res, key=RK)]})
if not good:
    log("NO variant in sync - fall back to the refit (u16a_rngfit.py)")
    e.close()
    sys.exit(1)
# ---- the WHOLE next segment behind the best candidates (shortest first): the quick test passes tails that are only NEAR the
#      old phase (a few stray frames with other dice, e.g. 10 of 9,790 behind fight s14's first pick).  Preferred: a tail
#      behind which no frame after the 7th differs; accepted: the toad's key never differs and the end state is the old one.
nxt_all = seg(NXT)
e.load(segj(NXT)["bookmark"])
REFH, REFK = [], []
for b in nxt_all:
    e.step(bt(b), 1)
    mm = e.ram(0, 0x800)
    REFH.append(cut(mm))
    REFK.append((mm[0x3FD] | mm[0x3EE] << 8, mm[0x439], mm[0x41B], mm[0x475], mm[0x51A], mm[0x10], mm[0x11]))


def whole(start, first, extra):
    ln, same, firstd, tail = run(start, first, extra, compare=False)
    nd = nk = 0
    for j, b in enumerate(nxt_all):
        e.step(bt(b), 1)
        mm = e.ram(0, 0x800)
        if j >= 7 and cut(mm) != REFH[j]:
            nd += 1
        if (mm[0x3FD] | mm[0x3EE] << 8, mm[0x439], mm[0x41B], mm[0x475], mm[0x51A], mm[0x10], mm[0x11]) != REFK[j]:
            nk += 1
    return ln, nd, nk, cut(mm) == REFH[-1], tail


picked = None
for r in good[:int(os.environ.get("U16A_WHOLE", 8))]:
    ln, nd, nk, endsame, tail_w = whole(-r[1], r[2], r[3])
    log(f"  whole {NXT} behind (mash +{-r[1]}, {r[2]} first, extra {r[3]}; segment {ln}): frames after the 7th with any RAM difference {nd}, "
        f"with a toad difference {nk}, end RAM {'identical' if endsame else 'DIFFERENT'}")
    cand = (ln, nk > 0 or not endsame, nd, r)
    if picked is None or cand[:3] < picked[:3]:
        picked = cand
    if nd == 0 and endsame and ln == good[0][0]:
        break
if picked is None or picked[1]:
    log("no candidate keeps the toad on the old track through the whole next segment")
    e.close()
    sys.exit(1)
ln, nst, first, extra, same, _ = picked[3]
log(f"picked: mash +{-nst}, {first} first, extra {extra}: {picked[2]} stray frames in the whole of {NXT}" + ("  (EXACT phase)" if picked[2] == 0 else "  (near phase: prove with u16a_chk.py and assemble.py)"))
ln2, same2, firstd2, tail = run(-nst, first, extra)
assert ln2 == ln and same2 == FULL
ins = pre + tail
e.mfree(base)
# ---- one more replay in one piece from the bookmark, then the next segment's first NA frames again
e.load("L6c_end0")
for b in ins:
    e.step(bt(b), 1)
m = bytes(e.ram(0, 0x800))
e.save(out + "_end0b")
dif = diff(m, m_ref)
same3 = 0
for j in range(NA):
    e.step(bt(nxt[j]), 1)
    if j >= 7 and cut(e.ram(0, 0x800)) == REF[j]:
        same3 += 1
lr, ud, st, sel = banned(ins)
t_new = toad(m)
log(f"chosen: mash from +{-nst}, {first} first, extra {extra}: {out} = {len(ins)} inputs (L8c {len(old)}: {len(old) - len(ins)} saved)")
log(f"replay in one piece: end {t_new}; RAM bytes that differ from L8c's end (stack excluded) {[hex(a) for a in dif]}; "
    f"{NXT} frames 8..{NA} identical {same3}/{FULL}; banned presses: Left+Right {lr}, Up+Down {ud}, Start {st}; frames with Select {sel}")
ok = same3 == FULL and lr == ud == st == 0 and all(t_new[q] == T_REF[q] for q in KEYS)
if ok:
    write_seg(out, {"bookmark": "L6c_end0", "inputs": ins, "slack": 0, "kill_at": len(pre),
                    "built_from": {"L8c": [0, CUT], "arrival": len(arrival), "fight": sys.argv[2], "fight_frames": len(fight),
                                   "mash_start_after_fight": -nst, "mash_first": first, "extra": extra, "in_sync_with": NXT},
                    "note": "LEVEL 8: INTRUDER EXCLUDER. The climb as before; the last jump is steered right so the arrival cutscene hands control "
                            "back at x 183, next to Robo-Manus. Only the jump-smash keeps him in his corner: which attack B gives is a dice "
                            "roll, and a Select press on an earlier frame re-rolls it.||"
                            f"{len(ins)} frames (was {len(old)}); A and B on alternate frames skip the next page"})
    log(f"wrote pbeam_{out}.json")
else:
    log("NOT written")
e.close()
sys.exit(0 if ok else 1)
