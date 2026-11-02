import sys
sys.path.insert(0, 'work/l44p')
from lib import *
fc = core(PRE)
for tag, v in (('d0', 5), ('d0', 22), ('d1', 24), ('d2', 25), ('t150', 40)):
    w = [tuple(sorted(r)) for r in C.rows_of(f'work/l44p/k44_{tag}.txt')] + [('Right',)] * 3
    fc.load('s'); fc.poke(0x62, v); fc.save('v')
    st = fc.run_batch('v', [w], record='all')[0].states
    n = len(w) - 3
    print(tag, v, 'row', n + 1, '62', st[n]['t62'], 'x', st[n]['x86'], 'prev x', st[n - 1]['x86'], '62 prev', st[n - 1]['t62'])
fc.close()
