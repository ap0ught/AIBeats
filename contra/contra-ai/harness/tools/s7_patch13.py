"""Second-pass patch 13: runner.progress_check (opt-in, stage 7 only): a remedy that keeps Bill alive but leaves
him far behind where its nominal cost says he should be (a jump into a hanging wall cost 37 frames, booked as 1)
is charged the frames it really lost, so a cheaper real remedy wins. s6run.py is backed up first."""
import shutil
from pathlib import Path

p = Path(r"contra\stages\s6run.py")
bak = p.with_name(p.name + ".backup_pass1")
if not bak.exists():
    shutil.copyfile(p, bak)
s = p.read_text(encoding="utf-8-sig")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


rep('''            if (ok and prog >= prog_D) or later:
                k = (cost, 1 if later else 0, tuple(-x for x in prog))
                if best is None:
                    best = (cost, prog, rems, k)
                elif best[3][1] == 1 and not later:
                    best = (cost, prog, rems, k)            # alive beats "dies later" (within the slack)
                elif best[3][1] == (1 if later else 0) and k < best[3]:
                    best = (cost, prog, rems, k)''',
    '''            if (ok and prog >= prog_D) or later:
                eff = cost
                if getattr(self, "progress_check", False):
                    # frames really lost against 1 px per row since the death row, beyond the nominal cost
                    lost = (prog_D[1] + (n - D)) - prog[1] - cost
                    if lost > 6:
                        eff = cost + lost
                k = (eff, 1 if later else 0, tuple(-x for x in prog))
                if best is None:
                    best = (eff, prog, rems, k)
                elif best[3][1] == 1 and not later and eff <= best[0] + 8:
                    best = (eff, prog, rems, k)             # alive beats "dies later" (within the slack)
                elif best[3][1] == (1 if later else 0) and k < best[3]:
                    best = (eff, prog, rems, k)
                elif eff + 8 < best[0]:
                    best = (eff, prog, rems, k)''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8-sig")
rep('''    r.local_over = 45
    r.repair_budget = 60
    return r''', '''    r.local_over = 45
    r.repair_budget = 60
    r.progress_check = True          # second pass: charge a remedy the frames it really loses
    return r''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("ok")
