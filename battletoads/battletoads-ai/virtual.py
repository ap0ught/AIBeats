"""Stitch new pieces into a segment WITHOUT fitting each one (2026-10-02).

Every piece (fightbeam.py, shortcut searches: {a, b, inputs}) was found from the old run's own state at frame a and
ends in the old run's state at frame b (same x, height, facing, speed). Put end to end - old[:a1] + piece1 +
old[b1:a2] + piece2 + ... - the inputs describe a run that never existed in one go: after the first piece the dice
are different. rngfit.py makes it exist: it replays each part from its own old bookmark to get the reference track,
then holds the real run to it with Select re-rolls and wait repairs, in one pass.

    python virtual.py <segment> <out> <piece json> [...]
        -> logs/pbeam_<out>.json {bookmark (the segment's), inputs, parts: [{bookmark, n}]}, bookmarks <out>_p<k>
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR


def main(seg, out, pieces):
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    old = [x.replace(",", "+") for x in d["inputs"]]
    ps = sorted((json.load(open(p)) for p in pieces), key=lambda p: p["a"])
    for p, q in zip(ps, ps[1:]):
        assert p["b"] <= q["a"], f"pieces overlap: {p['a']}-{p['b']} and {q['a']}-{q['b']}"
    marks = sorted({p["a"] for p in ps} | {p["b"] for p in ps})
    e = BizHawk(log_name=f"virtual_{out}.log")
    e.load(d["bookmark"])
    for i, x in enumerate(old):
        if i in marks:
            e.save(f"{out}_at{i}")
        if i >= marks[-1]:
            break
        e.step(tuple(v for v in x.split("+") if v), 1)
    e.close()
    inputs, parts, pos = [], [], 0
    bm = d["bookmark"]
    for p in ps:
        if p["a"] > pos:
            inputs += old[pos:p["a"]]
            parts.append({"bookmark": bm, "n": p["a"] - pos})
        inputs += list(p["inputs"])
        parts.append({"bookmark": f"{out}_at{p['a']}", "n": len(p["inputs"])})
        pos, bm = p["b"], f"{out}_at{p['b']}"
    inputs += old[pos:]
    parts.append({"bookmark": bm, "n": len(old) - pos})
    json.dump({"bookmark": d["bookmark"], "inputs": inputs, "parts": parts, "note": d.get("note", "")}, open(LOGS_DIR / f"pbeam_{out}.json", "w"))
    print(f"{out}: {len(inputs)} frames in {len(parts)} parts (segment {seg} was {len(old)}; saves {len(old) - len(inputs)})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
