"""Last scene forensics: object table every N frames from the tower's return to the T. Bird cut, for a few toad positions."""
import json, sys
import l13z_beam as zb
from toads.emulator import LOGS_DIR
seg, n0 = sys.argv[1], int(sys.argv[2])
xs = [int(v) for v in sys.argv[3].split(",")]
step = int(sys.argv[4]) if len(sys.argv) > 4 else 10
j = json.load(open(LOGS_DIR / f"pbeam_{seg}.json"))
ins = j["inputs"]
e = zb.Emu(log_name="l13z_tail3.log")
e.load(j["bookmark"])
for b in ins[:n0]:
    e.step(tuple(v for v in b.split("+") if v), 1)
base = e.msave()
for x in xs:
    e.mload(base)
    n = n0; phase = 0; k = 0; f = e.feat()
    print(f"==== toad to x {x}")
    while n < n0 + 2600:
        b = ("Right" if f.tx < x - 1 else ("Left" if f.tx > x + 1 else "")) if phase == 0 else (("A" if k % 2 == 0 else "") if phase == 1 else "")
        f = e.xp(None, [((b or "-"),)])[0][1]
        n += 1; k += 1
        if phase == 0 and f.lvl != 13: phase = 1; k = 0; print("cut1", n)
        elif phase == 1 and f.lvl == 13: phase = 2; k = 0; print("tower", n)
        elif phase == 2 and f.lvl == 254: print("tbird", n, "scene", k); break
        if phase == 2 and (k % step == 0 or k < 3):
            r = e.ram_all()
            o = " ".join(f"[{s}:{r[0x3C1+s]:02x} x{r[0x3FD+s]+256*r[0x3EE+s]} h{r[0x439+s]} y{r[0x41B+s]} z{r[0x475+s]} a{r[0x3B5+s]} s{r[0x4B1+s]} c{r[0x583+s]} e{r[0x4DE+s]}/{r[0x4ED+s]} p{r[0x592+s]} k{r[0x565+s]}]" for s in range(15) if r[0x3C1+s])
            print(k, "0B", r[0x0B], "rng", r[0x25:0x29].hex(), "23/24", f"{r[0x23]:02x}{r[0x24]:02x}", o)
e.close()
