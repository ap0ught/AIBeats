import contra.stages.base_room as br
S = G["S"]; S.e.set_fields(bc.make_fields())
tr, dead = br.record_room(S, G["snap_room4"], 260)
for T in list(range(192, 200)) + list(range(200, 260, 6)):
    s = tr[T]
    print(T, " ".join(f"[{i}:t{s[f'et{i}']:02x} r{s[f'er{i}']} p{s[f'ep{i}']} s{s[f'es{i}']:02x} hp{s[f'eh{i}']} ({s[f'ex{i}']},{s[f'ey{i}']}) d{s[f'ed{i}']} a{s[f'ea{i}']:02x}]" for i in (6,7,8,9)))
