"""u16b (chain B): level-entry dice scan, after l9heli_fix_entry2.py (not edited; this is a generalised copy).

After a level is rebuilt the next level's entry RAM can equal the old run's and still roll other dice a few frames later:
the difference is where the CPU stands in the idle loop that scrambles $25-$28 (knowledge/early_savings.md section 6).
One extra harmless press on a quiet frame of the rebuilt segment's tail changes that.  This tries every (frame, button)
in a window and keeps the variants after which the NEXT segment's own inputs give RAM identical to the next segment's
own reference run (replayed from its own bookmark) for NA frames - whole RAM, stack page excluded.  Behind such a
variant the next segment, and everything after it, replays unchanged.

    python u16b_entry.py <segment> <next segment> <S> <E> [NA=300] [buttons=Select] [out name to write]
        segment      logs/pbeam_<segment>.json, replayed from its own bookmark
        S..E         1-based frames of the segment that may get the extra press
        -> logs/fix/u16b_entry_<segment>.json (every variant that reaches the entry), prints the hits;
           with an out name: logs/pbeam_<out>.json = the shortest full hit (bookmark <out>_end0 saved)
No memory writes."""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR
from u16b_lib import bt, write_json, FIX, banned

SEG, NXT, S, E = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
NA = int(sys.argv[5]) if len(sys.argv) > 5 else 300
BTN = sys.argv[6].split(",") if len(sys.argv) > 6 else ["Select"]
OUT = sys.argv[7] if len(sys.argv) > 7 else None
sj = json.load(open(LOGS_DIR / f"pbeam_{SEG}.json"))
nj = json.load(open(LOGS_DIR / f"pbeam_{NXT}.json"))
seg = [b.replace(",", "+") for b in sj["inputs"]]
nxt = [b.replace(",", "+") for b in nj["inputs"]]
n = len(seg)
e = BizHawk(log_name=f"u16b_entry_{SEG}.log")


def cut(m):
    return m[:0x100] + m[0x200:]


# the next segment's own reference: its bookmark and its first NA frames
e.load(nj["bookmark"])
ENTRY = cut(e.ram(0, 0x800))
REF = []
for b in nxt[:NA]:
    e.step(bt(b), 1)
    REF.append(cut(e.ram(0, 0x800)))
print(f"reference: {NXT} from bookmark {nj['bookmark']}, {len(REF)} frames", flush=True)

e.load(sj["bookmark"])
for b in seg[:S - 1]:
    e.step(bt(b), 1)
base = e.msave()                                             # the state after S-1 inputs


def add(b, btn):
    if not btn or btn in b.split("+"):
        return b
    return (b + "+" + btn).lstrip("+")


def tail(k0, k, btn):
    """from the loaded state (after k0-1 inputs) play to the entry with `btn` added on frame k -> (segment length, equal frames, inputs)"""
    ins = []
    for i in range(k0 - 1, n - 6):
        b = add(seg[i], btn) if i + 1 == k else seg[i]
        e.step(bt(b), 1)
        ins.append(b)
    for d in range(0, 14):
        if cut(e.ram(0, 0x800)) == ENTRY:
            same = 0
            for j in range(len(REF)):
                e.step(bt(nxt[j]), 1)
                if cut(e.ram(0, 0x800)) != REF[j]:
                    break
                same += 1
            return n - 6 + d, same, ins
        i = n - 6 + d
        b = seg[i] if i < n else seg[i - 2]                    # past the end: the mash goes on in its own pattern
        if i + 1 == k:
            b = add(b, btn)
        e.step(bt(b), 1)
        ins.append(b)
    return None, 0, ins


e.mload(base)
r0 = tail(S, -1, "")
print(f"as built: entry RAM equals the reference at segment length {r0[0]} (built {n}); equal frames of the next {NA}: {r0[1]}", flush=True)
res, full = [], []
for k in range(S, E + 1):
    for b in BTN:
        if b in seg[k - 1].split("+") or banned(add(seg[k - 1], b)):
            continue
        e.mload(base)
        ln, same, ins = tail(k, k, b)
        res.append((same, ln, k, b))
        if ln is not None and same >= len(REF):
            full.append((ln, k, b))
            print(f"  FULL: {b} on frame {k} -> segment {ln} frames, the next {same} frames identical", flush=True)
    e.mload(base)                                            # roll the base one frame on
    e.step(bt(seg[k - 1]), 1)
    nb = e.msave()
    e.mfree(base)
    base = nb
    if (k - S) % 100 == 99:
        print(f"    ... frame {k}: {len(full)} full hits of {len(res)} variants; entries reached {sum(1 for t in res if t[1] is not None)}", flush=True)
res.sort(key=lambda t: (-t[0], t[1] or 10 ** 9))
print(f"variants {len(res)}; entry reached {sum(1 for t in res if t[1] is not None)}; full hits {len(full)}; best {res[:8]}", flush=True)
write_json(FIX / f"u16b_entry_{SEG}.json", {"segment": SEG, "next": NXT, "NA": NA, "as_built": r0[:2], "full": full,
                                             "all": [t for t in res if t[1] is not None][:400]})
if OUT and full:
    full.sort()
    ln, k, b = full[0]
    e.load(sj["bookmark"])
    ins = []
    for i in range(ln):
        x = seg[i] if i < n else seg[i - 2]
        if i + 1 == k:
            x = add(x, b)
        e.step(bt(x), 1)
        ins.append(x)
    assert cut(e.ram(0, 0x800)) == ENTRY
    e.save(OUT + "_end0")
    d = dict(sj)
    d["inputs"] = ins
    d["entry_press"] = [k, b]
    d["built_from"] = SEG
    write_json(LOGS_DIR / f"pbeam_{OUT}.json", d)
    print(f"wrote pbeam_{OUT}.json: {len(ins)} inputs ({b} on frame {k}); bookmark {OUT}_end0; banned presses {sum(1 for x in ins if banned(x))}", flush=True)
e.close()
