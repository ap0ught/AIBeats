CANDS = {}
for w in range(0, 6):
    for j in (2, 3):
        for m in range(3, 11):
            for k in range(1, 7):
                rows = rr(f'Left*{w}') + (rr(f'A+Right*{j},Left*{m}') * k)
                rows = (rows + rr('Left*90'))[:90]
                CANDS[f'w{w} j{j} m{m} k{k}'] = rows
