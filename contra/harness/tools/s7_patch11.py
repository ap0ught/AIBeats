"""Second-pass patch 11: earlier jump to the step 800 (762: the first point clear of the claw at 758) and the
wall-top jump without a pull-back (it lands on the wall's top 6 frames sooner)."""
from pathlib import Path

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
old = 'Jump(p.get("b_step", 768)), Land(y=164),'
assert s.count(old) == 1
s = s.replace(old, 'Jump(p.get("b_step", 762)), Land(y=164),')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
old = '''            for jx in (817, 816, 818, 815, 819):
                for lf in (12, 11, 13, 10, 14):
                    for ln in (3, 2, 4):'''
new = '''            for jx in (0, 813, 815, 817, 819):
                for lf in (12, 16, 9):
                    for ln in (0, 1, 2, 3, 4):'''
assert s.count(old) == 1
s = s.replace(old, new)
old = '''                    if best is not None and tried >= 30:
                        break
                if best is not None and tried >= 30:
                    break
            if best is not None:
                break'''
new = '''                    if best is not None and tried >= 25:
                        break
                if best is not None and tried >= 25:
                    break
            if best is not None:
                break'''
assert s.count(old) == 1
s = s.replace(old, new)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
