"""L12h track: camera-height progress, ours (logs/fix/<tag>.ram) vs the 1-player TAS log (tas/watch_1p_l12.txt)."""
import re, sys
from toads.emulator import LOGS_DIR
tag = sys.argv[1]
buf = open(LOGS_DIR / "fix" / f"{tag}.ram", "rb").read(); N = len(buf) // 2048
ours = []
for i in range(N):
    m = buf[i * 2048:(i + 1) * 2048]
    if m[0x10] != 5: break
    c = m[0x89] | m[0x8A] << 8
    ours.append(c - 65536 if c > 60000 else c)
tas = []; t0 = None; ev = []
pf = set()
for l in open("tas/watch_1p_l12.txt"):
    if " x=" not in l: continue
    f = int(l.split()[0][1:])
    if f < 69574: continue
    mm = re.search(r" x=(-?\d+) h=(-?\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", l)
    x, h, z, st, an, hp, cam, camy = map(int, mm.groups())
    if t0 is None and x == 136 and h == 30 and camy == 5888: t0 = f
    if t0 is None: continue
    camy = camy - 65536 if camy > 60000 else camy
    tas.append(camy)
    o = l.split("|")[1] if "|" in l else ""
    nf = " 60:" in o
    if nf and 60 not in pf: ev.append((f - t0, "face spawn camy %d" % camy)); pf.add(60)
    if not nf and 60 in pf: ev.append((f - t0, "face gone")); pf.discard(60)
    np_ = an in (94, 95, 96)
    if np_ and 'p' not in pf: ev.append((f - t0, "pole grab x=%d camy %d" % (x, camy))); pf.add('p')
    if not np_ and 'p' in pf: ev.append((f - t0, "pole leave")); pf.discard('p')
print("TAS placement frame", t0, "TAS rows", len(tas), "ours rows", len(ours))
for e in ev: print("TAS", e)
print("cam  ours  tas  diff")
for thr in list(range(5850, -50, -100)) + [2048, 1512, 1112, 1056, 0, -20]:
    a = next((i for i, c in enumerate(ours) if c <= thr), None); b = next((i for i, c in enumerate(tas) if c <= thr), None)
    print(thr, a, b, (a - b) if a is not None and b is not None else None)
