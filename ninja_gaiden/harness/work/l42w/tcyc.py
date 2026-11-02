"""Play row specs from a state and print Ryu per frame. python work/l42w/tcyc.py <mst> "<pre spec>" "<spec>" ...
spec tokens: buttons letters R L U D A B (- = none), :n repeat. e.g. "R:26" "R RU RU ALU AL"x """
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka
from ng import fastcore as F
M = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}
def spec(s):
    out = []
    for tok in s.split():
        k, n = tok.split(':') if ':' in tok else (tok, '1')
        out += [tuple(sorted(M[c] for c in k if c != '-'))] * int(n)
    return out
FL = {'x': 0x86, 'xsub': 0x85, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'vy': 0x89, 'coll': 0x8C, 'anim': 0x80, 'hp': 0x65,
      'np': 0x64, 'c5': 0x5C, 'rf': 0x84, 'it': 0xC9}
fc = F.FastCore(boot_rows=None, ticks=True, fields=FL)
fc.put('s', open(sys.argv[1], 'rb').read()); fc._ka_slot = 's'
pre = spec(sys.argv[2])
for sp in sys.argv[3:]:
    rows = pre + spec(sp)
    r = fc.run_batch('s', [rows], record='all')[0]
    print('==', sp)
    for i, (s, w) in enumerate(zip(r.states, rows)):
        if i < len(pre) - 3: continue
        print(i + 1, '+'.join(w) or '-', 'X', s['sh']*256 + s['sl'] + s['x'], 'y', s['y'], 'vy', s['vy'], 'coll', s['coll'], 'anim', s['anim'], 'rf', s['rf'], 'hp', s['hp'], 'np', s['np'], 'it', s['it'], '5C', s['c5'])
fc.close()
