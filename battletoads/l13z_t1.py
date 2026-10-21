import hashlib, json
import l13z_beam as zb
e = zb.Emu(log_name="l13z_t1.log")
ins = json.load(open("logs/pbeam_L13y0.json"))["inputs"][:200]
bt = lambda s: tuple(b for b in s.split("+") if b)
# B: load + plain steps
e.load("L12g_end0")
r0 = e.ram_all()
for b in ins: e.step(bt(b), 1)
hB = hashlib.sha1(e.ram_all()).hexdigest()
# A: load, msave at once, mload, steps
e.load("L12g_end0")
sid = e.msave()
e.step((), 50)
e.mload(sid)
r1 = e.ram_all()
for b in ins: e.step(bt(b), 1)
hA = hashlib.sha1(e.ram_all()).hexdigest()
# C: via xp in chunks of 2 frames
e.mload(sid)
cur = sid
for i in range(0, 200, 2):
    act = tuple((b.replace("+", ",") or "-") for b in ins[i:i + 2])
    res = e.xp(cur, [act], save=True)
    cur = res[0][0]
e.mload(cur)
hC = hashlib.sha1(e.ram_all()).hexdigest()
print("plain", hB[:10], "msave-after-load", hA[:10], "xp chain", hC[:10], "ram after load equal:", r0 == r1, flush=True)
f = e.feat(); print("feat", f.lvl, f.ctr, f.tx, f.th, f.qid, f.qx, f.qh, f.hits)
e.close()
