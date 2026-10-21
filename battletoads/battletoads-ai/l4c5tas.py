"""Checkpoint 5 by the TAS's own inputs (2026-10-04): our sprint over the switchback matches the TAS's pixel for pixel until
we release Right at the landing (up6 frame 6824). From a frame s of ours apply the TAS's inputs from t0+1 on (ours at s == TAS at t0)
and see how far the toad stays on the TAS's track, whether the x-244 snowman and the barrier die.
    python l4c5tas.py  -> knowledge/l4c5_tas.json {bookmark L4c5_6800, inputs}, bookmark L4c5_tasend"""
import json, re, sys
from toads.emulator import BizHawk, LOGS_DIR
from l4tas import load_tas, conv
rows = {}
for l in open("tas/watch_1p_l4.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+) cp=(\d+)", l)
    if m: r = tuple(int(v) for v in m.groups()); rows[r[0]] = r
tas = load_tas()
seg = [x.replace(",", "+") for x in json.load(open(LOGS_DIR / "pbeam_L4nm.json"))["inputs"]]
def ours(f): return seg[f - 4733]
def legal(b): return tuple(v for v in b if not ((v == "Left" and "Right" in b) or (v == "Up" and "Down" in b)))
def tx(m): return m[0x3FD] | m[0x3EE] << 8
def foes(m): return [(hex(m[0x3C1 + q]), m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q], m[0x51A + q]) for q in range(2, 15) if m[0x3C1 + q] in (0x33, 0x3c, 0x3e)]
LANDSYNC = bool(__import__('os').environ.get('C5_LANDSYNC'))
e = BizHawk(log_name="l4c5tas.log")
e.load("L4c5_6800"); base = e.msave(); best = None
pairs = [(s, t) for s in range(6812, 6830, 2) for t in range(17216, 17236, 1)]
if len(sys.argv) > 1: pairs = [tuple(int(v) for v in a.split(",")) for a in sys.argv[1:]]
for s, t0 in pairs:
    e.mload(base); ins = []
    for f in range(6801, s + 1):
        e.step(tuple(v for v in ours(f).split("+") if v), 1); ins.append(ours(f))
    m = e.ram(0, 0x800); hp0 = m[0x51A]
    if abs(tx(m) - rows[t0][1]) > int(__import__("os").environ.get("C5_XTOL", 0)) or m[0x439] != rows[t0][2] or m[0x565] != tas[t0 + 1][1][0x565]: continue
    sync, kill, bar, hurt = 0, None, None, None
    for t in range(t0 + 1, 17720):
        b = "+".join(legal(conv(tas[t][0]))); e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b); m = e.ram(0, 0x800)
        r = rows[t]
        if LANDSYNC and r[3] == 0 and rows[t - 1][3] != 0:      # the TAS just landed: we run 1 px behind, so land first (repeat the input) and only then go on
            for _ in range(3):
                if m[0x475] == 0: break
                e.step(tuple(v for v in b.split("+") if v), 1); ins.append(b); m = e.ram(0, 0x800)
        if abs(tx(m) - r[1]) <= 3 and abs(m[0x439] - r[2]) <= 3: sync = t
        if m[0x51A] < hp0 and hurt is None: hurt = t
        for oid, x, h, hp in foes(m):
            if oid == '0x33' and 200 <= x <= 300 and hp == 0 and kill is None: kill = t
            if oid == '0x3c' and hp == 0 and bar is None: bar = t
        if hurt and bar is None: break
    print(f"s {s} t0 {t0}: in sync to {sync} (+{sync - t0}), snowman dead {kill}, barrier dead {bar}, hurt {hurt}; end toad {tx(m)},{m[0x439]} foes {foes(m)}", flush=True)
    if bar and not hurt and (best is None or bar < best[0]): best = (bar, s, t0, list(ins), e.msave())
    if not hurt and __import__('os').environ.get('C5_SAVEPART') and best is None:          # the pile reached, the barrier not yet dead: keep it for a throw scan
        e.save("L4c5_pile"); json.dump({"bookmark": "L4c5_6800", "inputs": ins, "s": s, "t0": t0}, open("knowledge/l4c5_pile.json", "w")); print("saved L4c5_pile", len(ins), flush=True)
if best:
    e.mload(best[4]); e.save("L4c5_tasend")
    json.dump({"bookmark": "L4c5_6800", "inputs": best[3], "s": best[1], "t0": best[2], "barrier_dead_tas": best[0]}, open("knowledge/l4c5_tas.json", "w"))
    print("saved knowledge/l4c5_tas.json", len(best[3]), "frames from 6800; barrier dead at TAS", best[0], "=", best[0] - best[2] + best[1], "ours")
e.close()
