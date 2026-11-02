"""first-reach comparison of two traces (ours vs TAS) for a rightward/leftward stage by abs X columns.
    python work/c5/trcmp.py <our trace> <our c0> <tas c0> <stage idx> <col> [left]"""
import csv, sys
def reach(name, c0, stage, col, left):
    first = {}
    hp = {}
    for r in csv.DictReader(open(name)):
        f = int(r['row'])
        if f <= c0 or f > c0 + 4000 or int(r['stage']) != stage:
            continue
        scr = int(r['scroll_scr']); scr = scr - 256 if scr >= 128 else scr
        X = scr * 256 + int(r['scroll']) + int(r['x'])
        k = (int(r['room']), (X // col) if not left else -(X // col))
        if k not in first:
            first[k] = (f - c0, int(r['hp']), int(r['ninpo']))
    return first
ours, c0, tc0, st, col = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
left = len(sys.argv) > 6
a = reach(ours, c0, st, col, left); b = reach('logs/tas4751.trace.csv', tc0, st, col, left)
keys = sorted(set(a) | set(b))
best = {}
for k in keys:
    if k in a and k in b:
        print(k, 'ours', a[k], 'tas', b[k], 'diff', a[k][0] - b[k][0])
