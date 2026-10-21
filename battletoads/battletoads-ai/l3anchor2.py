"""Turbo Tunnel skip from the NEW gauntlet (2026-10-02). What the skip needs (see journal 014): after the respawn
the bike must hit the wall at x~1152 on the very frame the level timer $0B wraps 255 -> 0 (the crash debris then
fills slots 3-5 before the loader walks RAM). The old inputs do that when the respawn happens at $0B = 189. From
bookmark L3n_anchor (new gauntlet, toad standing at the old route's anchor spot (1416, 218)) wait w frames, replay
the old approach and the old skip inputs, and report the respawn's $0B and whether the level ends.

    python l3anchor2.py   -> knowledge/l3_f4.json + logs/pbeam_L3skipn.json for the first w that works
"""
import json
import re

from toads.emulator import BizHawk


def tx(m):
    return m[0x3FD] | m[0x3EE] << 8


def main():
    def g(s, k):
        m = re.search(r"\b" + k + r"=(-?\d+)", s)
        return int(m.group(1)) if m else None
    lines = open("logs/newrun3.trace.txt").read().splitlines()
    F0 = None
    for ln in lines[5800:6268]:
        i, b, s = ln.split("\t")
        if g(s, "x") + 256 * g(s, "xh") == 1416 and g(s, "xspd") == 0 and g(s, "height") == 64:
            F0 = int(i)
    old = [l.rstrip("\n") for l in open("logs/newrun3.inputs.txt") if not l.startswith("#")]
    tail = [b.replace(",", "+") for b in old[F0:6268]]
    sk = json.load(open("logs/pbeam_L3skip.json"))["inputs"]
    e = BizHawk(log_name="l3anchor.log")
    e.load("L3n_anchor")
    m = e.ram(0, 0x800)
    print("anchor: toad", tx(m), m[0x41B], "timers", m[0x0B], m[0x0C], "tail", len(tail), flush=True)
    root = e.msave()
    for w in range(0, 520):
        e.mload(root)
        e.step((), w)
        for b in tail:
            e.step(tuple(v for v in b.split("+") if v), 1)
        m = e.ram(0, 0x800)
        at = (tx(m), m[0x41B], m[0x0B], m[0x0C])
        resp = None
        end = None
        for k, b in enumerate(sk):
            e.step(tuple(v for v in b.split("+") if v), 1)
            m = e.ram(0, 0x800)
            if resp is None and (m[0xB7] | m[0xB8] << 8) < 0x800:
                resp = (k, m[0x0B], m[0x0C])
            if m[0x10] != 3:
                end = k
                break
        print("wait", w, "at bikes", at, "respawn (k, 0B, 0C)", resp, "level ends at", end, flush=True)
        if end is not None:
            e.mload(root)
            ins = [""] * w + tail
            for b in ins:
                e.step(tuple(v for v in b.split("+") if v), 1)
            e.save("L3n_f4")
            json.dump(ins, open("knowledge/l3_f4_anchor.json", "w"))
            print("saved: f4 from the anchor =", len(ins), "frames")
            break
    e.close()


if __name__ == "__main__":
    main()
