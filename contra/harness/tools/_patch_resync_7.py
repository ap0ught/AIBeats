"""One-off patch (kept for the record): when the movie's rows run out before the stage ends (a TAS movie stops at
its last needed input; on this ROM/emulator the final boss needs more), keep repeating its last 48 rows until
BOSS_DEFEATED_FLAG is set, then hold Up (the leaderboard's end rule wants Up or Down held) until the level ends."""
import os
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "resync.py"
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep('''    elif kind == "loopwait":''',
    '''    elif kind == "hold":                     # n rows of one button at t (t = len(rows) appends)
        rows[t:t] = [(ed[2],) if ed[2] else ()] * ed[3]
    elif kind == "loopwait":''')
rep('''    if ed[0] in ("loopwait", "cyc"):
        return ed[3]''', '''    if ed[0] in ("loopwait", "cyc", "hold"):
        return ed[3]''')
rep('''        if r.reason in ("eof", "gameover"):
            log(f"[{out}] {r.reason} without finishing the stage: {r}")
            save(False, 0)
            return False, rows, edits''',
    '''        if r.reason == "eof" and len(rows) < 7000 and not any(e[0] == "hold" for e in edits):
            t = len(rows)
            c0 = max(k for k in ck if k <= max(0, t - 200))
            pat = rows[max(0, t - 48):t] or [()]
            x = play(e0, ck[c0], rows[c0:] + [pat[i % len(pat)] for i in range(2000)], keep_trace=True,
                     stop_on_level=False)
            b = next((i for i, st_ in enumerate(x.trace) if i >= t - c0 and st_["bossdef"] == 1), None)
            if x.reason == "eof" and b is not None:
                n = (c0 + b + 1) - t
                for ed in (("cyc", t, 48, n), ("hold", t + n, "Up", 700), ("hold", t + n + 700, "", 700)):
                    rows = apply_edit(rows, ed)
                    edits.append(ed)
                log(f"[{out}]    the movie's rows ended at {t} with the boss alive: repeated its last 48 rows for {n} "
                    f"frames (boss defeated flag set), then Up held")
                save(False, 0)
                continue
            log(f"[{out}]    the movie's rows ended at {t}; repeating its last rows did not finish the boss: {x}")
        if r.reason in ("eof", "gameover"):
            log(f"[{out}] {r.reason} without finishing the stage: {r}")
            save(False, 0)
            return False, rows, edits''')
tmp = p.with_name("resync.py.tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(p, p.with_name("resync.py.backup7"))
os.replace(tmp, p)
print("patched")
