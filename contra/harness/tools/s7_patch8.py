"""Second-pass patch 8: never fire while an M / F / L flying capsule is ahead of Bill (a stray pellet releases
the item; the F item then lands in the wall-top jump path and cannot be avoided)."""
from pathlib import Path

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old = "fire_policy = make_fire_policy(target_box, avoid_box)\n"
new = '''_base_fire_policy = make_fire_policy(target_box, avoid_box)


def fire_policy(r, want, aim_over):
    """The generic Spread auto-aim, silenced while a flying capsule that holds M, F or L is on screen ahead of
    Bill (or just behind him): the capsule flies right at 1.5 px/frame through the line of fire for about 250
    frames, and the prediction in avoid_box is not exact for its sine path."""
    f = r.c.f
    for e in f.enemies():
        if e["type"] == T_CAPSULE and (e["attr"] & 7) in (1, 2, 4) and e["x"] > f["x"] - 24:
            return want
    return _base_fire_policy(r, want, aim_over)
'''
assert s.count(old) == 1
s = s.replace(old, new)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
