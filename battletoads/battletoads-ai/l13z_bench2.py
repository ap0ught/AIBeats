import json, sys, time, types
import toads.emulator as E
tweak = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
_loads = json.loads
def loads(s, *a, **k):
    d = _loads(s, *a, **k)
    if isinstance(d, dict) and "FrameSkip" in d:
        d.update(tweak)
    return d
E.json = types.SimpleNamespace(loads=loads, dumps=json.dumps)
E.BRIDGE_LUA = E.PROJECT / "l13z_bridge.lua"
e = E.BizHawk(log_name="l13z_bench2.log")
e.load("L13z_y0_i960"); e.step((), 1)
if "--fs" in sys.argv: e.frameskip(9)
t0 = time.time(); e.step((), 3000); dt = time.time() - t0
print(tweak, "fs" if "--fs" in sys.argv else "", f"{dt/3:.3f} ms/frame", flush=True)
e.load("L13z_y0_i960"); e.step((), 1)
e.cmd("xg " + ",".join(str(a) for a in [0x10, 0x11, 0x0B, 0x586]))
e.cmd("xs " + ",".join(str(a) for a in [0x3C1, 0x3FD, 0x439]))
e.cmd("xi 126,70")
sid = e.msave()
acts = "|".join(["A;A", "-;-", "Right;Right", "B;B", "Left,B;Left,B", "Select;Select", "Right,A;Right,A", "Left;Left", "Left,A;Left,A", "Right,B;Right,B"])
t0 = time.time()
ids = []
for _ in range(100):
    r = e.cmd(f"xp {sid} 1 {acts}")
    ids += [x.split(":")[0] for x in r.split("|")]
    if len(ids) >= 200:
        e.cmd("xfree " + ",".join(ids)); ids = []
dt = time.time() - t0
print(f"  xp: {dt*1000/1000:.3f} ms per eval (2-frame acts, save)", r[:120], flush=True)
e.close()
