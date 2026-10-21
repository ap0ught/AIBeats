"""u16b (chain B): make the NEXT level roll the old dice behind a rebuilt segment - the directed version of u16b_entry8.py.

What decides it (found 2026-10-10, see knowledge/u16b_notes.md): the level load zeroes the dice $25-$28; the idle loop
that scrambles them ($871F, 213 cycles a pass, restarted every frame when the frame's logic ends) is cut by the NMI at
an instruction boundary, so the only hidden state is the CPU's alignment against the frame - a few cycles.  It can be
READ from a savestate (QuickNES core blob: bytes 4-5 timestamp in 1/15 CPU clocks, 12-13 PC, 14-19 registers).  Two
variants of the same segment that reach the next level's first frame with the same RAM and the same alignment behave
identically for ever, so each alignment has to be tested only once.

    python u16b_sync.py <segment> <next segment> <T0> <next level byte> <out> [NA=240]
        T0 = index of the first input of the segment's free tail (for a Level 8 built by u16b_build.py: its kill index,
             kill_frame - 12483); from there on one extra press per variant is added (the toad is not in play)
        env U16B_BTNS (Select,Up,Down)   U16B_TWO=1 also pairs of presses when no single one works
    For every (tail frame, button): replay from a rolling base, find the frame the toad is set down in the next level,
    read the alignment there, and - once per alignment - replay the next segment's first NA frames against that
    segment's own reference (whole RAM, stack page excluded; frames 8..NA must all be identical).
    -> logs/fix/u16b_sync_<out>.txt-style prints, logs/fix/u16b_sync_<out>.json (the table alignment -> in sync?),
       logs/pbeam_<out>.json = the shortest in-sync variant (bookmark <out>_end0)
No memory writes."""
import json
import os
import sys

from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, write_json, FIX, banned
from u16b_phase import sig as _core

SEG, NXT, T0, LVL, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
NA = int(sys.argv[6]) if len(sys.argv) > 6 else 240
BTNS = os.environ.get("U16B_BTNS", "Select,Up,Down").split(",")
F = {"level": 0x10, "x": 0x3FD, "xh": 0x3EE, "hp": 0x51A, "lives": 0x11}
sj = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json"))
nj = json.load(open(LOGS_DIR / f"pbeam_{NXT}.json"))
seg = [b.replace(",", "+") for b in sj["inputs"]]
nxt = [b.replace(",", "+") for b in nj["inputs"]]
n = len(seg)
e = BizHawk(log_name=f"u16b_sync_{OUT}.log", fields=F)
cut = lambda m: m[:0x100] + m[0x200:]
SKIP = 7


def phase():
    c = _core(e, "u16b_phase_" + OUT)
    return c[12] | c[13] << 8, c[4] | c[5] << 8, bytes(c[14:20]), c[8] & 1   # PC, timestamp, registers, frame-count parity
    # (parity: odd and even PPU frames differ by a third of a CPU cycle; behind an ODD shift of the route two runs only
    #  track each other by luck and part at a later level load - found with B8a, see knowledge/u16b_notes.md)


e.load(nj["bookmark"])
PH0 = phase()
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
PHN = phase()                                                 # the reference's alignment NA frames in: a variant that has it too (with
FULL = NA - SKIP                                              # identical RAM) has MERGED with the old run - identical for ever
print(f"reference {NXT} from {nj['bookmark']}: alignment at its entry PC ${PH0[0]:04X} timestamp {PH0[1]} (1/15 CPU clocks)", flush=True)


def tail_input(i):
    return seg[i] if i < n else seg[n - 2 + (i - n) % 2]      # past the built end the mash goes on in its own pattern


def add(b, btn):
    return b if btn in b.split("+") else (b + "+" + btn).lstrip("+")


SEEN = {}                                                     # (alignment, RAM at the cut) -> identical frames


def finish(i0, presses):
    """from the loaded state (after i0 inputs) play the tail with the presses {index: button} until the toad is set down
    -> (segment length, alignment, identical frames) or None"""
    stage, s = 0, None
    i = i0
    while i < n + 40:
        b = tail_input(i)
        if i in presses:
            b = add(b, presses[i])
        s = e.step(bt(b), 1)
        i += 1
        if stage == 0 and s.level == LVL:
            stage = 1
        if stage == 1 and s.hp == 0 and (s.x | s.xh << 8) == 0:
            stage = 2
        if stage == 2 and s.hp > 0 and (s.x | s.xh << 8) > 0:
            break
    else:
        return None
    ph = phase()
    key = (ph, cut(e.ram(0, 0x800)))
    if key not in SEEN:
        same = 0
        for j in range(len(REF)):
            e.step(bt(nxt[j]), 1)
            if j < SKIP:
                continue
            if cut(e.ram(0, 0x800)) != REF[j]:
                break
            same += 1
        if same == FULL and phase() != PHN:                   # tracks the old run but is still out of step: it will part at a later level load
            same = -1
        SEEN[key] = same
    return i, ph, SEEN[key]


def describe(ph):
    return f"PC ${ph[0]:04X} ts {ph[1]}" + (f" ({(ph[1] - PH0[1]) / 15:+.2f} cycles vs the reference)" if ph[0] == PH0[0] else "")


e.load(sj["bookmark"])
for b in seg[:T0]:
    e.step(bt(b), 1)
