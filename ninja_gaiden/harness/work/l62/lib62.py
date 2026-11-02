"""l62 helpers (6-1 / 6-2 builder). Frames = power-on rows on the TAS axis unless noted."""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
_oi62 = F.FastCore.__init__
def _ni62(self, *a, **k):
    k.setdefault('min_free_gb', 1.2); return _oi62(self, *a, **k)
F.FastCore.__init__ = _ni62

def rows_file(p):
    L = open(p).read().split(chr(10))
    if L and L[-1] == '': L = L[:-1]
    return [row(l.strip()) for l in L if not l.startswith('#')]

def wrows(p, rows, hdr=''):
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fo:
        if hdr: fo.write('# ' + hdr + '\n')
        for r in rows: fo.write(P(r) + '\n')
    os.replace(tmp, p)

def base(F0=None, mst=None, pokes=None, slot='b'):
    """Mesen core at TAS frame F0 (or a .mst), pokes {addr: val}, saved in slot."""
    fc = core(mst) if mst else core_at(F0)
    for a_, v in (pokes or {}).items(): fc.poke(a_, v)
    fc.save(slot); fc._ka_slot = slot
    return fc

def run(fc, rows, slot='b'):
    return fc.run_batch(slot, [rows], record='all')[0].states

def events(st, f1, show_every=0, prev=None):
    """f1 = frame number of st[0]. Returns list of event strings."""
    ev = []
    for i, s in enumerate(st):
        f = f1 + i
        p = st[i-1] if i else prev
        X, y = RXY(s)
        if p is None:
            continue
        if s['room6e'] != p['room6e']: ev.append(f'{f} room {p["room6e"]}->{s["room6e"]} X{X} y{y}')
        if s['hp65'] < p['hp65']: ev.append(f'{f} HIT {p["hp65"]}->{s["hp65"]} X{X} y{y}')
        if s['np64'] != p['np64']: ev.append(f'{f} np {p["np64"]}->{s["np64"]} X{X} y{y}')
        if s['item'] != p['item']: ev.append(f'{f} item {p["item"]}->{s["item"]}')
        scr = (s['scr_hi'] - 256 if s['scr_hi'] >= 128 else s['scr_hi'])*256 + s['scr_lo']
        for j in range(8):
            on, on0 = s['eact'] >> j & 1, p['eact'] >> j & 1
            if on and (not on0 or s[f't{j}'] != p[f't{j}']): ev.append(f'{f} spawn s{j} t{s[f"t{j}"]} ({scr + s[f"ex{j}"]},{s[f"ey{j}"]})')
            if on0 and not on: ev.append(f'{f} gone s{j} t{p[f"t{j}"]}')
        if show_every and i % show_every == 0: ev.append(f'{f} X{X} y{y} hp{s["hp65"]} np{s["np64"]}')
    return ev
