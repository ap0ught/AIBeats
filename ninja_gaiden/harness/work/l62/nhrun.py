"""l62: NesHawk replay of a power-on file from a NesHawk state; events, pad conflicts, position check vs TAS (shift D), saves states.
python work/l62/nhrun.py file state F1 F2 D [--save f1,f2,...] [--tag l62] [--cmp TASframe]"""
import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l61p')
from ng.solve import common as C
from ng.mode import TICKS
from ng.inputs import read_inputs
from lib0 import TM, XY
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
SV = [int(x) for x in opt('--save', '').split(',') if x]; TAG = opt('--tag', 'l62'); CMP = opt('--cmp', 0); NOPOS = opt('--nopos', 0)
FN, ST, F1, F2, D = a[0], a[1], int(a[2]), int(a[3]), int(a[4])
BIT = {'A': 0x80, 'B': 0x40, 'Select': 0x20, 'Start': 0x10, 'Up': 0x08, 'Down': 0x04, 'Left': 0x02, 'Right': 0x01}
R = [tuple(r) for r in read_inputs(FN)]
e = C.open_emu(f'{TAG}_nhrun.log')
try:
    e.tick(TICKS)
    st = e.load(ST); f0 = st['frame']; print('state', ST, 'frame', f0, flush=True)
    rams = []; f = f0
    cuts = sorted(set([x for x in SV if f0 < x <= F2] + [F2]))
    for c in cuts:
        _, rr = e.run_ram(R[f:c]); rams += rr; f = c
        if c in SV: e.save(f'{TAG}_{c}'); print('saved', f'{TAG}_{c}', flush=True)
    prev = None; conf = []; divs = []
    for i, m in enumerate(rams):
        fr = f0 + 1 + i
        r = R[fr - 1]; want = sum(BIT[b] for b in r)
        if fr >= F1 and m[0x2A] != want: conf.append((fr, '+'.join(r), m[0x2A], want))
        if prev is not None and fr >= F1:
            ev = []
            for ad, nm in ((0x6E, 'room'), (0x6D, 'stage'), (0x65, 'hp'), (0x64, 'np'), (0xC9, 'item')):
                if m[ad] != prev[ad]: ev.append(f'{nm} {prev[ad]}->{m[ad]}')
            if ev: print(fr, 'X,y', XY(m), ev)
            if D and not NOPOS and F1 <= fr and fr - D > 29261 and fr - D <= 34760:
                bad = XY(m) != XY(TM(fr - D))
                if bad and (not divs or divs[-1][1] != fr - 1): divs.append([fr, fr])
                elif bad: divs[-1][1] = fr
        prev = m
    print('pad-read conflicts', len(conf), conf[:20])
    K3 = next((f0 + 1 + i for i, r in enumerate(rams) if r[0x6D] == 21 and r[0x66] == 0 and r[0x5C] != 0), None)
    Pf = next((f0 + 1 + i for i, r in enumerate(rams) if K3 and f0 + 1 + i > K3 and r[0x6D] == 21 and r[0x63] == 0), None)
    Ef = next((f0 + 1 + i for i, r in enumerate(rams) if Pf and f0 + 1 + i > Pf and r[0x3E] == 1), None)
    if Pf: print('6-5 kill', K3, 'P', Pf, 'E', Ef, 'END seen', Ef + 1 if Ef else None)
    for i, r in enumerate(rams):
        if r[0x6E] == 35 and i and rams[i-1][0x6E] != 35: print('DEATH -> 6-1 at', f0 + 1 + i)
    print('position divergence ranges vs TAS (shift %d):' % D, divs[:30])
    m = rams[-1]; print('end', F2, 'X,y', XY(m), 'hp', m[0x65], 'np', m[0x64], 'item', m[0xC9], 'room', m[0x6E], 'BF', m[0xBF])
    open(f'work/l62/{TAG}_{F2}.ram', 'wb').write(m)
    if CMP:
        t = TM(CMP); print('RAM diffs vs TAS', CMP, [(hex(x), m[x], t[x]) for x in range(0x800) if m[x] != t[x] and not 0x100 <= x < 0x300][:60])
finally:
    e.close()
