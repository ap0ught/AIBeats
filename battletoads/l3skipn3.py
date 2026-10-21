"""Turbo Tunnel skip from the NEW gauntlet's arrival (bookmark L3n_f4, from l3chain.py). 2026-10-02.

Mechanism (journal 014): the respawn before the first checkpoint leaves the object-list pointer at $000B; 255
frames after the respawn's timer reset ($0B = $FF, $0C = $7F, $0D = 3) the "entry" is a jump to $037F and the
loader walks RAM 11 bytes per frame. The old (TAS-derived) post-respawn inputs ride the bike so that it crashes at
that moment; they only need to be re-aligned to the new respawn frame.

Pre-death part: line up in the lane (y 218), skip3_tas.tas_seq(12, nleft) until the pointer is in RAM. Then
`shift` idle frames, then the old skip's inputs from its respawn on (logs/pbeam_L3skip.json[182:]).

    python l3skipn3.py   -> logs/pbeam_L3skipn.json (bookmark L3n_f4), bookmark L3skipn_end
"""
import json

from toads.emulator import BizHawk
from skip3_tas import tas_seq


ROOT = __import__("os").environ.get("L3SKIP_ROOT", "L3n_f4")
OUT = __import__("os").environ.get("L3SKIP_OUT", "pbeam_L3skipn.json")


def main():
    e = BizHawk(log_name="l3skipn.log")
    sk = json.load(open("logs/pbeam_L3skip.json"))["inputs"]
    best = None
    for nright, nlu, nleft in __import__("itertools").product((12, 8, 16, 4, 0, 20), (11, 9, 13, 7, 15), range(20, 62, 2)):
        e.load(ROOT)
        lives0 = e.byte(0x11)
        pre = []
        for _ in range(30):
            m = e.ram(0, 0x800)
            if abs(m[0x41B] - 218) <= 1:
                break
            b = "Down" if m[0x41B] < 218 else "Up"
            e.step((b,), 1)
            pre.append(b)
        ok = False
        for b in tas_seq(nright, nlu=nlu, nleft=nleft):
            m = e.ram(0, 0x800)
            if (m[0xB7] | m[0xB8] << 8) < 0x800:
                ok = True
                break
            e.step(tuple(v for v in b.split("+") if v), 1)
            pre.append(b)
        if not ok:
            pass
            continue
        root = e.msave()
        for s in range(0, 16):
            e.mload(root)
            post = [""] * s + sk[182:] + [""] * 200
            got = end = None
            for k, b in enumerate(post):
                e.step(tuple(v for v in b.split("+") if v), 1)
                m = e.ram(0, 0x800)
                if got is None and 0x7F in m[0x3C1:0x3D0]:
                    got = k
                if m[0x10] != 3:
                    end = k + 1
                    break
            if end and got and m[0x11] == lives0 - 1:
                total = len(pre) + end
                print("nright", nright, "nlu", nlu, "nleft", nleft, "shift", s, "pre", len(pre), "0x7F at", got, "level ends at", end, "total", total, "lives", m[0x11], flush=True)
                if best is None or total < len(best):
                    best = pre + post[:end]
                    e.save(OUT.replace("pbeam_", "").replace(".json", "") + "_end")
        e.mfree(root)
    if best:
        json.dump({"bookmark": ROOT, "inputs": best,
                   "note": "TURBO TUNNEL SKIP from the new gauntlet: mount, roll back, dive into the gap before the first checkpoint; "
                           "after the respawn the bike crashes on the frame the loader's pointer jumps into RAM.||" + f"{len(best)} frames"},
                  open("logs/" + OUT, "w"))
        print("saved logs/" + OUT + ":", len(best), "frames (old skip: 598)")
    e.close()


if __name__ == "__main__":
    main()
