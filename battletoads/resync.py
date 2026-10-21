"""Re-sync with the 1P TAS (The Revolution): from a bookmark (+2 idle), try short legal prefixes (walk, turn,
double-tap sprint, jump with A held k frames, drift) and, at every frame, look for an exact match with a TAS frame j
(x, raw h, z, anim) in [jlo, jhi]; from a match, replay the TAS's own inputs j+1..jcheck and keep the result if our
position at jcheck equals the TAS's (within tol). Prints the best (fewest frames to jcheck).
    python resync.py <bookmark> <jlo> <jhi> <jcheck> [dir R|L] [maxa] [out.json]"""
import json, re, sys, itertools
from toads.emulator import BizHawk, PROJECT
rows, objs = [], []
for ln in open(PROJECT / "tas" / "watch_1p_l12.txt"):
    m = re.match(r"f(\d+) x=(\d+) h=(\d+) z=(\d+) st=\d+ an=(\d+).*?\| ?(.*)", ln)
    if m:
        rows.append(tuple(int(v) for v in m.groups()[:5]))
        objs.append([(int(o[:2], 16),) + tuple(int(v) for v in o[3:].split(",")[:2]) for o in m.group(6).split() if ":" in o])
pl = next(i for i, r in enumerate(rows) if r[1] == 136 and r[2] == 30); rows = rows[pl:]; objs = objs[pl:]
TAS = [tuple(b for b in s.split("+") if b) for s in json.load(open(PROJECT / "knowledge" / "tas1p_l12_inputs.json"))]
ILL = lambda b: ("Left" in b and "Right" in b) or ("Up" in b and "Down" in b)

def st(r): return (r[0x3FD] + 256 * r[0x3EE], r[0x439], r[0x475], r[0x3B5], r[0x51A], r[0x11])

def prefixes(D, O, maxa):
    """legal prefixes toward direction D (O = the opposite): position first, then run/jump"""
    N = ()
    DA = D + ("A",)
    for pos, a in itertools.product(("wait", "toD", "toO"), range(0, maxa + 1, 2)):
        if pos == "wait" and a > 40: continue
        move = [N] * a if pos == "wait" else ([D] * a if pos == "toD" else [O] * a)
        for run in ("hold", "tap", "turntap"):
            r = [] if run == "hold" else ([D, N, D] if run == "tap" else [D] + [N] * 5 + [D, N, D])
            for c in (0, 2, 4, 8, 12, 16, 24):
                for k in (0, 4, 8, 12, 16, 21):
                    yield move + r + [D] * c + [DA] * k + [D] * 40
                    if k and run != "hold":                     # the dash jump: a release frame before direction+A keeps the sprint speed
                        yield move + r + [D] * c + [N] + [DA] * k + [D] * 40

def objsig(lst, oc):
    """sorted x of objects of type oc[0] with height in [oc[1], oc[2]]"""
    return tuple(sorted((x, h) for t, x, h in lst if t == oc[0] and oc[1] <= h <= oc[2]))

