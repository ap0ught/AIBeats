"""Third pass lab helpers (rooms of the two bases). Used by snippets run through tools/s2_daemon.py (port 47391)."""
import contra.stages.base_common as bc

F = bc.make_fields(extra={"ysub": 0x94, "xsub": 0x0})


def spec_rows(n, spec):
    return bc.rows_from_spec(n, spec)


def trace(e, state, rows, fields=None):
    """Load a savestate (or an in-memory id when state starts with 'm:'), play rows, return [State] (index 0 = the
    loaded frame)."""
    e.set_fields(fields or F)
    s0 = e.mload(state[2:]) if state.startswith("m:") else e.load(state)
    e.trace(True)
    e.run([tuple(r) for r in rows])
    tr = [s0] + list(e.last_trace)
    e.trace(False)
    return tr


def logic(tr):
    """Drop lag frames: index = T (0 = the loaded frame)."""
    return [tr[0]] + [s for s in tr[1:] if not s["lagged"]]


def hits(tr):
    """[(index, slot, type, hp before, hp after)] HP changes of wall targets."""
    out = []
    for i in range(1, len(tr)):
        a, b = tr[i - 1], tr[i]
        for k in range(16):
            if a[f"er{k}"] and a[f"et{k}"] == b[f"et{k}"] and a[f"eh{k}"] != b[f"eh{k}"]:
                out.append((i, k, b[f"et{k}"], a[f"eh{k}"], b[f"eh{k}"]))
    return out


def show(tr, a=0, b=None, every=1):
    b = len(tr) if b is None else b
    for i in range(a, min(b, len(tr)), every):
        s = tr[i]
        print(f"T{i:4d} x{s['x']:4d} y{s['y']:4d} j{s['jump']:3d} aim{s['aim']:2d} pad{s['pad']:02x} lag{s['lagged']} "
              f"cl{s['cleared']:3d} B[{bc.fmt_bullets(s)}]")
