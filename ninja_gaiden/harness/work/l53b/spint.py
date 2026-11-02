"""l53b: spin necessity. For each B press in rows (from mst at F0), variant 'none' (drop B for the press) and 'slash' (B+Down, no
direction, for the press). Reports hp/np at the end and the goal frame (first room change after F0 + 30).
python work/l53b/spint.py <mst> F0 rows.txt [pad]"""
import sys
sys.path.insert(0, 'work/l53p'); sys.path.insert(0, 'work/l53b')
from lb import *
src, F0, rf = sys.argv[1], int(sys.argv[2]), sys.argv[3]
pad = int(sys.argv[4]) if len(sys.argv) > 4 else 40
rows = [row(l.strip()) for l in open(rf) if l.strip() and not l.startswith('#')]
presses = []
for i, r in enumerate(rows):
    if 'B' in r and (i == 0 or 'B' not in rows[i-1]):
        j = i
        while j < len(rows) and 'B' in rows[j]: j += 1
        presses.append((i, j))
fc = core(src); fc.save('b'); fc._ka_slot = 'b'
def out(rr):
    st = fc.run_batch('b', [rr + [()] * pad], record='all')[0].states
    rm0 = st[0]['room6e']; gf = None
    for t, s in enumerate(st):
        if s['room6e'] != rm0: gf = F0 + 1 + t; break
    hits = [F0 + 1 + t for t in range(1, len(st)) if st[t]['hp65'] < st[t-1]['hp65']]
    return gf, st[-1]['hp65'], st[-1]['np64'], hits[:4]
print('base', out(rows), flush=True)
for i, j in presses:
    for name in ('none', 'slash'):
        rr = list(rows)
        for k in range(i, j):
            s = set(rr[k]) - {'B'}
            if name == 'slash': s = {'B', 'Down'} | (s - {'Left', 'Right', 'Up'})
            rr[k] = tuple(sorted(s))
        if legal_ok(rr): pass
        print(F0 + 1 + i, P(rows[i]), name, out(rr), flush=True)
fc.close()
