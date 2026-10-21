"""From L3_skip_respawn, apply an input list and trace the object pointer walk; stop when object 0x7F spawns."""
import sys
from toads.emulator import BizHawk

def trace(e, seq, n=700, verbose=True):
    e.load("L3_skip_respawn")
    prev = None
    for k in range(n):
        r = e.ram_all()
        ptr = r[0xB7] | r[0xB8] << 8
        ids = [r[0x3C1 + i] for i in range(8)]
        if 0x7F in ids:
            if verbose: print(f"k{k} 0x7F SPAWNED ptr {ptr:04X} ids {ids}")
            return k
        if ptr != prev and verbose:
            print(f"k{k:4d} ptr {ptr:04X} 0B {r[0x0B]:3d} 0C {r[0x0C]:3d} cam {r[0x87]|r[0x88]<<8:5d} x {r[0x3FD]:3d} y {r[0x41B]:3d} "
                  f"st {r[0x3B5]:3d} lvl {r[0x10]} ids {ids} desc {list(r[ptr:ptr+11]) if ptr < 0x7F5 else '-'}")
        prev = ptr
        if r[0x10] != 3: print("level changed", r[0x10]); return None
        b = seq[k] if k < len(seq) else ""
        e.step(tuple(v for v in b.split("+") if v), 1)
    return None

if __name__ == "__main__":
    e = BizHawk(log_name="skip3_trace.log")
    print("idle ->", trace(e, [], n=int(sys.argv[1]) if len(sys.argv) > 1 else 700))
    e.close()
