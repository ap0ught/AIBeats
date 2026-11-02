import sys
sys.path.insert(0, 'work/l53p')
from lib import *
fc = core_at(28843); fc.save('b'); fc._ka_slot = 'b'
R = ('Right',); S = ('Start',)
base = [()] * 23 + [R] * (29099 - 28867 + 1)
for k in range(1, 9):
    rows = base + [()] * (k - 1) + [S, S] + [()] * 200
    st = fc.run_batch('b', [rows], record='all')[0].states
    ch = hp = None
    for i, s in enumerate(st):
        f = 28844 + i
        if hp is None and s['hp65'] == 16: hp = f
        if ch is None and s['room6e'] == 34: ch = f
    print(f'Start at trigger+{k} ({29099 + k}): hp16 {hp} room34 {ch}')
# TAS-shaped: blank 29098
rows = [()] * 23 + [R] * (29097 - 28867 + 1) + [(), R] + [()] * 5 + [S, S] + [()] * 200
st = fc.run_batch('b', [rows], record='all')[0].states
print('TAS shape room34', next(28844 + i for i, s in enumerate(st) if s['room6e'] == 34))
fc.close()
