"""Mesen grid over override variants of legalized TAS rows (agent l63p).
python work/l63p/grid.py F0 F1 'goal' --var 'spec1|spec2|...' [--tail Right] [--n 200] [--top 10] [--bf v] [--pre rowsfile]
  rows = legalized TAS rows F0+1..F1 with the variant's overrides ('a-b=Row;c=Row'), then the tail row up to n rows.
  --vars-file: one spec per line. goal: python expr on X, y, s, hp, rm, np, it. Prints the earliest goal frames."""
import sys
sys.path.insert(0, 'work/l63p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
VAR = opt('--var', ''); VF = opt('--vars-file', ''); TAIL = opt('--tail', 'Right'); N = opt('--n', 200); TOP = opt('--top', 10); BF = opt('--bf', -1)
LR = opt('--lr', 'R'); SHOW = opt('--show', '')
F0, F1 = int(a[0]), int(a[1]); G = compile(a[2], 'g', 'eval')
specs = [s for s in VAR.split('|')] if VAR else []
if VF: specs += [l.strip() for l in open(VF) if l.strip() and not l.startswith('#')]
if not specs: specs = ['']
def parse(OV):
    ov = {}
    for part in [p for p in OV.split(';') if p]:
        k, v = part.split('=')
        if '-' in k: x, y = map(int, k.split('-'))
        else: x = y = int(k)
        for f in range(x, y + 1): ov[f] = set(row(v))
    return ov
def want(f, ov):
    if f in ov: return ov[f]
    if f > F1: return set(row(TAIL))
    w = set(T(f))
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= ({'Left'} if LR == 'R' else {'Right'})
    return w
hist = [tuple(sorted(want(f, {}))) for f in range(F0 - 150, F0 + 1)]
cands = []
for sp in specs:
    ov = parse(sp)
    en = A.Enforcer(hist); rows = [tuple(sorted(en.emit(tuple(sorted(want(f, ov)))))) for f in range(F0 + 1, F0 + 1 + N)]
    bad = legal_ok(rows, hist)
    if bad: print('ILLEGAL', sp, bad); continue
    cands.append((sp, rows))
print('variants', len(specs), 'legal', len(cands), flush=True)
fc = core_at(F0)
if BF >= 0: fc.poke(0xBF, BF)
fc.save('b'); fc._ka_slot = 'b'
res = []
for i in range(0, len(cands), 64):
    rs = fc.run_batch('b', [c[1] for c in cands[i:i+64]], record='all')
    for (sp, rows), r in zip(cands[i:i+64], rs):
        hit = None
        for k, s in enumerate(r.states):
            X, y = RXY(s)
            if eval(G, dict(X=X, y=y, s=s, hp=s['hp65'], rm=s['room6e'], it=s['item'], np=s['np64'])):
                hit = (F0 + 1 + k, s['hp65'], s['np64'], s['item'], X, y); break
        if hit: res.append((hit, sp))
        if SHOW == sp:
            for k, s in enumerate(r.states):
                if k % 3 == 0: print(F0 + 1 + k, P(rows[k]), RXY(s), 'TAS', tas_xy(F0 + 1 + k), 'hp', s['hp65'], 'rm', s['room6e'])
res.sort()
for x in res[:TOP]: print(x, flush=True)
print('goal reached by', len(res), 'of', len(cands))
fc.close()
