"""Chain A: writes u16a_rngfit.py = rngfit.py + the chain-A changes (rngfit.py itself is shared and must not be edited).
Re-run after rngfit.py changes; every replacement asserts that its anchor text is still there exactly once."""
import os

s = open("rngfit.py", encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80])
    s = s.replace(a, b)


# header
rep('"""Re-fit an old segment onto a new upstream route WITHOUT re-searching it (2026-10-02).',
    '"""[u16a_rngfit.py = chain A\'s copy of rngfit.py, 2026-10-10 (made by u16a_mkrngfit.py). Changes, all marked "chain A":\n'
    '  1. the page mash at the end also tries A,B / B,A on alternate frames (recipe 3 of knowledge/early_savings.md), then one\n'
    '     Select on each of the last frames before the mash (dice: the page takes 44-47 frames);\n'
    '  2. HEAD: when the level timer $0B on the black entry frames differs from the old run\'s (it is 0 behind an A,B mash and\n'
    '     1 behind the old A mash; the level sets it to 0 on its first frame either way), the old inputs up to and including\n'
    '     the old run\'s first timer change are given verbatim before the tracking starts - otherwise the lag logic reads the\n'
    '     missing 1 -> 0 as a dropped frame and repeats an input (every later frame is then one late: STUCK at frame 2);\n'
    '  3. the end check accepts an entry frame whose RAM equals the old run\'s except for $0B/$0C and the stack;\n'
    '  4. emulator log names u16a_rngfit_<out>.log; lives and score at the end are checked / printed against the old run\'s.]\n\n'
    'Re-fit an old segment onto a new upstream route WITHOUT re-searching it (2026-10-02).')

# reference: remember the timer at the old bookmark
rep('''        e.load(part["bookmark"])
        lives, tb = e.byte(0x11), e.byte(0x0B)
''', '''        e.load(part["bookmark"])
        lives, tb = e.byte(0x11), e.byte(0x0B)
        if not ref:
            reference.tb0 = tb                                # chain A: the old run's timer on its entry frame
''')

# rewind: clamp to the earliest save
rep('''        s = max(f for f in self.saves if f <= to)
        self.drop_after(s)''', '''        s = max([f for f in self.saves if f <= to] or [min(self.saves)])   # chain A: never before the head
        self.drop_after(s)''')

# main: log name, HEAD
rep('''    e = BizHawk(log_name=f"rngfit_{seg}.log")
    ref, ref2, tick, dref, m, deaths = reference(e, d, old, len(old))   # the old run's own track''',
    '''    e = BizHawk(log_name=f"u16a_rngfit_{out}.log")
    reference.tb0 = None
    ref, ref2, tick, dref, m, deaths = reference(e, d, old, len(old))   # the old run's own track''')
rep('''    rerolls, safe = [(0, tuple(sorted(F.sel)), 0)] if F.sel else [], 0
    while True:''', '''    rerolls, safe = [(0, tuple(sorted(F.sel)), 0)] if F.sel else [], 0
    # chain A: the head (see the docstring)
    HEAD = int(os.environ.get("RNGFIT_HEAD", -1))
    tb_new = F.tb
    if HEAD < 0:
        HEAD = 0
        if reference.tb0 is not None and F.tb != reference.tb0 and not F.ins_at.get(0):
            HEAD = next((i for i in range(min(n, 40)) if tick[i]), -1) + 1
    if HEAD:
        for i in range(HEAD):
            b = old[i]
            if i in F.sel:
                b = (b + "+Select").lstrip("+")
            e.step(btn(b), 1)
            F.out.append(b)
            mh = e.ram(0, 0x800)
            F.lv.append(mh[0x10])
        F.r, F.tb, F.lives = HEAD, mh[0x0B], mh[0x11]
        F.saves[HEAD] = (e.msave(), F.deaths, F.lives, F.tb, len(F.out))
        print(f"  head: entry timer {reference.tb0} in the old run, {tb_new} here -> the first {HEAD} old inputs given verbatim; "
              f"key now {key(mh)} (old {ref[HEAD - 1]}) {'SAME' if same(key(mh), ref[HEAD - 1]) else 'DIFFERENT'}", flush=True)
    while True:''')
rep('''        lo = max(0, bad - W)
        # 1. harmless?''', '''        lo = max(HEAD, bad - W)
        # 1. harmless?''')

# page mash: patterns + fallback + Select scan
rep('''        pats = {"A even": ("A", ""), "A odd": ("", "A"), "B even": ("B", ""), "B odd": ("", "B")}   # (a Start press that lands in the new level pauses it)''',
    '''        pats = {"A even": ("A", ""), "A odd": ("", "A"), "B even": ("B", ""), "B odd": ("", "B"),   # (a Start press that lands in the new level pauses it)
                "A,B": ("A", "B"), "B,A": ("B", "A")}        # chain A: a fresh press on every frame''')
