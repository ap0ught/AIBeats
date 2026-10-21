"""Helpers for the base-boss experiments (second pass, stages 2 and 4). Used by snippets run through s2_daemon."""
import contra.stages.base_common as bc

EXTRA = {"ysub": 0x94, "frame_fc": 0x1A}
for _i in range(10):
    EXTRA[f"bax{_i}"] = 0x3A8 + _i   # bullet X velocity accumulator (verified against ram.asm in the snippet a2)
    EXTRA[f"bay{_i}"] = 0x398 + _i


def fields(extra=None):
    x = dict(EXTRA)
    if extra:
        x.update(extra)
    return bc.make_fields(extra=x)


def trace(e, rows):
    e.trace(True)
    e.run([tuple(r) for r in rows])
    tr = e.last_trace
    e.trace(False)
    return tr


def events(prev, s, keys=("screen", "loc", "plates", "cores", "jump", "death", "attack", "bossdef")):
    ev = []
    for k in keys:
        if s[k] != prev[k]:
            ev.append(f"{k} {prev[k]}->{s[k]}")
    if s["lagged"]:
        ev.append("LAG")
    pe = {x[0]: x for x in bc.enemies(prev)}
    ce = {x[0]: x for x in bc.enemies(s)}
    for k in ce:
        if k not in pe:
            ev.append(f"+e{k} t{ce[k][2]:02x} hp{ce[k][3]} ({ce[k][4]},{ce[k][5]}) s{ce[k][6]:02x} a{ce[k][8]:02x}")
        else:
            a, b = pe[k], ce[k]
            for nm, j in (("type", 2), ("hp", 3), ("st", 6), ("rt", 1)):
                if a[j] != b[j]:
                    ev.append(f"e{k}(t{b[2]:02x}) {nm} {a[j]:x}->{b[j]:x}")
    for k in pe:
        if k not in ce:
            ev.append(f"-e{k} t{pe[k][2]:02x}")
    return ev


def rows_spec(n, spec):
    return bc.rows_from_spec(n, spec)
