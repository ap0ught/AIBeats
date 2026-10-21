"""One-off patch: FightCfg.first_jump_rows (the rows on which a "free" jump may be taken; None = any).
utf-8, temp file then rename."""
import os
from pathlib import Path
p = Path(__file__).resolve().parent.parent / "contra" / "stages" / "s3s8_fight.py"
s = p.read_text(encoding="utf-8")
reps = [
("""    aim_dir: dict = field(default_factory=dict)   # aim -> base override, e.g. {"U": ()} to stand still
""", """    aim_dir: dict = field(default_factory=dict)   # aim -> base override, e.g. {"U": ()} to stand still
    first_jump_rows: tuple | None = None   # "free" mode: the only rows on which a jump may start (None = any)
"""),
("""                Jsets = ([set()] + [{n.i + a} for a in cfg.free_offsets]) if ground(n.last) else [set()]
""", """                Jsets = ([set()] + [{n.i + a} for a in cfg.free_offsets
                                    if cfg.first_jump_rows is None or (n.i + a) in cfg.first_jump_rows
                                    or n.i < panic["until"]]) if ground(n.last) else [set()]
"""),
]
for a, b in reps:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
os.replace(tmp, p)
print("patched")