def run(bm, jlo, jhi, jcheck, dirc="R", maxa=40, tol=0, objcheck=None, save=None, stop_first=False, idle=True, extend=True):
    D, O = (("Right",), ("Left",)) if dirc == "R" else (("Left",), ("Right",))
    e = BizHawk(log_name=f"resync_{bm}.log"); e.load(bm)
    if idle:
        e.step((), 2)
    root = e.msave(); best = None; tried = set()
    idx = {}
    for j in range(jlo, jhi + 1):
        idx.setdefault((rows[j][1], rows[j][2], rows[j][3], rows[j][4]), []).append(j)
    for pre in prefixes(D, O, maxa):
        e.mload(root); seq = []
        for i, b in enumerate(pre):
            e.step(b, 1); seq.append(b); q = st(e.ram_all())
            if q[4] < 47 or q[5] < 6: break
            for j in idx.get(q[:4], []):
                if any(ILL(TAS[s]) for s in range(j + 1, jcheck + 1)): continue
                if objcheck:                                  # a moving platform must be where the TAS had it
                    r = e.ram_all()
                    ours = objsig([(r[0x3C1 + k], r[0x3FD + k] + 256 * r[0x3EE + k], r[0x439 + k]) for k in range(2, 15)], objcheck)
                    if ours != objsig(objs[j], objcheck): continue
                key = (tuple(seq), j)
                if key in tried: continue
                tried.add(key)
                tot = len(seq) + (jcheck - j)
                if best and tot >= best[0]: continue
                sid = e.msave(); ok = True
                for s in range(j + 1, jcheck + 1):
                    e.step(TAS[s], 1); qq = st(e.ram_all())
                    if qq[4] < 47 or qq[5] < 6: ok = False; break
                qq = st(e.ram_all()); t = rows[jcheck]
                oe = __import__("os").environ.get("RESYNC_OBJEND")          # an enemy that must also be where the TAS had it at jcheck
                if ok and oe:
                    r2 = e.ram_all(); oid = int(oe, 16)
                    ours2 = sorted((r2[0x3FD + k] + 256 * r2[0x3EE + k], r2[0x439 + k]) for k in range(2, 15) if r2[0x3C1 + k] == oid)
                    want2 = sorted((x, h) for t_, x, h in objs[jcheck] if t_ == oid)
                    ow = __import__("os").environ.get("RESYNC_OBJWANT")       # "x,h,tol": this one object must be here instead
                    if ow:
                        wx, wh, wt = (int(v) for v in ow.split(","))
                        if not (len(ours2) == 1 and abs(ours2[0][0] - wx) <= wt and abs(ours2[0][1] - wh) <= wt): ok = False
                    elif ours2 != want2: ok = False
                if ok and abs(qq[0] - t[1]) <= tol and abs(qq[1] - t[2]) <= tol and qq[2] == t[3]:
                    tail, jend = [], jcheck
                    if extend:                                 # keep replaying the TAS while exactly in sync; end on its last landing
                        cur = []
                        for s in range(jcheck + 1, len(TAS) - 1):
                            if ILL(TAS[s]): break
                            e.step(TAS[s], 1); q2 = st(e.ram_all()); t2 = rows[s]
                            dx = min(abs(q2[0] - t2[1]), 512 - abs(q2[0] - t2[1])); dh = abs((q2[1] - t2[2] + 128) % 256 - 128)
                            if dx > 3 or dh > 3 or q2[2] != t2[3] or q2[4] < 47: break      # within 3 px (sub-pixel drift is fine)
                            cur.append("+".join(TAS[s]))
                            if t2[3] == 0 and rows[s - 1][3] > 0 and q2[:4] == t2[1:5]:  # end on an exactly matching landing
                                tail, jend = list(cur), s
                    best = (tot, j, ["+".join(b) for b in seq] + ["+".join(TAS[s]) for s in range(j + 1, jcheck + 1)] + tail, jend)
                    if jend > jcheck:
                        print(f"   extended in sync to TAS {jend} (+{len(tail)} frames)", flush=True)
                    print(f"BEST {tot} frames: prefix {len(seq)} then TAS {j + 1}..{jcheck}; end {qq[:3]} TAS {t[1:4]}", flush=True)
                    if save:
                        (PROJECT / "knowledge" / save).write_text(json.dumps(best[2]))
                    if stop_first:
                        e.close(); return best
                e.mload(sid); e.mfree(sid)
    e.close()
    return best

if __name__ == "__main__":
    bm, jlo, jhi, jcheck = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    dirc = sys.argv[5] if len(sys.argv) > 5 else "R"
    maxa = int(sys.argv[6]) if len(sys.argv) > 6 else 40
    oc = tuple(int(v, 0) for v in sys.argv[8].split(",")) if len(sys.argv) > 8 else None
    best = run(bm, jlo, jhi, jcheck, dirc, maxa, objcheck=oc, save=sys.argv[7] if len(sys.argv) > 7 else None,
               stop_first=bool(int(__import__("os").environ.get("RESYNC_FIRST", 0))))
    print("result", best[:2] if best else None)
    if best and len(sys.argv) > 7:
        (PROJECT / "knowledge" / sys.argv[7]).write_text(json.dumps(best[2]))
