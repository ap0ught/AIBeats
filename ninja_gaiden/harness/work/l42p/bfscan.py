"""$BF poke scan at 4-2 control (Mesen). python work/l42p/bfscan.py <dump.bin> <state.mst> <out> [bf list a-b or csv]
Plays the dump's NesHawk effective pads from the state with $BF poked; per bf: first Ryu divergence vs the unpoked base,
first enemy divergence (slot/type), stage-end frame, hp/np/item at the end."""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
dump, mst, outp = sys.argv[1:4]
spec = sys.argv[4] if len(sys.argv) > 4 else '0-255'
if '-' in spec: a, b = map(int, spec.split('-')); bfs = list(range(a, b + 1))
else: bfs = [int(v) for v in spec.split(',')]
d = open(dump, 'rb').read(); f0 = int.from_bytes(d[:4], 'little'); d = d[4:]
pads = bytes(d[i*2048 + 0x2A] for i in range(len(d)//2048))
FL = {'x': 0x86, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'hp': 0x65, 'np': 0x64, 'it': 0xC9, 'st': 0x6D, 'rm': 0x6E,
      'en': 0x73, 'BF': 0xBF, 'pad': 0x2A}
for j in range(8):
    FL[f't{j}'] = 0x400 + j; FL[f's{j}'] = 0x410 + j; FL[f'ex{j}'] = 0x460 + j; FL[f'ey{j}'] = 0x480 + j
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(mst, 'rb').read()); fc._ka_slot = 's'
def run(bf):
    fc.load('s')
    if bf is not None: fc.poke(0xBF, bf)
    fc.save('p')
    r = fc.run_batch('p', [pads], record='all', stops=[(0x6D, 'changed', 0)])[0]
    return r.states if hasattr(r, 'states') else r[2]
def X(s): return s['sh']*256 + s['sl'] + s['x']
def ek(s, j):
    if not (s['en'] >> j & 1): return None
    return (s[f't{j}'], s[f's{j}'], s[f'ex{j}'] + s['sl'] + 256*s['sh'], s[f'ey{j}'])
base = run(None)
out = open(outp, 'w')
def summ(st):
    hits = [(f0 + 1 + i, s['hp']) for i, s in enumerate(st) if i and s['hp'] < st[i-1]['hp']]
    return f0 + len(st), st[-1]['hp'], st[-1]['np'], st[-1]['it'], hits
print('base end/hp/np/item/hits', summ(base), 'BF@ctl', base[0]['BF'] - 1, file=out, flush=True)
for bf in bfs:
    st = run(bf)
    rd = next((f0 + 1 + i for i, (s, t) in enumerate(zip(st, base)) if (X(s), s['y'], s['hp']) != (X(t), t['y'], t['hp'])), None)
    ed = []
    seen = set()
    for i, (s, t) in enumerate(zip(st, base)):
        if rd is not None and f0 + 1 + i >= rd: break
        for j in range(8):
            if ek(s, j) != ek(t, j) and j not in seen:
                seen.add(j); ed.append((f0 + 1 + i, j, ek(t, j), ek(s, j)))
    print(f'bf {bf:3d} ryu-div {rd} end/hp/np/item/hits {summ(st)} en-div {ed[:4]}', file=out, flush=True)
fc.close()
