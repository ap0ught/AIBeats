"""Frame-by-frame comparison around the corridor-floor landing (old 8456..8482): our run after the join (bookmark) vs the old run.
x.sub, H, z, speed, anim, flags, $0B."""
import sys
from l9heli_fix_lib import *
R = cap(); ins = up14_inputs()
e = BizHawk(log_name="l9heli_fix_p13.log"); e.load(sys.argv[1])
for k in range(8280, 8484):
    b = ins[OFF + k - 1]; e.step(bt(b), 1)
    if k >= 8456:
        m = e.ram(0, 0x800); ref = bytes(R[OFF + k - 1])
        f = lambda m: f"x {m[0x3FD] | m[0x3EE] << 8}.{m[0x448]:3d} H {m[0x439] | m[0x42A] << 8}.{m[0x466]:3d} z {m[0x475]} spd {m[0x565]:3d} an {m[0x3D0]:2d}/{m[0x3DF]:3d} f {m[0x4A2]:3d} vy {m[0x4C0]},{m[0x4CF]:3d} t {m[0x0B]:3d}"
        print(k, repr(b).ljust(12), "ours", f(m), "| old", f(ref), "" if f(m)[:40] == f(ref)[:40] else "  <<<", flush=True)
e.close()
