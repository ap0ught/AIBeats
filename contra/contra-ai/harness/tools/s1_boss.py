"""Stage 1 boss experiments from a saved hand-over state (states/s1/<name>_boss.State).

    python tools/s1_boss.py <state> scripted <action list, e.g. RD*8,RF*3,PR*4,P*20>
    python tools/s1_boss.py <state> beam [width]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.stages import s1  # noqa: E402
from contra.stages.s1_common import Game, log  # noqa: E402

state, mode = sys.argv[1], sys.argv[2]
g = Game(name="s1_boss")
try:
    g.load_file(state)
    if mode == "scripted":
        acts = []
        for tok in sys.argv[3].split(","):
            a, _, n = tok.partition("*")
            acts += [a] * int(n or 1)
        while g.pad.held["B"] or not g.pad.can_press("B"):
            g.step({"Right"})
        hp0 = 32
        prev_en = {e[0]: e for e in g.r.enemies()}
        log("at start:", [(e[0], hex(e[1]), e[3], e[4], e[5]) for e in g.r.enemies()])
        for i, a in enumerate(acts):
            for k in range(5):
                r = g.step(s1.boss_rows(g, a, k))
                hp = s1.door_hp(r)
                d = s1.door(r)
                cur = {e[0]: e for e in r.enemies()}
                for sl, e in cur.items():
                    if sl not in prev_en or prev_en[sl][1] != e[1]:
                        log(f"      row {len(g.rows)} NEW slot {sl} type ${e[1]:02x} hp {e[3]} at {e[4]},{e[5]} attr ${e[8]:02x}"
                            f" vel {r.m[0x508 + sl]}.{r.m[0x518 + sl]},{r.m[0x4E8 + sl]}.{r.m[0x4F8 + sl]}")
                for sl, e in prev_en.items():
                    if sl not in cur and e[1] != 1:
                        log(f"      row {len(g.rows)} GONE slot {sl} type ${e[1]:02x}")
                prev_en = cur
                if hp != hp0 or r.dead or k == 0:
                    log(f"step {i:2d}.{k} {a:2s} row {len(g.rows):3d} auto {r.auto:3d} scr {r.scr} x={r.x} y={r.y} air={r.air} hp {hp} "
                        f"door {d[4:6] if d else None} pend {s1.pending_hits(r)} bullets {r.nbullets()} dead {r.dead}"
                        + (f" enemies {[(e[1], e[4], e[5]) for e in r.enemies() if e[1] not in (0x11,)]}" if r.dead else ""))
                hp0 = hp
                if r.dead or hp == 0:
                    break
            if r.dead or hp == 0:
                break
    else:
        w = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        ja = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "-" else None
        res = s1.boss_fight(g, width=w, jump_at=ja)
        log("result:", None if res is None else (len(res[0]), res[1]))
        if res is None:
            from contra.stages.s1_engine import beam
            for sc, hist in (beam.last_fail or []):
                log("  dead end:", sc, ",".join(hist))
        if res:
            from contra.stages.s1_engine import beam
            log("actions:", ",".join(beam.last_hist))
            log("rows:", ["+".join(x) for x in res[0]])
finally:
    g.close()
