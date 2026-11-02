"""Summarize a bf61.py output: c = $BF on the 6-1 control row (TAS 84) = (v - TAS_BF_at_F0 + 84) mod 256; good = rooms/hits/item as given."""
import sys, re
fn = sys.argv[1]; want_rooms = sys.argv[2]; want_hits = sys.argv[3]; want_it = sys.argv[4] if len(sys.argv) > 4 else None
good = []; bad = []
for l in open(fn):
    m = re.match(r'v\s+(\d+) \(TAS (\d+)\).*hp (\d+) np (\d+) it (\d+) rm (\d+) X,y (\(.*?\)) div (\S+) hits (\[.*?\]) rooms (\[.*?\])', l)
    if not m: continue
    v, t, hp, np_, it, rm, xy, div, hits, rooms = m.groups(); c = (int(v) - int(t) + 84) % 256
    ok = rooms == want_rooms and hits == want_hits and (want_it is None or it == want_it)
    (good if ok else bad).append((c, hits, rooms, np_, it, hp))
def runs(cs):
    cs = sorted(cs); out = []
    for c in cs:
        if out and c == out[-1][1] + 1: out[-1][1] = c
        else: out.append([c, c])
    return ', '.join(f'{a}' if a == b else f'{a}-{b}' for a, b in out)
print('good', len(good), 'bad', len(bad))
print('bad c:', runs([b[0] for b in bad]))
for b in sorted(bad)[:400]: print('  ', b)
