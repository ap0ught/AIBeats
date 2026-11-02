"""Full r2c line for a list of spawn BF values (Mesen): end frame, room entries, hits vs the unpoked base.
python work/l41p/fullchk.py b1 b2 ..."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
d = open('work/l41p/r2c_ram.bin', 'rb').read()[4:]; rows = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
def run(bf):
    fc.load('s')
    if bf is not None: fc.poke(0xBF, bf)
    fc.save('p')
    return fc.run_batch('p', [rows], record='all', stops=[(0x6D, 'changed', 0)])[0].states
def kk(s): return (C.abs_x(s), s['y'], s['room'], s['hp'])
def summ(st):
    r14 = next((14570 + i for i, s in enumerate(st) if s['room'] == 14), None)
    r15 = next((14570 + i for i, s in enumerate(st) if s['room'] == 15), None)
    hits = [(14570 + i, s['hp']) for i, s in enumerate(st) if i and s['hp'] < st[i-1]['hp']]
    return r14, r15, 14569 + len(st), hits, st[-1]['ninpo'], st[-1]['item']
base = run(None)
print('base', summ(base), flush=True)
for b in [int(v) for v in sys.argv[1:]]:
    st = run((b - 448) & 255)
    div = next((14570 + i for i, (s, t) in enumerate(zip(st, base)) if kk(s) != kk(t)), None)
    print('spawnBF', b, 'ryu-div', div, 'IDENTICAL' if div is None and len(st) == len(base) else '', summ(st), flush=True)
fc.close()
