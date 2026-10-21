"""Verifier: is the 30-presses-a-second page mashing needed, or is it cosmetic?

    python u16v_demash.py <inputs file> <reference capture tag> <out inputs file>

For each mash stretch (rows that are exactly 'A' or 'B', toggling every frame) every mash press is removed, then single
presses are put back one at a time only where the game's RAM (the capture of the plain replay, pad bytes masked) would
otherwise change. The result is an input list with one press where the game takes one; it must then be replayed from
power-on by u16v_replay.py (final RAM sha1 and the whole capture are compared there, not here).
Savestates are in-memory core states of this one emulator; no memory writes.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

from toads.emulator import BizHawk, BUTTONS

HERE = Path(__file__).resolve().parent
FIX = HERE / "logs" / "fix"
STRETCHES = [(2312, 2516), (4732, 4778), (9664, 9887), (12358, 12481), (16187, 16375), (26036, 26163), (27960, 28106),
             (34841, 34985), (45006, 45016)]
MASK = (0x29, 0x2A, 0x2B, 0x2C)          # pad bytes: held / new, both controllers
TAIL = 60                                # frames after a stretch that must also be identical (all bytes there)

path, reftag, outp = sys.argv[1], sys.argv[2], sys.argv[3]
raw = Path(path).read_text(encoding="utf-8").split("\n")
if raw[-1] == "":
    raw = raw[:-1]
header, rows = raw[0], raw[1:]
REF = (FIX / f"u16v_{reftag}.ram").read_bytes()
N = len(rows)
assert len(REF) == N * 2048
log = open(FIX / "u16v_demash.stdout.txt", "w", encoding="utf-8")


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    log.write(s + "\n")
    log.flush()


def toks(r):
    t = tuple(x for x in r.replace("+", ",").split(",") if x)
    assert all(b in BUTTONS for b in t)
    return t


def ref(f):
    return REF[(f - 1) * 2048:f * 2048]


def masked(b):
    b = bytearray(b)
    for m in MASK:
        b[m] = 0
    return bytes(b)


e = BizHawk(log_name="u16v_demash_emu.log", fields={"level": 0x10})
say("emulator pid", e.proc.pid)
states = {}
starts = {a - 2: a for a, b in STRETCHES}
t0 = time.time()
for i, r in enumerate(rows):
    f = i + 1
    e.step(toks(r), 1)
    if f in starts:
        states[starts[f]] = e.msave()
h = hashlib.sha1(e.ram_all()).hexdigest()
say(f"main line replayed, RAM sha1 {h} ({time.time() - t0:.0f}s)")


LOCAL = {}                               # frame -> RAM of the plain rows replayed from the SAME reloaded state


def run(a, end, cand, record=False):
    """Replay frames a-1 .. end from the state before the stretch with rows `cand` (dict frame -> row) and return
    (first frame whose masked RAM differs from the plain rows or None, full-RAM-equal over the last TAIL-20 frames).
    The comparison is against the plain rows replayed from the same reloaded state (record=True stores it): a state
    reload shifts two bytes ($1A, $100) for the first frames of a level load against a replay without a reload, so the
    power-on capture cannot be the yardstick here; the finished list is checked against it from power-on afterwards."""
    e.mload(states[a])
    first = None
    tail_ok = True
    nref = 0
    for f in range(a - 1, end + 1):
        e.step(toks(cand.get(f, rows[f - 1])), 1)
        ram = e.ram_all()
        if record:
            LOCAL[f] = ram
            if ram != ref(f):
                nref += 1
            continue
        if first is None and masked(ram) != masked(LOCAL[f]):
            first = f
        if f > end - TAIL + 20 and ram != LOCAL[f]:
            tail_ok = False
    if record:
        return nref
    return first, tail_ok


new_rows = list(rows)
report = []
for a, b in STRETCHES:
    end = min(N, b + TAIL)
    mash = [f for f in range(a, b + 1) if rows[f - 1] in ("A", "B")]
    nref = run(a, end, {}, record=True)
    f0, ok0 = run(a, end, {})
    assert f0 is None and ok0, f"sanity: the plain rows do not reproduce themselves from the state at stretch {a} ({f0}, {ok0})"
    assert LOCAL[end] == ref(end), f"stretch {a}: the reloaded state does not rejoin the power-on capture by frame {end}"
    cand = {f: "" for f in mash}
    kept = []
    tries = 0
    while True:
        tries += 1
        first, tail_ok = run(a, end, cand)
        if first is None and tail_ok:
            break
        if first is None:
            raise SystemExit(f"stretch {a}-{b}: masked RAM equal but the tail differs")
        # put back the latest removed press at or before the first differing frame; if that does not move the
        # difference later, the loop puts back the one before it next time
        back = [f for f in mash if f <= first and cand.get(f) == ""]
        if not back:
            raise SystemExit(f"stretch {a}-{b}: difference at {first} with no removed press before it")
        g = back[-1]
        del cand[g]
        kept.append(g)
        if tries > 400:
            raise SystemExit(f"stretch {a}-{b}: no convergence")
    # second pass: try to drop each kept press again (a press put back on the way that turned out not to be needed)
    for g in sorted(kept):
        cand[g] = ""
        first, tail_ok = run(a, end, cand)
        if first is None and tail_ok:
            kept.remove(g)
        else:
            del cand[g]
    first, tail_ok = run(a, end, cand)
    assert first is None and tail_ok
    for f, r in cand.items():
        new_rows[f - 1] = r
    kept.sort()
    say(f"stretch {a}-{b}: {len(mash)} mash presses, {len(mash) - len(kept)} removed, kept {len(kept)}: "
        f"{[(g, rows[g - 1]) for g in kept]} ({tries} trials; frames where the reloaded state differs from the power-on capture: {nref})")
    report.append({"stretch": [a, b], "mash_presses": len(mash), "kept": [(g, rows[g - 1]) for g in kept]})
e.close()
tmp = Path(outp + ".tmp")
tmp.write_text(header + "\n" + "\n".join(new_rows) + "\n", encoding="utf-8")
tmp.replace(outp)
removed = sum(1 for x, y in zip(rows, new_rows) if x != y)
say(f"wrote {outp}: {removed} rows changed (presses removed), {N} frames")
(FIX / "u16v_demash.json").write_text(json.dumps({"removed": removed, "stretches": report}, indent=1), encoding="utf-8")
