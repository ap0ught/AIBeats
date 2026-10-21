"""Track K2: final check of a K7 candidate (complete Level 6 inputs from the bookmark, e.g. logs/fix/u17k_pick_B_21_6_1797.json):
one-piece replay from B4_end0 AND from L4c5_end0 against K6 from the same bookmark; placement on the last input; end state =
K6's (level 7, toad position, hp 47, lives 2, score 091600); min hp 47; no Start / Select / Left+Right / Up+Down.
Writes logs/pbeam_<out>.json (bookmark B4_end0) and states/<out>_end0b.State.     python u17k_verify.py <out> <json>"""
import hashlib, json, os, sys
from u17k_lib import *

out, new = sys.argv[1], json.load(open(sys.argv[2]))["inputs"]
k6 = seg("K6")
logf = open(FIX / f"u17k_verify_{out}.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True); logf.write(s + "\n"); logf.flush()


def toad(m):
    return dict(level=m[0x10], x=m[0x3FD] | m[0x3EE] << 8, H=m[0x439] | m[0x42A] << 8, z=m[0x475], hp=m[0x51A], lives=m[0x11],
                score="".join(str(d) for d in m[0x5F4:0x5FA]))


def replay(e, bm, ins, tag):
    e.load(bm)
    stage, placed, minhp, room2 = 0, None, 99, None
    for n, b in enumerate(ins, 1):
        e.step(bt(b), 1)
        m = e.ram(0, 0x800)
        lv, hp, x = m[0x10], m[0x51A], m[0x3FD] | m[0x3EE] << 8
        if lv == 8 and n > 300:
            minhp = min(minhp, hp)
        if room2 is None and n > 1700 and x == 76 and (m[0x439] | m[0x42A] << 8) < 7600:
            room2 = n
        if stage == 0 and lv == 7:
            stage = 1
        if stage == 1 and hp == 0 and x == 0:
            stage = 2
        if stage == 2 and hp > 0 and x > 0 and placed is None:
            stage, placed = 3, n
    m = bytes(e.ram(0, 0x800))
    log(f"{tag} from {bm}: {len(ins)} inputs, toad in room 2 at {room2}, Level 8 placement at input {placed}, min hp {minhp}, end {toad(m)}")
    return m, placed, minhp


bad = banned(new)
cnt = {k: sum(k in b for b in new) for k in ("Start", "Select")}
log(f"candidate: {len(new)} inputs (K6 {len(k6)}: saves {len(k6) - len(new)}); banned presses {len(bad)}; Start {cnt['Start']}, Select {cnt['Select']}; "
    f"first index differing from K6: {next(i for i in range(len(new)) if new[i] != k6[i])}; inputs sha1 {hashlib.sha1(chr(10).join(new).encode()).hexdigest()}")
e = BizHawk(log_name=f"u17k_verify_{out}.log")
ok = not bad and cnt["Start"] == 0
for bm in ("B4_end0", "L4c5_end0"):
    m_ref, p_ref, hp_ref = replay(e, bm, k6, "K6")
    m_new, p_new, hp_new = replay(e, bm, new, out)
    diff = [hex(i) for i in range(0x800) if m_ref[i] != m_new[i]]
    a, b_ = toad(m_ref), toad(m_new)
    good = p_new == len(new) and a == b_ and hp_new == 47 and b_["hp"] == 47 and b_["lives"] == 2 and b_["score"] == "091600" and b_["level"] == 7
    log(f"  RAM bytes differing from K6's end state: {len(diff)} {diff[:20]}; placement on the last input {p_new == len(new)}; OK {good}")
    ok = ok and good
    if bm == "B4_end0" and good:
        e.save(out + "_end0b")
log(f"VERIFIED {ok}: frames saved vs K6 {len(k6) - len(new)}")
if ok:
    note = json.load(open(LOGS_DIR / "pbeam_K6.json")).get("note", "")
    p = LOGS_DIR / f"pbeam_{out}.json"
    if p.exists():
        os.replace(p, str(p) + ".backup")
    json.dump({"bookmark": "B4_end0", "inputs": new, "note": note, "rerolls": [], "slack": 0}, open(str(p) + ".tmp", "w"))
    os.replace(str(p) + ".tmp", p)
    log(f"wrote logs/pbeam_{out}.json (bookmark B4_end0) and states/{out}_end0b.State")
e.close()
