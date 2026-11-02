import sys; sys.path.insert(0, 'work/l51a')
from lib import *
for fn in sys.argv[1:]:
    tr = trace(rows_file(fn)); trig = None; hp = None; ev = []
    for t in tr:
        if hp is not None and t[3] != hp: ev.append((t[0], t[1], t[2], t[3]))
        hp = t[3]
        if trig is None and t[9] == 0 and t[0] > 24000: trig = t[0]
    l = tr[-1]
    print(fn, 'trigger', trig, 'end', l[:6], 'hp changes after 24404', [e for e in ev if e[0] > 24404])
