"""Second-pass patch 12: longer fire range after the six claws (kill the gunners before their first shot)."""
from pathlib import Path

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old = '''    return [
        Jump(p.get("e_step", 3316)), Land(y=164),   # step at 3360
        Mark("last"),
    ]'''
new = '''    return [
        Run(p.get("e_far_from", 3100)),
        # SECOND PASS: from here the auto-aim reaches further, so the gunners (10 HP, first shot about 60 frames
        # after they scroll in) are hit from the moment they appear
        set_user(fire_range=p.get("e_fire_range", 130)),
        Jump(p.get("e_step", 3316)), Land(y=164),   # step at 3360
        Mark("last"),
    ]'''
assert s.count(old) == 1
s = s.replace(old, new)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
