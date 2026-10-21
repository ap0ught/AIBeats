"""Second-pass patch 1 for contra/stages/s7.py: Barrier route + scripted door fight. utf-8, temp file + rename."""
from pathlib import Path

p = Path(r"contra\stages\s7.py")
s = p.read_text(encoding="utf-8")


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a))
    s = s.replace(a, b)


rep("from .s6 import exit_proc as _exit_proc\n", "from .s6 import exit_proc as _exit_proc\nfrom . import s7b\n")
rep('''    if t == T_CART and r is not None and r.user.get("kill_carts"):
        return (16, 12)                 # the cart at the alley's mouth is in the way: shoot it (3 HP)
''', '''    if t == T_MCART and r is not None and r.user.get("shoot_mcart") and 0 < e["hp"] < 0xF0 and e["routine"] < 5:
        return (16, 12)                 # the rolling cart on the lower floor of screen 5 (3 HP): in the way
''')
rep('''    if t in (T_CART, T_MCART):
        if r is not None and r.user.get("kill_carts"):
            return None
        return (16, 12)
''', '''    if t == T_CART:
        return (16, 12)                 # stationary carts are ridden: never shot
    if t == T_MCART:
        if r is not None and r.user.get("shoot_mcart"):
            return None
        return (16, 12)
''')
a = s.index("def route_c(p=P):")
b = s.index("def route_e(p=P):")
new_cd = '''def route_c(p=P):
    """SECOND PASS. Lower floor under the claws of screen 5 -> cart 1424 ("Chariot Hop") -> small ledge -> the
    Barrier pill box (s7b.bgrab_proc) -> floor -> step 1632 -> ledge 1696 -> off at 1792 (cart 1824)."""
    return [
        set_user(shoot_mcart=True, fire_range=p.get("c_fire_range", 100)),
        Run(p.get("c_pre", 1392)),                  # claws 1270..1398 (runner remedies), the rolling cart is shot
        set_user(shoot_mcart=False, fire_range=p.get("fire_range", 60)),
        Proc(s7b.bgrab_proc, "B grab"),
        Mark("bgrab"),
        Set(aim_mode="off"),                        # invincible from here to the trio: no shots (they only lag)
        Jump(p.get("c_step", 1596)), Land(y=164),   # step at 1632
        Jump(p.get("c_up", 1652)), Land(y=132),     # ledge at 1696 (claws at 1718, 1750 above it)
        Mark("ledge3"),
        Run(1792), Land(),                          # off the ledge (cart at 1824 below)
        Mark("cart3"),
    ]


def route_d(p=P):
    """Bottom floor of screens 7-9 with the Barrier: under two hanging walls, the pit at 2320 (cart at 2376),
    Heartbreak Alley straight through (the seeking claws cannot hurt), step 2592, ledge 2656, the trio."""
    return [
        Jump(p.get("d_pit", 2318)), Land(),         # the pit 2320..2367 (cart at 2376 beyond it)
        Mark("alley"),
        Jump(p.get("d_step", 2562)), Land(y=164),   # step at 2592
        Set(aim_mode="always"),                     # the trio: fire forward at every opportunity
        Jump(p.get("d_up", 2612)), Land(y=132),     # ledge at 2656 with the three rising walls
        Mark("trio"),
        Run(2800),
        Set(aim_mode=None),
        Run(2816), Land(y=196),
        Mark("lower4"),
    ]


'''
s = s[:a] + new_cd + s[b:]
rep('''        Until(lambda r: r.c.f.cam >= 3488 - 24, ("Right",), "boss approach"),
        Mark("boss_beam"),
        Proc(boss_proc, "boss"),
''', '''        Until(lambda r: r.c.f.cam >= 3488 - 24, ("Right",), "boss approach"),
        Mark("boss_beam"),
        Set(aim_mode="off"),
        Proc(boss_proc if p.get("boss_beam") else s7b.boss_proc2, "boss"),
''')
rep('SAVE_MARKS = ("cart1", "walls3", "lower2", "cart3", "alley", "trio", "lower4", "last", "boss_beam", "boss_dead")',
    'SAVE_MARKS = ("cart1", "walls3", "lower2", "bgrab", "cart3", "alley", "trio", "lower4", "last", "boss_beam",\n'
    '              "boss_dead")')
rep('''           "saved": list(r.saved)}''', '''           "saved": list(r.saved), "bgrab": r.user.get("bgrab"), "boss": r.user.get("boss")}''')
tmp = p.with_name(p.name + ".tmp")
tmp.write_text(s, encoding="utf-8")
tmp.replace(p)
print("patched")
