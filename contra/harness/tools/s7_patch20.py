"""Second-pass patch 20: (a) the leading pause for phase scans starts on row 40 (on the very first row the game
does not take the Start press: three "phases" of the first scan were all the same solve) and the result says how
many paused frames were really seen; (b) the claw corridor shoots a soldier that walks at Bill."""
from pathlib import Path

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''        # phase scans only: a pause of `lead` frames on the very first frame. The frame counter runs on while the
        # game stands still, so the stage is then played as if it had started `lead` frames later in $1A terms.
        r.remedies.append(Remedy(0, "pause", lead))''',
    '''        # phase scans only: a pause of `lead` frames on row 40, while Bill is still dropping in (on row 0 the game
        # does not take the Start press). The frame counter runs on while the game stands still, so the stage
        # is then played as if it had started `lead` frames later in $1A terms.
        r.remedies.append(Remedy(40, "pause", lead))''')
rep('''    out = {"ok": res == "done", "lead_pause": lead, "frames_without_lead_pause": len(c.rows) - lead,''',
    '''    out = {"ok": res == "done", "lead_pause": lead, "frames_without_lead_pause": len(c.rows) - lead,
           "lead_pause_frames_seen": sum(1 for f in c.tr[:lead + 60] if f["pause"]),''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
rep('''        if mc is not None and 0 < mc["x"] - f["x"] < fire_d and vol < maxvol and c.can("B"):
            want.add("B")
            vol += 1
        _fr(c, want)
        n += 1
        if n > limit:
            raise Fail("corridor: too long")''',
    '''        if mc is not None and 0 < mc["x"] - f["x"] < fire_d and vol < maxvol and c.can("B"):
            want.add("B")
            vol += 1
        elif c.can("B") and any(e["type"] in (0x05, 0x06) and 0 < e["hp"] < 0xF0 and e["routine"] < 5
                                and 0 < e["x"] - f["x"] < soldier_d and abs(e["y"] - f["y"]) < 20
                                for e in f.enemies()):
            want.add("B")                 # a soldier walking at Bill: one level volley
        _fr(c, want)
        n += 1
        if n > limit:
            raise Fail("corridor: too long")''')
rep("def corridor_try(c, x_end, w0=0, kill=(), fire_d=24, maxvol=1, off=3, limit=420, need_cart=1425):",
    "def corridor_try(c, x_end, w0=0, kill=(), fire_d=24, maxvol=1, off=3, limit=420, need_cart=1425, soldier_d=44):")
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"tools\s7_phase_scan.py")
s = p.read_text(encoding="utf-8-sig")
rep('''                   "next_fc": (res.get("replay") or {}).get("next_frame", {}).get("fc"),
                   "seconds": round(time.time() - t0)}
            with open(outp / f"{tag}.jsonl", "a", encoding="utf-8") as fh:''',
    '''                   "next_fc": (res.get("replay") or {}).get("next_frame", {}).get("fc"),
                   "lead_seen": res.get("lead_pause_frames_seen"),
                   "seconds": round(time.time() - t0)}
            with open(outp / f"{tag}.jsonl", "a", encoding="utf-8") as fh:''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
