"""One-off patch (kept for the record): "loop" edits (repeat the movie's own last rows) for bosses that need more
damage on this ROM/emulator than the movie delivers, and for base rooms whose core dies later than the movie expects."""
import os
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "resync.py"
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep('''    elif kind == "wait":                     # n frames of nothing before row t (wait for a base fence to drop)
        rows[t:t] = [()] * ed[2]''',
    '''    elif kind == "wait":                     # n frames of nothing before row t (wait for a base fence to drop)
        rows[t:t] = [()] * ed[2]
    elif kind == "loop":                     # repeat the L rows before t, n times, before going on (more of the
        L, n = ed[2], ed[3]                  # movie's own attack pattern; everything after is delayed by L*n)
        pat = rows[max(0, t - L):t]
        rows[t:t] = pat * n
    elif kind == "loopwait":                 # n frames taken cyclically from the L rows before t, without Up
        L, n = ed[2], ed[3]
        pat = [tuple(b for b in r if b != "Up") for r in rows[max(0, t - L):t]] or [()]
        rows[t:t] = [pat[i % len(pat)] for i in range(n)]''')
rep('''    return {"P": ed[2] if len(ed) > 2 else 0, "wait": ed[2] if len(ed) > 2 else 0, "dup": 1, "del": -1}.get(ed[0], 0)''',
    '''    if ed[0] == "loop":
        return ed[2] * ed[3]
    if ed[0] == "loopwait":
        return ed[3]
    return {"P": ed[2] if len(ed) > 2 else 0, "wait": ed[2] if len(ed) > 2 else 0, "dup": 1, "del": -1}.get(ed[0], 0)''')
# elec: keep shooting with the room's last burst pattern while waiting for the fence
rep('''            x = play(e0, cname, rows[c0:up] + [()] * 400, keep_trace=True, stop_on_death=False, stop_on_level=False)
            j = next((i for i, s in enumerate(x.trace) if i >= up - c0 - 1 and s["cleared"] == 0x80), None)
            if j is not None:
                n = max(1, (c0 + j) - up + 1)            # Up must be read on the frame AFTER the flag reads $80
                ed = ("wait", up, n)''',
    '''            LW = 26
            pat = [tuple(b for b in r if b != "Up") for r in rows[max(0, up - LW):up]] or [()]
            x = play(e0, cname, rows[c0:up] + [pat[i % len(pat)] for i in range(600)], keep_trace=True,
                     stop_on_death=False, stop_on_level=False)
            j = next((i for i, s in enumerate(x.trace) if i >= up - c0 - 1 and s["cleared"] == 0x80), None)
            if j is not None:
                n = max(1, (c0 + j) - up + 1)            # Up must be read on the frame AFTER the flag reads $80
                ed = ("loopwait", up, LW, n)''')
rep('''            log(f"[{out}]    fence at row {up}: the room is not cleared within 400 frames -> random search")''',
    '''            log(f"[{out}]    fence at row {up}: the room is not cleared within 600 frames -> random search")''')
# stuck at a boss: loop candidates anchored where progress stopped
rep('''        cands = [rand_edit(rng, rows, w0, max(w0 + 1, D - 6), kinds) for _ in range(K * (1 + min(fails, 2)))]
''',
    '''        cands = [rand_edit(rng, rows, w0, max(w0 + 1, D - 6), kinds) for _ in range(K * (1 + min(fails, 2)))]
        lg = base + getattr(r, "last_gain", 0)
        if D - lg > 250:
            # no progress for a long time before failing: probably a boss that the movie expects to be dead.
            # Try repeating the movie's own attack rows somewhere after the place progress stopped.
            lo, hi = lg + 30, max(lg + 60, min(D - 6, lg + 700))
            w0 = min(w0, max(0, lo - 100))
            for _ in range(K * (1 + min(fails, 2))):
                t = rng.randrange(lo, hi)
                cands.append(("loop", t, rng.choice((24, 48, 48, 96)), rng.choice((1, 2, 2, 3, 4, 6))))
            drop_ck(w0)
            cname = checkpoint(w0)
''')
rep('''            return play(emu, cname, rr[w0:D + H + 2], stall=stall)''',
    '''            return play(emu, cname, rr[w0:D + H + 2 + max(0, edit_cost(ed))], stall=stall)''')
tmp = p.with_name("resync.py.tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(p, p.with_name("resync.py.backup5"))
os.replace(tmp, p)
print("patched")
