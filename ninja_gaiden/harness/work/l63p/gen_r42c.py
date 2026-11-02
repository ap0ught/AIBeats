CANDS = {}
for m1 in range(4, 15):
    for m2 in range(4, 15):
        for k in range(1, 5):
            for w in (0, 2):
                rows = rr(f'Right*{w}') + rr(f'A+Left*2,Left*{m1},A+Right*2,Right*{m2}') * k + rr('A+Left*2') + rr('Left*120')
                CANDS[f'w{w} m1 {m1} m2 {m2} k{k}'] = rows[:120]
