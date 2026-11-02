PRE = [l.strip() for l in open('work/l63p/b_r42y_last.txt') if not l.startswith('#')]
CANDS = {}
for cut in (30, 36, 42, 48):
    pre = [row(x) for x in PRE[:cut]]
    for w in (0, 2, 4):
        for j in (2, 3):
            for m in range(3, 11):
                for k in range(1, 5):
                    rows = pre + rr(f'Left*{w}') + rr(f'A+Right*{j},Left*{m}') * k + rr('Left*80')
                    CANDS[f'cut{cut} w{w} j{j} m{m} k{k}'] = rows[:130]
