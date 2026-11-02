"""Fast $BF scan at the TAS 4-1 control state (Mesen, NesHawk pads of a RAM dump). Phase 1: play to frame CHK and
compare Ryu + enemy RAM with the unpoked run; equal -> identical to the base line (the tosser is the only $BF reader).
Otherwise play the full line. python work/l41p/bfscan2.py <dump.bin> [chk=15210] [a b]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
from ng.solve import common as C
rf = sys.argv[1]; CHK = int(sys.argv[2]) if len(sys.argv) > 2 else 15210
a, b = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, 255)
d = open(rf, 'rb').read()[4:]; rows = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
fc = F.FastCore(boot_rows=None, ticks=True); fc.put('s', open('states/mesen/l41p_tas14569.mst', 'rb').read()); fc._ka_slot = 's'
n1 = CHK - 14569
def prep(bf):
    fc.load('s')
    if bf is not None: fc.poke(0xBF, bf)
    fc.save('p')
def key(m):
    return bytes(m[0x60:0x67]) + bytes(m[0x80:0x9F]) + bytes(m[0xC0:0xCA]) + bytes([m[0x73]]) + bytes(m[0x400:0x498])
prep(None)
kb = key(fc.run_batch('p', [rows[:n1]], record='last', record_ram=True)[0].ram)
def summ(st):
    r14 = r15 = None; hits = []; hp = 16
    for i, s in enumerate(st):
        f = 14570 + i
        if r14 is None and s['room'] == 14: r14 = f
        if r15 is None and s['room'] == 15: r15 = f
        if s['hp'] < hp: hits.append((f, s['hp'], C.abs_x(s), s['y']))
        hp = s['hp']
    return r14, r15, 14569 + len(st), hits, st[-1]['ninpo'], st[-1]['item']
prep(None)
base = fc.run_batch('p', [rows], record='all', stops=[(0x6D, 'changed', 0)])[0].states
print('base', summ(base), flush=True)
def kk(s): return (C.abs_x(s), s['y'], s['room'], s['hp'])
for bf in range(a, b + 1):
    prep(bf)
    k = key(fc.run_batch('p', [rows[:n1]], record='last', record_ram=True)[0].ram)
    sb = (bf + 448) & 255
    if k == kb:
        print(f"bf@ctl {bf:3d} spawnBF {sb:3d} SAME at {CHK}", flush=True); continue
    prep(bf)
    st = fc.run_batch('p', [rows[:15700 - 14569]], record='all', stops=[(0x6D, 'changed', 0)])[0].states
    div = next((14570 + i for i, (s, t) in enumerate(zip(st, base)) if kk(s) != kk(t)), None)
    dp = kk(st[div - 14570]) if div else None
    hits = [h for h in summ(st)[3]]
    print(f"bf@ctl {bf:3d} spawnBF {sb:3d} DIFF ryu-div {div} {dp} to15700 hits {hits} item {st[-1]['item']} np {st[-1]['ninpo']}", flush=True)
fc.close()