base = e.msave()
base0 = e.msave()                                             # kept: the state after T0 inputs (pairs start from it)
r0 = finish(T0, {})
print(f"{SEG} as built: set down at segment length {r0[0]} (built {n}); alignment {describe(r0[1])}; next-level frames 8..{NA} identical: {r0[2]} of {FULL}"
      f"{'  -> MERGED' if r0[2] == FULL else ''}", flush=True)
res = [(r0[0], r0[2] == FULL, {}, r0[1][:2])]
hits = 1 if r0[2] == FULL else 0
for i in (range(T0, n - 1) if os.environ.get("U16B_ONLYTWO") != "1" else []):   # the rolling base is the state after i inputs
    for btn in BTNS:
        if btn in seg[i].split("+") or banned(add(seg[i], btn)):
            continue
        e.mload(base)
        r = finish(i, {i: btn})
        if r is None:
            continue
        ok = r[2] == FULL
        res.append((r[0], ok, {i: btn}, r[1][:2]))
        if ok:
            hits += 1
            print(f"  MERGED: {btn} on tail frame {i - T0 + 1} (segment index {i}) -> segment {r[0]} inputs; alignment {describe(r[1])}", flush=True)
    e.mload(base)
    e.step(bt(seg[i]), 1)
    nb = e.msave()
    e.mfree(base)
    base = nb
    if (i - T0) % 100 == 99:
        print(f"    ... tail frame {i - T0 + 1}: {len(res)} variants, {hits} in sync, {len(SEEN)} alignments seen", flush=True)
table = sorted(((f"${k[0][0]:04X}", k[0][1], "same parity" if k[0][3] == PH0[3] else "ODD shift", v) for k, v in SEEN.items()), key=lambda t: t[:3])
print(f"variants {len(res)}; merged {hits}; alignments at the cut -> identical frames (of {FULL}; -1 = all identical but not merged): {table}", flush=True)
lens = {}
for ln, ok, pr, ph in res:
    lens.setdefault(ln, [0, 0])[1 if ok else 0] += 1
print("segment length -> (out of sync, in sync):", sorted(lens.items()), flush=True)
EXACT = os.environ.get("U16B_EXACT") == "1"                  # only variants whose alignment EQUALS the reference's count: behind
                                                              # those everything is identical for ever; others can track the old run
                                                              # for a whole level and still enter the level after it out of step
good = sorted((r for r in res if r[1] and (not EXACT or tuple(r[3]) == PH0[:2])), key=lambda r: (r[0], len(r[2])))
print(f"exact alignment (PC ${PH0[0]:04X} ts {PH0[1]}): {sum(1 for r in res if r[1] and tuple(r[3]) == PH0[:2])} variants, shortest "
      f"{min([r[0] for r in res if r[1] and tuple(r[3]) == PH0[:2]], default=None)}; any in-sync alignment: shortest {min([r[0] for r in res if r[1]], default=None)}", flush=True)
if not good and (os.environ.get("U16B_TWO") == "1" or os.environ.get("U16B_ONLYTWO") == "1"):            # pairs: one press early, one late (each changes the alignment by its own amount)
    import random
    rng = random.Random(int(os.environ.get("U16B_SEED", 1)))
    idx = list(range(T0, n - 1))
    for t in range(int(os.environ.get("U16B_PAIRS", 1500))):
        i1, i2 = sorted(rng.sample(idx, 2))
        pr = {i1: rng.choice(BTNS), i2: rng.choice(BTNS)}
        if any(banned(add(seg[i], b)) for i, b in pr.items()):
            continue
        e.mload(base0)
        r = finish(T0, pr)
        if r and r[2] == FULL:
            res.append((r[0], True, pr, r[1][:2]))
            print(f"  MERGED (pair): {pr} -> segment {r[0]} inputs; alignment {describe(r[1])}", flush=True)
            if sum(1 for x in res if x[1]) >= int(os.environ.get("U16B_MAXHITS", 8)):
                break
        if t % 200 == 199:
            print(f"    ... {t + 1} pairs, {sum(1 for x in res if x[1])} merged, {len(SEEN)} alignments seen", flush=True)
    table = sorted(((f"${k[0][0]:04X}", k[0][1], "same parity" if k[0][3] == PH0[3] else "ODD shift", v) for k, v in SEEN.items()), key=lambda t: t[:3])
    print(f"after the pairs: alignments -> identical frames: {table}", flush=True)
    good = sorted((r for r in res if r[1] and (not EXACT or tuple(r[3]) == PH0[:2])), key=lambda r: (r[0], len(r[2])))
write_json(FIX / f"u16b_sync_{OUT}.json", {"segment": SEG, "next": NXT, "T0": T0, "table": table,
                                            "results": [[ln, ok, {str(k): v for k, v in pr.items()}, list(ph)] for ln, ok, pr, ph in res if ok or not pr]})
if good:
    ln, ok, pr, ph = good[0]
    full = [add(tail_input(i), pr[i]) if i in pr else tail_input(i) for i in range(ln)]
    e.load(sj["bookmark"])
    for b in full:
        e.step(bt(b), 1)
    e.save(OUT + "_end0")
    d = dict(sj)
    d.update(inputs=full, built_from=SEG, sync_press={str(k): v for k, v in pr.items()})
    if "placed" in d:
        d["placed"] = d["placed"] - n + ln
    write_json(LOGS_DIR / f"pbeam_{OUT}.json", d)
    print(f"wrote pbeam_{OUT}.json: {ln} inputs ({ln - n:+d} vs as built), presses {pr}; banned presses {sum(1 for x in full if banned(x))}; bookmark {OUT}_end0", flush=True)
else:
    print("NO in-sync variant found", flush=True)
e.close()
