for k in (4, 5):
    R = G.get(f"R{k}")
    print(k, R, R.plan if R else None)
S = G["S"]
print("rows", len(S.rows), {k: S.s[k] for k in ("frame","screen","x","y","cores","loc")})
