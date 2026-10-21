"""How fast can each level's briefing page be skipped? (2026-10-02)

The record's video shows ~1 s of black between levels; our late segments press Start a few times and then wait
~220 frames on the "LEVEL n" briefing page. For each segment: replay it from its bookmark, find the frame the
level byte changes for the last time, and from there try mash patterns until the state equals the segment's own
last frame (the toad placed in the next level).

    python mashtest.py <segment> [...]      prints old length vs the best pattern
"""
import json
import sys

from toads.emulator import BizHawk, LOGS_DIR


def key(m):
    return (m[0x3FD] | m[0x3EE] << 8, m[0x439], m[0x41B], m[0x475], m[0x51A], m[0x10])


PATTERNS = {
    "A even": lambda k: ("A",) if k % 2 == 0 else (),
    "A odd": lambda k: ("A",) if k % 2 == 1 else (),
    "Start even": lambda k: ("Start",) if k % 2 == 0 else (),
    "Start odd": lambda k: ("Start",) if k % 2 == 1 else (),
    "B even": lambda k: ("B",) if k % 2 == 0 else (),
    "A/Start": lambda k: (("A",), (), ("Start",), ())[k % 4],
    "A+Start even": lambda k: ("A", "Start") if k % 2 == 0 else (),
}


def main(seg):
    d = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    ins = [b.replace(",", "+") for b in d["inputs"]]
    e = BizHawk(log_name="mashtest.log")
    e.load(d["bookmark"])
    lv = e.byte(0x10)
    c = None
    saves = {}
    for i, b in enumerate(ins):
        if i % 100 == 0:
            saves[i] = e.msave()
        e.step(tuple(x for x in b.split("+") if x), 1)
        l = e.byte(0x10)
        if l != lv:
            c, lv = i, l
    last = key(e.ram(0, 0x800))
    n = len(ins)
    if c is None:
        print(seg, "no level change")
        e.close()
        return
    s0 = max(f for f in saves if f <= c)
    print(f"{seg}: {n} frames, level byte last changes at {c} (-> {lv}), old tail {n - c} frames; end key {last}", flush=True)
    for back in [int(v) for v in __import__('os').environ.get('MASH_BACK', '0,60').split(',')]:
        for name, pat in PATTERNS.items():
            if __import__('os').environ.get('MASH_PAT') and name not in __import__('os').environ['MASH_PAT'].split(','):
                continue
            s1 = max(f for f in saves if f <= max(0, c - back))
            e.mload(saves[s1])
            for b in ins[s1:max(s1, c - back)]:
                e.step(tuple(x for x in b.split("+") if x), 1)
            got = None
            for k in range(n - (c - back) + 60):
                e.step(pat(k), 1)
                if key(e.ram(0, 0x800)) == last:
                    got = c - back + k + 1
                    break
            print(f"   mash from {c - back:6d} {name:14s} -> {got}  ({'saves ' + str(n - got) if got else 'never'})", flush=True)
    e.close()


if __name__ == "__main__":
    for s in sys.argv[1:]:
        main(s)
