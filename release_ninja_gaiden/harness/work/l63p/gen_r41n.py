CANDS = {}
for a in range(0, 13):
    for d in range(10, 34, 2):
        for c in (0, 1):
            rows = rr(f'Right*{a},A+Right*2') + rr(f'Right*{d - 2}') + rr('A+Right*2') + rr('Right*80')
            if c: rows = rr(f'Right*{a},A+Right*2,-*2') + rr(f'Right*{d - 4}') + rr('A+Right*2') + rr('Right*80')
            CANDS[f'a{a} d{d} c{c}'] = rows[:75]