rep('''        def mash(back, pat):
            """-> (frames to the key match, idle frames from there to the old run's timers, entry identical?)"""
            goto(max(0, c - back))
            for k in range(len(fin) - (c - back) + 60):
                b = pat[k % len(pat)]
                e.step(btn(b), 1)
                F.out.append(b)
                if same(key(e.ram(0, 0x800)), ref[-1]):''',
    '''        VOL = set(range(0x100, 0x200)) | {0x0B, 0x0C}

        def mash(back, pat, selk=None):
            """-> (frames to the key match, idle frames from there to the old run's timers, entry identical?)
            selk (chain A): Select is added on raw frame c - back - selk (a frame of the level's own last inputs)"""
            if selk is None:
                goto(max(0, c - back))
            else:
                goto(max(0, c - back - selk))
                for b in fin[len(F.out):c - back]:
                    if len(F.out) == c - back - selk:
                        b = (b + "+Select").lstrip("+")
                    e.step(btn(b), 1)
                    F.out.append(b)
            for k in range(len(fin) - (c - back) + 60):
                b = pat[k % len(pat)]
                e.step(btn(b), 1)
                F.out.append(b)
                if same(key(e.ram(0, 0x800)), ref[-1]):
                    m1 = e.ram(0, 0x800)
                    if (m1[0x11], bytes(m1[0x5F4:0x5FA])) != (m_end[0x11], bytes(m_end[0x5F4:0x5FA])):
                        return None                               # chain A: lives and score must be the old run's''')
rep('''                    res = (len(F.out), 60, False)                 # (no such frame: the level's clock is not what the old run waited on)''',
    '''                    res = (len(F.out), 0, sum(1 for i in range(0x800) if i not in VOL and m1[i] != m_end[i]) == 0)   # chain A: no such frame = the
                    # page left another timer value behind (0 behind an A,B mash); the next fit handles it (HEAD)''')
rep('''        if best and best[0][0] < len(fin):
            slack = mash(best[1], pats[best[2]])[1]''', '''        selbest = None
        if best and os.environ.get("RNGFIT_PAGESEL", "1") != "0":   # chain A: dice - one Select on one of the frames before the mash
            tops = sorted({(best[1], best[2]), (0, "A,B")})
            for back, name in tops:
                for selk in range(1, int(os.environ.get("RNGFIT_PAGESEL_N", 80)) + 1):
                    if c - back - selk < 1:
                        break
                    got = mash(back, pats[name], selk)
                    if got and (got[0], not got[2]) < (best[0][0], not best[0][2]):
                        best = (got, back, name)
                        selbest = selk
                        print(f"  page dice: Select {selk} frames before the mash ('{name}' from {c - back}) -> set down at {got[0]}", flush=True)
        if best and best[0][0] < len(fin):
            slack = mash(best[1], pats[best[2]], selbest)[1]''')
rep('''            print(f"  briefing page: '{best[2]}' from frame {c - best[1]} -> the toad is set down at frame {len(F.out)} (was {len(fin)}); the old run's "''',
    '''            print(f"  briefing page: '{best[2]}' from frame {c - best[1]}{'' if selbest is None else f' + Select {selbest} frames before it'} -> the toad is set down at frame {len(F.out)} (was {len(fin)}); the old run's "''')
rep('''    print(f"{seg} -> pbeam_{out}.json: {len(F.out)} frames, {len(rerolls)} re-rolls, {F.lags} lag shifts; end level {m[0x10]} toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439]} hp {m[0x51A]} lives {m[0x11]}; slack {slack}", flush=True)''',
    '''    sc = lambda q: "".join(str(q[0x5F4 + i] & 15) for i in range(6))
    print(f"{seg} -> pbeam_{out}.json: {len(F.out)} frames, {len(rerolls)} re-rolls, {F.lags} lag shifts; end level {m[0x10]} toad {m[0x3FD] | m[0x3EE] << 8},{m[0x439]} hp {m[0x51A]} lives {m[0x11]}; slack {slack}", flush=True)
    print(f"  end against the old run's: hp {m[0x51A]}/{m_end[0x51A]} lives {m[0x11]}/{m_end[0x11]} score {sc(m)}/{sc(m_end)} timers {m[0x0B]},{m[0x0C]}/{m_end[0x0B]},{m_end[0x0C]}; "
          f"RAM bytes that differ (stack and $0B/$0C aside): {sum(1 for i in range(0x800) if not (0x100 <= i < 0x200) and i not in (0x0B, 0x0C) and m[i] != m_end[i])}; "
          f"{len(F.out) - n:+d} frames against the old segment's {n}", flush=True)''')
rep('''                    for w in range(400):
                        m2 = e.ram(0, 0x800)''', '''                    for w in range(int(os.environ.get("RNGFIT_SLACKMAX", 4))):   # chain A: every segment of this chain ends on the placement frame
                        m2 = e.ram(0, 0x800)''')
rep('''    e = BizHawk(log_name=f"rngscan_{seg}.log")''', '''    e = BizHawk(log_name=f"u16a_rngscan_{seg}.log")''')
open("u16a_rngfit.py.tmp", "w", encoding="utf-8").write(s)
os.replace("u16a_rngfit.py.tmp", "u16a_rngfit.py")
print("wrote u16a_rngfit.py", len(s), "bytes")
