import sys; sys.path.insert(0, 'work/l52a')
from lib2 import *
pre = rows_file('work/l52p/pre52_24625.txt'); print('rows', len(pre))
h = chain_hist(); print('legal', repr(legal_ok(pre, h)))
fc = core(BASE52)
r = fc.run_batch('s', [pre], record='all')[0]
bad = 0
for i, s in enumerate(r.states):
    f = CTL52 + i; t = TM(f - OFF)
    a = RXY(s) + (s['hp65'], s['np64'], s['item']); b = XY(t) + (t[0x65], t[0x64] - 5 + 0, t[0xC9])
    if a[:3] != b[:3] or a[4] != b[4]:
        bad += 1
        if bad < 10: print('DIFF', f, a, b)
s = r.states[-1]; print('end', CTL52 + len(pre) - 1, RXY(s), s['hp65'], s['np64'], s['item'], 'bad', bad)
fc.save('e'); fc.save_file('e', 'states/mesen/l52a_pre_25196.mst', CTL52 + len(pre) - 1)
fc.close()
