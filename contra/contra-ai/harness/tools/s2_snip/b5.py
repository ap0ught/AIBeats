S = G["S"]; S.e.set_fields(bc.make_fields())
s = bc.State.parse(S.e.cmd("state"))
i = 15
out = []
for k in range(150):
    s = S.step(S.pad.fix(()), strict=False)
    if k % 6 == 0 or k < 4:
        out.append(f"{k}: r{s[f'er{i}']} hp{s[f'eh{i}']} s{s[f'es{i}']:02x} d{s[f'ed{i}']} v1={s[f'e1{i}']} ({s[f'ex{i}']},{s[f'ey{i}']}) vx={s[f'evx{i}']}.{s[f'efx{i}']} c{s[f'ec{i}']:02x} dead{s['death']}")
print("\n".join(out))
