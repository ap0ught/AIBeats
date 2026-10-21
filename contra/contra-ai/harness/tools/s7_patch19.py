"""Second-pass patch 19: (a) a remedy trial that reaches an unsolved Proc alive counts as passed and stops there
(the door grid took 4 minutes PER TRIAL when a soldier killed Bill 30 px before the boss); (b) the scripted door
fight shoots a soldier that walks at Bill on the ground."""
from pathlib import Path

p = Path(r"contra\stages\s6run.py")
s = p.read_text(encoding="utf-8-sig")
old = '''        self.restore(sn)
        self.remedies = saved + [rm for rm in rems if rm.kind != "shift"]
        self.trials += 1
        try:
            res = self.play(until_row=R)
        finally:
            self.remedies = saved
            self.shifts = saved_shifts'''
new = '''        self.restore(sn)
        self.remedies = saved + [rm for rm in rems if rm.kind != "shift"]
        self.trials += 1
        self._in_trial = True                 # a memoised Proc (stage 7) ends the trial instead of searching
        try:
            res = self.play(until_row=R)
        finally:
            self._in_trial = False
            self.remedies = saved
            self.shifts = saved_shifts'''
assert s.count(old) == 1
s = s.replace(old, new)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7b.py")
s = p.read_text(encoding="utf-8-sig")
old = '''            c.restore(base)
            c.free(base)
        n0, m0 = len(c.rows), len(r.marks)
        u0 = dict(r.user)
        fn(r)'''
new = '''            c.restore(base)
            c.free(base)
        if getattr(r, "_in_trial", False):
            raise _Done()                     # a remedy trial got here alive: that is all the trial has to show
        n0, m0 = len(c.rows), len(r.marks)
        u0 = dict(r.user)
        fn(r)'''
assert s.count(old) == 1
s = s.replace(old, new)
old = "from .s6ctl import Stuck\n"
assert s.count(old) == 1
s = s.replace(old, "from .s6ctl import Stuck\nfrom .s6run import Done as _Done\n")
old = '''            elif s >= up_s:
                want.add("Up")
            if hover is not None'''
new = '''            elif s >= up_s:
                want.add("Up")
            if g and "A" not in want:
                # a soldier walking at Bill on the ground: a level volley (the Spread kills it in one hit)
                for e in f.enemies():
                    if (e["type"] == 0x05 and 0 < e["hp"] < 0xF0 and e["routine"] < 5 and 0 < e["x"] - f["x"] < 56
                            and abs(e["y"] - f["y"]) < 20):
                        want.discard("Up")
                        want.discard("Down")
                        if c.can("B"):
                            want.add("B")
                        break
            if hover is not None'''
assert s.count(old) == 1
s = s.replace(old, new)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
