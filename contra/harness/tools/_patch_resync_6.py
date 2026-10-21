"""One-off patch (kept for the record): boss handling in repair_stage. When the movie fails after a long stretch
without progress (a boss it expects to be dead is still alive), find where the movie stops shooting, keep repeating
its own last 48 rows there until the boss's HP is 0, and try every resume point within +-12 frames of that."""
import os
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "contra" / "resync.py"
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep('''    elif kind == "loopwait":''',
    '''    elif kind == "cyc":                      # n rows taken cyclically from the L rows before t (all buttons)
        L, n = ed[2], ed[3]
        pat = rows[max(0, t - L):t] or [()]
        rows[t:t] = [pat[i % len(pat)] for i in range(n)]
    elif kind == "loopwait":''')
rep('''    if ed[0] == "loopwait":
        return ed[3]''', '''    if ed[0] in ("loopwait", "cyc"):
        return ed[3]''')
rep('''        cands = [rand_edit(rng, rows, w0, max(w0 + 1, D - 6), kinds) for _ in range(K * (1 + min(fails, 2)))]
        lg = base + getattr(r, "last_gain", 0)
        if D - lg > 250:''',
    '''        cands = [rand_edit(rng, rows, w0, max(w0 + 1, D - 6), kinds) for _ in range(K * (1 + min(fails, 2)))]
        lg = base + getattr(r, "last_gain", 0)
        boss_cands = []
        if D - lg > 250 and fails < 2:
            # where does the movie stop shooting after progress stopped? (last B before 30 rows without one)
            t = None
            lastb = None
            for i in range(lg, min(D, len(rows) - 31)):
                if "B" in rows[i]:
                    lastb = i
                elif lastb is not None and i - lastb >= 30:
                    t = lastb + 1
                    break
            if t is not None:
                c0 = max(0, t - 100)
                drop_ck(c0)
                cn = checkpoint(c0)
                HPF = dict(F)
                for sl in range(16):
                    HPF[f"hp{sl}"] = 0x578 + sl
                    HPF[f"ty{sl}"] = 0x528 + sl
                    HPF[f"rt{sl}"] = 0x4B8 + sl
                pat = rows[max(0, t - 48):t] or [()]
                e0.load(cn)
                e0.set_fields(HPF)
                e0.trace(True)
                e0.run_comp(rows[c0:t] + [pat[i % len(pat)] for i in range(1500)])
                tr = e0.last_trace
                e0.trace(False)
                e0.set_fields(F)
                at = tr[t - c0 - 1]
                slots = [sl for sl in range(16) if at[f"rt{sl}"] and at[f"ty{sl}"] != 1 and at[f"hp{sl}"] > 8]
                if slots:
                    bs = max(slots, key=lambda sl: at[f"hp{sl}"])
                    e_hp = next((i for i in range(t - c0, len(tr)) if tr[i][f"hp{bs}"] == 0 or tr[i][f"ty{bs}"] != at[f"ty{bs}"]), None)
                    log(f"[{out}]    boss: the movie stops shooting at row {t} with slot {bs} (type ${at[f'ty{bs}']:02x}) at "
                        f"{at[f'hp{bs}']} HP; repeating its last 48 rows the HP reaches 0 after {None if e_hp is None else e_hp - (t - c0)} more frames")
                    if e_hp is not None:
                        d = e_hp - (t - c0)
                        boss_cands = [("cyc", t, 48, nn) for nn in range(max(1, d - 12), d + 13)]
                        w0 = min(w0, c0)
        if boss_cands:
            cands = boss_cands
            drop_ck(w0)
            cname = checkpoint(w0)
        elif D - lg > 250:''')
tmp = p.with_name("resync.py.tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(p, p.with_name("resync.py.backup6"))
os.replace(tmp, p)
print("patched")
