"""Compact event list of the Queen's slot through the ending, from an endcap_<tag> capture (see end_var.py)."""
import sys
from end_an import load


def events(tag, a=None, b=None):
    idx, rows = load(tag)
    f0 = idx["first_frame"]
    s = idx.get("slot", 3)
    out = []
    p = None
    for i, m in enumerate(rows):
        f = f0 + i
        if (a and f < a) or (b and f > b):
            continue
        h = m[0x439 + s] + 256 * m[0x42A + s]
        h = h - 65536 if h > 32767 else h
        cur = dict(id=m[0x3C1 + s], spr=m[0x3D0 + s], fl=m[0x4A2 + s], st=m[0x4B1 + s], A=m[0x4ED + s], h=h, lv=m[0x10], t=m[0x0B],
                   x=m[0x3FD + s], v=m[0x4C0 + s], ctr=m[0x586])
        ev = []
        if p is not None:
            for k in ("id", "spr", "st", "lv"):
                if cur[k] != p[k]:
                    ev.append(f"{k} {p[k]}>{cur[k]}")
            if cur["A"] != (p["A"] - 1) % 256 and cur["A"] != p["A"]:
                ev.append(f"A {p['A']}>{cur['A']}")
            if (cur["A"] == p["A"]) != p.get("Afrozen", False):
                ev.append("A stops" if cur["A"] == p["A"] else "A runs")
            cur["Afrozen"] = cur["A"] == p["A"]
            dh = cur["h"] - p["h"]
            if dh != p.get("dh", 0):
                ev.append(f"dh {p.get('dh', 0)}>{dh}")
            cur["dh"] = dh
            if cur["t"] == p["t"] and not p.get("tfz") and cur["lv"] == 13:
                ev.append("T freeze")
            cur["tfz"] = cur["t"] == p["t"]
        if ev:
            out.append((f, cur, ev))
        p = cur
    return idx, out


if __name__ == "__main__":
    tag = sys.argv[1]
    idx, out = events(tag, idx0 := None)
    hit = idx["hit21"]
    for f, c, ev in out:
        if f < hit - 3:
            continue
        ref = f"hit+{f - hit}" if f < idx["resp"] else f"resp+{f - idx['resp']}" if f < idx["back"] else f"back+{f - idx['back']}"
        print(f, ref, f"h={c['h']} A={c['A']} fl={c['fl']} spr={c['spr']} t={c['t']} x={c['x']}", "|", "; ".join(ev))
