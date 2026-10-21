"""Track K2: is room 1 invariant under a time shift of snake 3?  K6 with a jump in the idle wait (index 1100) that delays the
tail of snake 2 by j frames, then K6[1150:] shifted by j: does the toad get captured j frames later?"""
import sys
from u17k_sim import *
k6 = seg("K6")
s = Sim("u17k_shift.log")
tr0 = s.set_base(k6, 1992, every=50)
print("K6: tgone", tr0["tgone"], "happ", tr0["happ"], "tail pauses", [p for p in tr0["tp"] if p > 1060])
for spec in sys.argv[1:]:
    extra = parse(spec)
    ins = k6[:1090] + extra + [""] * (60 - len(extra))      # 1090..1150 replaced
    tr = s.run(ins + [""] * 200, 1300, stop=lambda t: len(t["tgone"]) >= 2)
    if len(tr["tgone"]) < 2:
        print(spec, "tail never gone", tr["toad"]); continue
    j = tr["tgone"][1] - tr0["tgone"][1]
    full = ins + [""] * j + k6[1150:1992] if j >= 0 else None
    tr2 = s.run(full + [""] * 60, 1992 + j + 20, stop=lambda t: len(t["happ"]) >= 4)
    print(f"{spec}: tail gone {tr['tgone'][1]} (shift {j}), toad then {tr['toad']}; shifted replay: happ {tr2['happ']} tgone {tr2['tgone']} "
          f"head pauses>1200 {[p - j for p in tr2['hp'] if p > 1200]} tail pauses>1150 {[p - j for p in tr2['tp'] if p > 1150]} toad {tr2['toad']} hpmin {tr2['hp_min']}")
s.close()
