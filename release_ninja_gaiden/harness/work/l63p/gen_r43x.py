PRE = [l.strip() for l in open('work/l63p/b_r43j_last.txt') if not l.startswith('#')]
CANDS = {}
for cut in range(112, 132, 2):   # rows from 36281; cut 112 -> through 36392
    pre = [row(x) for x in PRE[:cut]]
    for w in range(0, 12, 2):
        for g in range(4, 30, 2):
            rows = pre + rr(f'Left*{w},A+Left*2') + rr(f'Left*{g - 2},A+Left*2') + rr('Left*80')
            CANDS[f'cut{cut} w{w} g{g}'] = rows[:200]
