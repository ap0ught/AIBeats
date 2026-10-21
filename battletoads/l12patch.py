"""The Revolution: replay FODA's 1P TAS inputs (they sync exactly in BizHawk with a 1-frame shift) and patch each
banned Left+Right / Up+Down stretch with legal inputs found by a small exact-state search.
Our step s applies tas[s+1]; after step s our state is compared with the TAS log row s+1."""
import json, re, sys, time
from toads.emulator import BizHawk, PROJECT
rows = []
for ln in open(PROJECT / "tas" / "watch_1p_l12.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=(\d+) an=(\d+) hp=(\d+) cam=(\d+) camy=(\d+)", ln)
    if m: rows.append(tuple(int(v) for v in m.groups()))
pl = next(i for i, r in enumerate(rows) if r[1] == 136 and r[2] == 30); rows = rows[pl:]
TAS = [tuple(b for b in s.split("+") if b) for s in json.load(open(PROJECT / "knowledge" / "tas1p_l12_inputs.json"))]
ILLEGAL = lambda b: ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)
LEGAL = [(), ("Left",), ("Right",), ("A",), ("Left", "A"), ("Right", "A"), ("B",), ("Left", "B"), ("Right", "B"),
         ("Down",), ("Down", "Left"), ("Down", "Right"), ("Down", "Left", "A"), ("Down", "Right", "A"), ("Up",)]

def st(r):
    return (r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x475], r[0x3B5])

def tas_row(s):                     # (x, h, z, an) of the TAS after our step s
    r = rows[s + 1]; return (r[1], r[2], r[3], r[5])

def score(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) + (4 if a[2] != b[2] else 0) + (4 if a[3] != b[3] else 0)

def patch(e, s0, s1, width=300):
    """legal inputs for steps s0..s1 (inclusive) ending in the TAS's state after s1 (and matching each step if possible)"""
    root = e.msave(); layer = [(0, [], root)]
    for s in range(s0, s1 + 1):
        nxt = {}
        for sc, seq, sid in layer:
            for b in LEGAL:
                e.mload(sid); e.step(b, 1); q = st(e.ram_all()); r = e.ram_all()
                key = q + (r[0x448], r[0x565], r[0x4A2])
                c = score(q, tas_row(s)) * (1 if s == s1 else 0.25) + sc
                if key in nxt and nxt[key][0] <= c: continue
                nxt[key] = (c, seq + [b], None, sid, b)
        best = sorted(nxt.values(), key=lambda t: t[0])[:width]
        new = []
        for c, seq, _, psid, b in best:
            e.mload(psid); e.step(b, 1); new.append((c, seq, e.msave()))
        for _, _, sid in layer:
            if sid != root: e.mfree(sid)
        layer = new
    c, seq, sid = layer[0]
    e.mload(sid)
    return seq, st(e.ram_all()), tas_row(s1)

if __name__ == "__main__":
    upto = int(sys.argv[1]) if len(sys.argv) > 1 else 2300
    K, M = int(sys.argv[2]) if len(sys.argv) > 2 else 4, int(sys.argv[3]) if len(sys.argv) > 3 else 8
    e = BizHawk(log_name="l12patch.log"); e.load("L12_start")
    out = []; s = 0; synced_to = 0
    while s < upto and s + 1 < len(TAS):
        if ILLEGAL(TAS[s + 1 + K]) if s + 1 + K < len(TAS) else False:
            a = s + K                                  # the first illegal step index is s+K (applies TAS[s+K+1])
            b = a
            while b + 1 + 1 < len(TAS) and (ILLEGAL(TAS[b + 2]) or ILLEGAL(TAS[b + 3]) or ILLEGAL(TAS[b + 4])): b += 1
            s1 = b + M
            t0 = time.time()
            seq, got, want = patch(e, s, s1)
            out += ["+".join(x) for x in seq]
            print(f"patch steps {s}..{s1} ({s1 - s + 1} f): got {got} want {want} ({time.time() - t0:.0f}s)", flush=True)
            s = s1 + 1
            continue
        e.step(TAS[s + 1], 1); out.append("+".join(TAS[s + 1]))
        q = st(e.ram_all())
        if q != tas_row(s):
            print(f"desync at step {s}: ours {q} TAS {tas_row(s)}", flush=True); break
        synced_to = s; s += 1
    print("synced through step", synced_to, "of", upto, flush=True)
    (PROJECT / "knowledge" / "l12_tas_patched.json").write_text(json.dumps(out))
    e.save("L12_patched"); e.close()
