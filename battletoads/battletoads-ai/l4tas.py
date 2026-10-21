"""Replay TAS #5093's Level 4 inputs from our tunnel-end state and measure how long they stay in sync with the TAS's
own RAM (tas/ram_l4_1p.txt). Usage: python l4tas.py [shift ...]  (our step j applies TAS input 15267+shift+j)."""
import sys
from toads.emulator import BizHawk

NAMES = ["Right", "Left", "Down", "Up", "Start", "Select", "B", "A"]
def conv(b): return tuple(n for n, c in zip(NAMES, b) if c != ".")

def load_tas():
    rows = {}
    for ln in open("tas/ram_l4_1p.txt"):
        f, b, h = ln.split(); rows[int(f[1:])] = (b, bytes.fromhex(h))
    return rows

def key(m): return (m[0x3FD] | m[0x3EE] << 8, m[0x41B], m[0x439], m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8)

def run(e, rows, shift, n=1600, bm="L3skip_end"):
    e.load(bm)
    t0 = 15267 + shift
    first_bad = None; lvl4 = None
    for j in range(n):
        f = t0 + j
        if f not in rows: break
        e.step(conv(rows[f][0]), 1)
        m = e.ram(0, 0x800)
        if lvl4 is None and m[0x10] == 4: lvl4 = j
        # compare with the TAS's RAM on the frame whose input we just applied (+1 for the dump's timing)
        tm = rows.get(f + 1, (None, None))[1]
        if tm is not None and tm[0x10] == 4 and m[0x10] == 4 and key(m) != key(tm):
            first_bad = (j, f, key(m), key(tm)); break
    return lvl4, first_bad

if __name__ == "__main__":
    rows = load_tas()
    e = BizHawk(log_name="l4tas.log")
    for s in (int(a) for a in sys.argv[1:]) if len(sys.argv) > 1 else range(-3, 25):
        print(s, run(e, rows, s), flush=True)
    e.close()
