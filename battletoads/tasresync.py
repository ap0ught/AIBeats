"""Legal re-sync to a TAS's RAM trajectory across a stretch where the TAS uses a banned input (Left+Right/Up+Down).

    python tasresync.py BOOKMARK TASLOG T0 [--span N] [--beam W] [--save NAME] [--out FILE]

BOOKMARK is our state synced with the TAS at the START of TAS frame T0 (the frame whose input is the first banned
one). Beam search over legal buttons; score each child by its distance to the TAS's RAM at the same frame (toad x/y/h,
speed, anim, camera, object slots). A child "matches" when the full gameplay RAM ($300-$6FF except the stack and
sound) equals the TAS's; we then check that the TAS's own inputs keep us in sync for 120 more frames. Writes the
legal input bridge to FILE (json) and saves bookmark NAME at the match."""
import argparse, json
from toads.emulator import BizHawk

NAMES = ["Right", "Left", "Down", "Up", "Start", "Select", "B", "A"]
def conv(b): return tuple(n for n, c in zip(NAMES, b) if c != ".")
def banned(b): return (b[0] != "." and b[1] != ".") or (b[2] != "." and b[3] != ".")

ACTIONS = [(), ("Right",), ("Left",), ("Up",), ("Down",), ("Right", "Up"), ("Right", "Down"), ("Left", "Up"),
           ("Left", "Down"), ("B",), ("A",), ("Right", "B"), ("Left", "B"), ("Right", "A"), ("Left", "A"), ("A", "B")]

def load(taslog):
    rows = {}
    for ln in open(taslog):
        f, b, h = ln.split(); rows[int(f[1:])] = (b, bytes.fromhex(h))
    return rows

def feat(m):
    x = m[0x3FD] | m[0x3EE] << 8
    return (x, m[0x41B], m[0x439], m[0x475], m[0x565], m[0x3B5], m[0x87] | m[0x88] << 8, m[0x89] | m[0x8A] << 8)

def dist(m, t):
    a, b = feat(m), feat(t)
    d = abs(a[0] - b[0]) + (0 if 0x41B in IGNORE else abs(a[1] - b[1])) + abs(((a[2] - b[2] + 128) & 255) - 128) + abs(a[3] - b[3]) * 0.5
    d += abs(a[4] - b[4]) * SPDW + (a[5] != b[5]) * 2 + abs(a[6] - b[6]) + abs(a[7] - b[7])
    # object slots 2..14: ids and positions
    for s in range(2, 15):
        if m[0x3C1 + s] != b and False: pass
        d += (m[0x3C1 + s] != t[0x3C1 + s]) * 3
        d += min(abs((m[0x3FD + s] | m[0x3EE + s] << 8) - (t[0x3FD + s] | t[0x3EE + s] << 8)), 20) * 0.2
    return d

IGNORE = set()
SPDW = 1 / 16
MASK = [i for i in range(0x300, 0x700)]
SLOT0 = False
def full_eq(m, t):
    if SLOT0:      # loose: the toad's own slot in every object table, the camera and the global timers
        if any(m[i] != t[i] for i in (0x0B, 0x0C, 0x87, 0x88, 0x89, 0x8A)): return False
        return all(m[a] == t[a] for a in range(0x3C1, 0x6FF, 15) if a not in IGNORE)
    return all(m[i] == t[i] for i in MASK if i not in IGNORE)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bookmark"); ap.add_argument("taslog"); ap.add_argument("t0", type=int)
    ap.add_argument("--span", type=int, default=90); ap.add_argument("--beam", type=int, default=40)
    ap.add_argument("--save", default=None); ap.add_argument("--out", default=None)
    ap.add_argument("--lag", type=int, default=1, help="TAS RAM row offset: RAM after applying input f is row f+lag")
    ap.add_argument("--ignore", default="", help="address ranges to ignore in the exact match, e.g. 41B-429,4C0-4CF")
    ap.add_argument("--verify", type=int, default=120)
    ap.add_argument("--spdw", type=float, default=1 / 16)
    ap.add_argument("--slot0", action="store_true", help="match only the toad's slot, camera and timers")
    a = ap.parse_args()
    global SPDW, SLOT0
    SPDW = a.spdw; SLOT0 = a.slot0
    for rng in filter(None, a.ignore.split(",")):
        lo, hi = (int(v, 16) for v in rng.split("-"))
        IGNORE.update(range(lo, hi + 1))
    rows = load(a.taslog)
    e = BizHawk(log_name="tasresync.log")
    e.load(a.bookmark)
    beam = [(0.0, e.msave(), [])]
    found = None
    for d in range(a.span):
        f = a.t0 + d
        target = rows[f + a.lag][1]
        kids = []
        for score, sid, path in beam:
            for act in ACTIONS:
                e.mload(sid)
                e.step(act, 1)
                m = e.ram(0, 0x800)
                if full_eq(m, target):
                    # confirm: TAS inputs from f+1 keep us in sync
                    ok = True
                    for g in range(f + 1, f + 1 + a.verify):
                        b = rows[g][0]
                        if banned(b): break
                        e.step(conv(b), 1)
                        mm = e.ram(0, 0x800); tt = rows[g + a.lag][1]
                        if feat(mm)[:1] + feat(mm)[2:] != feat(tt)[:1] + feat(tt)[2:]: ok = False; break
                    if ok:
                        found = (f, path + ["+".join(act)])
                        break
                    e.mload(sid); e.step(act, 1)
                kids.append((score + dist(m, target), e.msave(), path + ["+".join(act)]))
            if found: break
        for _, sid, _ in beam: e.mfree(sid)
        if found: 
            for _, sid, _ in kids: e.mfree(sid)
            break
        kids.sort(key=lambda k: k[0])
        for _, sid, _ in kids[a.beam:]: e.mfree(sid)
        beam = kids[:a.beam]
        if d % 5 == 0:
            print(f"d{d} f{f} best {beam[0][0]:.1f} feat {feat(e.ram(0,0x800))} tas {feat(target)} path {beam[0][2][-6:]}", flush=True)
    if found:
        f, path = found
        print(f"MATCH at TAS frame {f} after {len(path)} legal frames: {path}", flush=True)
        # rebuild state at the match and save
        e.load(a.bookmark)
        for b in path: e.step(tuple(v for v in b.split("+") if v), 1)
        if a.save: e.save(a.save)
        if a.out: json.dump({"bookmark": a.bookmark, "tas_frame": f, "inputs": path}, open(a.out, "w"))
    else:
        print("no exact match within span", flush=True)
    e.close()

if __name__ == "__main__":
    main()
