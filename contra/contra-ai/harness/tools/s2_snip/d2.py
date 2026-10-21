R = G["R4"]
for en in R.ents[7:]:
    ts = sorted(en.track)
    print(en, [ (T, en.track[T]) for T in ts[:3] ], "...", [(T, en.track[T]) for T in ts[-2:]])
