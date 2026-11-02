"""Bird (type 11) simulator in abs coordinates on the TAS's Ryu path (TAS dump) with inserted waits.
Ryu path P[t] = (X, y, fz) for TAS frames; bird state (B = abs x * 256, V = vel * 256, Y)."""
import sys; sys.path.insert(0, 'work/l51p')
from lib0 import *
def tas_path(t1, t2):
    out = {}
    for t in range(t1, t2 + 1):
        m = TM(t); X, y = XY(m); out[t] = (X, y, m[0x4C] >> 6 & 1)
    return out
def tas_bird(t, j=7):
    m = TM(t); X, y = XY(m); scr = (m[0x52]-256 if m[0x52] >= 128 else m[0x52])*256 + m[0x51]
    v = m[0x450+j]*256 + m[0x448+j]; v = v - 65536 if v >= 32768 else v
    return (scr + m[0x460+j])*256 + m[0x458+j], v, m[0x480+j]
def step(b, X, y, fz):
    B, V, Y = b
    if fz: return b
    Y = Y + 1 if y >= Y else Y - 1
    V = V - 16 if (B >> 8) >= X else V + 16
    return (B + V, V, Y)
def run(b, path, t1, t2, waits=(), rec=None):
    """advance from 'after TAS-eq t1' to t2; waits = [(t, w)]: Ryu stands still w frames before TAS frame t."""
    wd = dict(waits); X0 = None
    for t in range(t1 + 1, t2 + 1):
        if t in wd:
            Xp, yp, _ = path[t - 1]
            for _ in range(wd[t]):
                b = step(b, Xp, yp, 0)
        X, y, fz = path[t]
        b = step(b, X, y, fz)
        if rec is not None: rec[t] = b
    return b
