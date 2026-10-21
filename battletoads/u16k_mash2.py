"""Track K: level-byte timeline of L6c's own warp (reference) and of variants behind K6's contact.
    python u16k_mash2.py -> logs/fix/u16k_mash2.txt"""
import json
from toads.emulator import BizHawk, LOGS_DIR

bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
old = json.load(open(LOGS_DIR / "pbeam_L6c.json"))["inputs"]
seg = json.load(open(LOGS_DIR / "pbeam_K6.json"))["inputs"]
best = json.load(open(LOGS_DIR / "fix" / "u16k_mash_best.json"))
e = BizHawk(log_name="u16k_mash2.log")
out = []


def timeline(pre, tail, label, c0):
    e.load("L4c5_end0")
    for b in pre:
        e.step(bt(b), 1)
    stage, ev, prev_lv, prev_rtn = 0, [], 8, None
    for j, b in enumerate(tail):
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        lv, hp, x, rtn, tm = m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8, m[0x23] | m[0x24] << 8, m[0x0B]
        if j == 0:
            ev.append(f"timer$0B={tm}")
        if rtn != prev_rtn and j < 60:
            ev.append(f"rtn{rtn:04X}@{j + 1}")
            prev_rtn = rtn
        if lv != prev_lv:
            ev.append(f"{prev_lv}->{lv}@{j + 1}(t{tm})")
            prev_lv = lv
        if stage == 0 and lv == 7:
            stage = 1
        if stage == 1 and hp == 0 and x == 0:
            stage = 2
            ev.append(f"blank@{j + 1}")
        if stage == 2 and hp > 0 and x > 0:
            ev.append(f"placed@{j + 1}")
            break
    out.append(f"{label} (contact at input {c0}): " + " ".join(ev))
    print(out[-1], flush=True)


timeline(old[:2378], old[2378:], "L6c own mash", 2378)
alt = lambda first, n=260: [(first if k % 2 == 0 else ("B" if first == "A" else "A")) for k in range(n)]
timeline(old[:2378], alt("A"), "L6c contact + A,B", 2378)
timeline(old[:2378], alt("B"), "L6c contact + B,A", 2378)
timeline(seg[:2286], best["tail"], "K6 contact + best tail", 2286)
timeline(seg[:2286], ["Right"] * 14 + best["tail"][14:], "K6 contact + Right x14 + best tail", 2286)
# K6 with the contact one portal check later (rj 94)
line94 = [""] * 94 + ["Right", ""] + ["Right+A"] * 171
timeline(old[:2022] + line94, alt("A"), "rj94 line + A,B from the end of the line", 2022 + len(line94))
timeline(old[:2022] + line94, alt("B"), "rj94 line + B,A from the end of the line", 2022 + len(line94))
open(LOGS_DIR / "fix" / "u16k_mash2.txt", "w").write("\n".join(out) + "\n")
e.close()
