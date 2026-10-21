import time
from toads.emulator import BizHawk
e = BizHawk(log_name="l13z_bench.log")
e.load("L13z_y0_i960")
e.step((), 1)
sid = e.msave()
def t(label, fn, n):
    t0 = time.time(); fn(); dt = time.time() - t0
    print(f"{label}: {dt*1000/n:.3f} ms each ({n})", flush=True)
t("ping", lambda: [e.cmd("ping") for _ in range(2000)], 2000)
t("step1", lambda: [e.step((), 1) for _ in range(2000)], 2000)
t("step 2000 in one cmd", lambda: e.step((), 2000), 2000)
e.mload(sid)
t("mload", lambda: [e.mload(sid) for _ in range(500)], 500)
t("msave+mfree", lambda: [e.mfree(e.msave()) for _ in range(500)], 500)
t("ram_all", lambda: [e.ram_all() for _ in range(500)], 500)
t("ram 16", lambda: [e.ram(0x3C1, 16) for _ in range(500)], 500)
def ev():
    for _ in range(300):
        e.mload(sid)
        for _ in range(4): e.step(("A",), 1)
        e.ram_all()
t("eval (mload + 4x step + ram_all)", ev, 300)
e.frameskip(9)
t("frameskip9 step 2000 in one cmd", lambda: e.step((), 2000), 2000)
t("frameskip9 eval", ev, 300)
print(e.cmd("apikeys memorysavestate"))
print(e.cmd("apikeys client")[:1500])
e.close()
