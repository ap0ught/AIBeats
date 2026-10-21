"""Second-pass patch 9: solve(): optional leading pause (phase scans), all procedure results in the output."""
from pathlib import Path

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''    res = r.solve(max_deaths=max_deaths, back=110)
    c = r.c
    out = {"ok": res == "done",''', '''    lead = int((params or {}).get("lead_pause", 0))
    if lead:
        # phase scans only: a pause of `lead` frames on the very first frame. The frame counter runs on while the
        # game stands still, so the stage is then played as if it had started `lead` frames later in $1A terms.
        r.remedies.append(Remedy(0, "pause", lead))
    res = r.solve(max_deaths=max_deaths, back=110)
    c = r.c
    out = {"ok": res == "done", "lead_pause": lead, "frames_without_lead_pause": len(c.rows) - lead,''')
rep('''"saved": list(r.saved), "bgrab": r.user.get("bgrab"), "boss": r.user.get("boss")}''',
    '''"saved": list(r.saved), "procs": {k: v for k, v in r.user.items()
                                              if k in ("precart", "bgrab", "walls2", "trio", "boss", "jump_choice")}}''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
