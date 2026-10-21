"""u16b: bridge throughput benchmark + bookmark semantics check against cap14.ram."""
import time, hashlib
from toads.emulator import BizHawk, LOGS_DIR
F = {"level": 0x10, "x": 0x3FD, "height": 0x439, "hh": 0x42A, "z": 0x475, "anim": 0x3B5, "hp": 0x51A, "lives": 0x11}
bt = lambda l: tuple(x for x in l.replace(",", "+").split("+") if x)
lines = [l for l in open(LOGS_DIR / "up14.inputs.txt").read().splitlines() if not l.startswith("#")]
R = open(LOGS_DIR / "cap14.ram", "rb")
def row(f):
    R.seek((f - 1) * 2048); return R.read(2048)
e = BizHawk(log_name="u16b_bench.log", fields=F)
s = e.load("early_L8_p0")
print("after load:", s, flush=True)
m = e.ram_all()
for f in range(12485, 12492):
    d = sum(1 for i in range(2048) if m[i] != row(f)[i])
    print("  ram vs cap14 row", f, "diff bytes", d)
# replay up14 from the bookmark for 200 frames and compare with cap14
bad = 0
for f in range(12489, 12689):
    e.step(bt(lines[f - 1]), 1)
    m = e.ram_all()
    d = sum(1 for i in range(2048) if m[i] != row(f)[i])
    if d and bad < 5:
        print("   frame", f, "diff", d); bad += 1
print("replay of up14 12489..12688 from the bookmark: mismatching frames", bad, flush=True)
sid = e.msave()
for fs in (0, 4, 9, 30):
    e.frameskip(fs)
    e.mload(sid)
    t = time.time()
    for _ in range(3000):
        e.step((), 1)
    a = 3000 / (time.time() - t)
    h1 = hashlib.sha1(e.ram_all()).hexdigest()[:8]
    e.mload(sid)
    t = time.time()
    e.step((), 3000)
    b = 3000 / (time.time() - t)
    h2 = hashlib.sha1(e.ram_all()).hexdigest()[:8]
    print(f"frameskip {fs}: single {a:.0f} fps, batch {b:.0f} fps, ram {h1} {h2}", flush=True)
e.close()
