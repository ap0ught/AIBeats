"""Poke $BF at the TAS 4-1 control state (frame 14569, TAS $BF 217) to every value and replay a rows file (default
logs/a34/4-1_r2c, which is in exact TAS sync to 15540). Report the first divergence from the unpoked run, hits, room
entries and the end. python work/l41p/bfscan.py [rows] [first_bf last_bf]"""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
rf = sys.argv[1] if len(sys.argv) > 1 else 'logs/a34/4-1_r2c.inputs.txt'
a, b = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 255)
if rf.endswith('.bin'):
    d = open(rf, 'rb').read()[4:]; rows = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))  # NesHawk pads from a RAM dump
else:
    rows = C.rows_of(rf)
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
fc.load('s')
stops = [(0x6D, 'changed', 0)]
def run(bf):
    fc.load('s')
    if bf is not None: fc.poke(0xBF, bf)
    fc.save('p')
    return fc.run_batch('p', [rows], record='all', stops=stops)[0].states
base = run(None)
def key(s): return (C.abs_x(s), s['y'], s['room'], s['hp'], s['ninpo'], s['item'])
def summ(st):
    r14 = r15 = None; hits = []; hp = 16
    for i, s in enumerate(st):
        f = 14570 + i
        if r14 is None and s['room'] == 14: r14 = f
        if r15 is None and s['room'] == 15: r15 = f
        if s['hp'] < hp: hits.append((f, s['hp'])); 
        hp = s['hp']
    return r14, r15, 14569 + len(st), hits, st[-1]['ninpo'], st[-1]['item']
print('base', summ(base), flush=True)
for bf in range(a, b + 1):
    st = run(bf)
    div = next((14570 + i for i, (s, t) in enumerate(zip(st, base)) if key(s) != key(t)), None)
    r14, r15, end, hits, np_, it = summ(st)
    dpos = None
    if div is not None:
        i = div - 14570; s = st[i]; dpos = (C.abs_x(s), s['y'], s['hp'])
    print(f"bf@ctl {bf:3d} spawnBF {(bf + 448) & 255:3d} div {div} {dpos} r14 {r14} r15 {r15} end {end} np {np_} item {it} hits {hits}", flush=True)
fc.close()
