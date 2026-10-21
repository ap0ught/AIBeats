"""Level 3's last stretch and the tunnel skip chosen TOGETHER (2026-10-02): not every arrival at the bikes lets the
skip fire (it needs the right camera position and speed), so take the T3 arrivals in order of time and run the
skip scan from each until one works; keep the fastest total.

    L3F_TAG=u python l3end.py   (needs knowledge/l3<TAG>_C.json + bookmark L3<TAG>_C from l3fight.py)
    -> logs/pbeam_L3<TAG>.json (to the bikes, bookmark = l3fight's root), logs/pbeam_L3skip<TAG>.json, bookmark L3skip<TAG>_end
"""
import itertools
import json
import os

from toads.emulator import BizHawk
from l3fight import Line, tx, alive, ROOT, TAG
from skip3_tas import tas_seq


def skip_scan(e, sk, lives0):
    """from the current emulator state (at the bikes): (inputs, frames) of the fastest working skip or None"""
    root = e.msave()
    best = None
    for nright, nleft in itertools.product((12, 8, 16), range(28, 48, 2)):
        e.mload(root)
        pre = []
        for _ in range(30):
            m = e.ram(0, 0x800)
            if abs(m[0x41B] - 218) <= 1:
                break
            b = "Down" if m[0x41B] < 218 else "Up"
            e.step((b,), 1)
            pre.append(b)
        ok = False
        for b in tas_seq(nright, nleft=nleft):
            m = e.ram(0, 0x800)
            if (m[0xB7] | m[0xB8] << 8) < 0x800:
                ok = True
                break
            e.step(tuple(v for v in b.split("+") if v), 1)
            pre.append(b)
        if not ok:
            continue
        r2 = e.msave()
        for s in range(0, 16):
            e.mload(r2)
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
            if end and got and m[0x11] == lives0 - 1 and (best is None or len(pre) + end < len(best)):
                best = pre + post[:end]
        e.mfree(r2)
        if best:
            break                                           # other dive timings differ by a frame or two at most
    e.mfree(root)
    return best


def main():
    e = BizHawk(log_name="l3end.log")
    sk = json.load(open("logs/pbeam_L3skip.json"))["inputs"]
    L = Line(e)
    L.ins = json.load(open(f"knowledge/l3{TAG}_C.json"))
    e.load(f"L3{TAG}_C")
    m = L.ram()
    lives0, hp0 = m[0x11], m[0x51A]
    mk = L.mark()
    arrivals = {}
    for n, k, a, yt in itertools.product((0, 2, 4, 8, 12, 16), range(0, 44, 4), (0, 1, 8, 16, 30), (212, 215, 218)):
        L.back(mk)
        L.idle_until_free()
        L.st("", n)
        L.st("Right")
        L.st("")
        m = L.st("Right")
        if m[0x565] < 160:
            continue
        got = None
        j = 0
        for _ in range(160):
            m = L.ram()
            v = "+Down" if m[0x41B] < yt - 1 else "+Up" if m[0x41B] > yt + 1 else ""
            if j == k and a:
                m = L.st("Right+A" + v, a)
            else:
                m = L.st("Right" + v)
            j += 1
            if not alive(m, lives0, hp0):
                break
            if tx(m) >= 1677 and any(m[0x3C1 + s] == 0x18 for s in range(1, 15)) and m[0x439] == 64:
                got = len(L.ins)
                break
        if got:
            key = (tx(m), m[0x41B], m[0x565], m[0x87] | m[0x88] << 8, m[0x0B])
            if key not in arrivals or got < arrivals[key][0]:
                arrivals[key] = (got, list(L.ins), (n, k, a, yt))
    order = sorted(arrivals.items(), key=lambda kv: kv[1][0])
    print(len(order), "distinct arrivals; fastest", order[0][1][0] if order else None, flush=True)
    best = None
    for key, (got, ins, par) in order[:40]:
        if got > order[0][1][0] + 16 or (best and got + 598 >= best[0]):
            break
        L.back(mk)
        for b in ins[mk[1]:]:
            L.st(b)
        sol = skip_scan(e, sk, lives0)
        print("arrival", got, par, key, "skip", sol and len(sol), flush=True)
        if sol and (best is None or got + len(sol) < best[0]):
            best = (got + len(sol), ins, sol)
    if not best:
        print("no arrival lets the skip fire")
        e.close()
        return
    L.back(mk)
    for b in best[1][mk[1]:]:
        L.st(b)
    e.save(f"L3{TAG}_bikes")
    for b in best[2]:
        e.step(tuple(v for v in b.split("+") if v), 1)
    e.save(f"L3skip{TAG}_end")
    json.dump({"bookmark": ROOT, "inputs": best[1],
               "note": "LEVEL 3 on foot, the TAS's way: every rat gets a flying attack and then the boot (dash + B) - two blows, "
                       "about 95 frames from the moment it drops in.||" + f"{len(best[1])} frames to the bikes"},
              open(f"logs/pbeam_L3{TAG}.json", "w"))
    json.dump({"bookmark": f"L3{TAG}_bikes", "inputs": best[2],
               "note": "TURBO TUNNEL SKIP: mount, roll back, dive into the gap before the first checkpoint; after the respawn the "
                       "bike crashes on the very frame the game's object pointer jumps into RAM, and the level ends.||" + f"{len(best[2])} frames"},
              open(f"logs/pbeam_L3skip{TAG}.json", "w"))
    print("saved: bikes at", len(best[1]), "+ skip", len(best[2]), "=", best[0])
    e.close()


if __name__ == "__main__":
    main()
