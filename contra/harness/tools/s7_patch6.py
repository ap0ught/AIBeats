"""Second-pass patch 6: trio_try waits for a destroyed wall to vanish (it is lethal for 3 more frames) and the
stop distance becomes a grid parameter (point-blank shots do only 1 damage per volley; 25+ px away they do more)."""
from pathlib import Path

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''                if e["type"] == T_RISE and 0 < e["hp"] < 0xF0 and 0 < e["x"] - f["x"] < stop_d:
                    want.discard("Right")''',
    '''                if e["type"] != T_RISE or not (0 < e["x"] - f["x"] < stop_d):
                    continue
                if e["hp"] == 0 and e["x"] - f["x"] >= 17:
                    continue                    # dying: gone in 3 frames, only its last 16 px are still lethal
                want.discard("Right")''')
rep('''        for jx in (2612, 2616, 2620, 2608):
            for phase in range(5):
                for stop_d in (16, 17):''',
    '''        for jx in (2612, 2618):
            for phase in range(5):
                for stop_d in (17, 22, 27, 32, 38):''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
