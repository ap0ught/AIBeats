"""Replay queen segments from their entry bookmarks and print the fight/ending timeline of each:
hit times ($586 +12), the kill (7e -> 46), where she was, the body's despawn (7e back, countdown starts), the rise, cut 1.
    python l13z_tailstat.py <segment>...     (dumps logs/fix/l13z_ts_<segment>.bin = RAM per input from 0)"""
import json, sys
from toads.emulator import BizHawk, LOGS_DIR, STATES_DIR
bt = lambda s: tuple(b for b in s.split("+") if b)
e = BizHawk(log_name="l13z_tailstat.log")
for seg in sys.argv[1:]:
    j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
    if not (STATES_DIR / f"{j['bookmark']}.State").exists():
        print(seg, "bookmark missing", j["bookmark"], flush=True); continue
    e.load(j["bookmark"])
    out = open(LOGS_DIR / "fix" / f"l13z_ts_{seg}.bin", "wb")
    hits, prevc, kill, back, zero, top, cut = [], 0, None, None, None, None, None
    pq = None
    for n, b in enumerate(j["inputs"], 1):
        e.step(bt(b), 1)
        r = e.ram_all(); out.write(r)
        c = r[0x586]
        q = next(((s, r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s]) for s in range(2, 15) if r[0x3C1 + s] == 0x7E), None)
        body = next(((s, r[0x3FD + s] + 256 * r[0x3EE + s], r[0x439 + s]) for s in range(2, 15) if r[0x3C1 + s] == 0x46), None)
        if kill is None and c > prevc:
            hits.append((n, c, pq[1:] if pq else None, (r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x3B5])))
        if kill is None and body and not q and c >= 240:
            kill = (n, body[1:], pq[1:] if pq else None, (r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x3B5]))
        if kill and back is None and q:
            back = (n, c, q[1:])
        if back and zero is None and c == 0:
            zero = n
        if zero and top is None and q and q[2] == 156:
            top = n
        if r[0x10] != 13:
            cut = n; break
        prevc = c; pq = q or pq
    out.close()
    print(f"== {seg} (from {j['bookmark']}, {len(j['inputs'])} inputs)")
    print("  hits:", " ".join(f"{n}" for n, c, qq, t in hits))
    print("  gaps:", " ".join(str(hits[i][0] - hits[i - 1][0]) for i in range(1, len(hits))))
    print("  last hits (n, ctr, queen x,h, toad x,h,anim):", hits[-3:])
    print(f"  kill {kill}  body gone/7e back {back}  countdown 0 at {zero}  top at {top}  cut1 at {cut}")
    if kill and back and cut:
        print(f"  20th->kill {kill[0] - hits[-1][0]}  kill->back {back[0] - kill[0]}  back->zero {zero - back[0]}  zero->top {top - zero}  top->cut {cut - top}  kill->cut {cut - kill[0]}", flush=True)
e.close()
