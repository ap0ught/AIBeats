"""Classify a bf61 scan by c: G = TAS-equivalent; H61 = hit in 6-1 (thrower axes); H36 = hit in room 36 before 32300 (thrower axes);
J36 = the 32426 jetpack/shuriken hit; other."""
import sys, re
fn = sys.argv[1]; okrooms = sys.argv[2]; okhits = sys.argv[3]
cl = {}
for l in open(fn):
    m = re.match(r'v\s+(\d+) \(TAS (\d+)\).*hp (\d+) np (\d+) it (\d+) rm (\d+) X,y (\(.*?\)) div (\S+) hits \[(.*?)\] rooms (\[.*?\])', l)
    if not m: continue
    v, t, hp, np_, it, rm, xy, div, hits, rooms = m.groups(); c = (int(v) - int(t) + 84) % 256
    h = [int(x) for x in hits.split(',') if x.strip()]
    if rooms == okrooms and '[' + hits + ']' == okhits: k = 'G'
    elif h and h[0] < 31487: k = 'H61'
    elif h and h[0] < 32300: k = 'H36'
    elif h and h[0] in (32426, 32425, 32427): k = 'J36'
    else: k = 'other'
    cl.setdefault(k, []).append(c)
def runs(cs):
    cs = sorted(cs); out = []
    for c in cs:
        if out and c == out[-1][1] + 1: out[-1][1] = c
        else: out.append([c, c])
    return ', '.join(f'{a}' if a == b else f'{a}-{b}' for a, b in out)
for k in sorted(cl): print(k, len(cl[k]), ':', runs(cl[k]))
