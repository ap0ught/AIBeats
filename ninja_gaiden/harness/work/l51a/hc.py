"""Hill climb on an event list over a TAS window (after a prefix), legalized via Enforcer.
Rows in [T0, END] (TAS axis, lag LG): Right, plus events: (t,'A') A+Right, (t,'B') B+Right, (t,'L') Left x2, (t,'-') blank x2,
(t,'BL') B+Left x2. Before T0 / outside: TAS rows as in rep.py.  Score: no hit (or allowed), no death, X at END, np >= NPMIN.
python -u work/l51a/hc.py <prefix> <N> <LG> <T0> <END> <tag> --ev "22647:A,22655:B,..." [--npmin 30] [--rounds 6]"""
import sys, time, itertools; sys.path.insert(0, 'work/l51a')
from rep import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
EVS = opt('--ev', ''); NPMIN = opt('--npmin', 0); ROUNDS = opt('--rounds', 6); ADD = opt('--add', 1); ITEM = opt('--item', 130); BW = opt('--bird', ''); ADDLO = opt('--addlo', 0); ADDHI = opt('--addhi', 10**6); ADDK = opt('--addk', 'B,A,-').split(',')
import rep as _rep
NH = opt('--needhit', ''); ORDER2 = opt('--order2', 0); DEADX = opt('--deadx', 0)
NEEDHIT = tuple(int(x) for x in NH.split(',')) if NH else None
if NEEDHIT: _rep.HITOK = NEEDHIT[0]
EMP = opt('--empty', 0); SFR = opt('--sf', 0)
if SFR: _rep.SF = SFR
if EMP: _rep.EMPTY = EMP
if BW: _rep.BIRD = tuple(int(x) for x in BW.split(','))
pf, N, LG, T0, END, TAG = a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4]), a[5]
R = Rep(pf, N, LG, END)
KR = {'A': [{'A', 'Right'}], 'B': [{'B', 'Right'}], 'L': [{'Left'}, {'Left'}], '-': [set(), set()], 'BL': [{'B', 'Left'}, {'B', 'Left'}],
      'R-': [set()]}
def ov_of(evs):
    o = {t: {'Right'} for t in range(T0, END + 1)}
    for t, k in sorted(evs):
        for i, w in enumerate(KR[k]): o[t + i] = set(w)
    return o
def ev(evs):
    r = R.run(ov_of(evs))
    dead = r['dead'] is not None; hit = r['hit'] is not None
    last = r['last']; X = last[1] if (not dead or DEADX) else -999; np_ = last[4]
    if SFR and r['sfx'] is not None: X = r['sfx']
    it_ok = last[5] == ITEM and (r['bird'] is not None or not BW)
    if EMP: it_ok = it_ok and bool(r['empty'])
    if NEEDHIT: it_ok = it_ok and any(NEEDHIT[0] <= h[0] <= NEEDHIT[1] for h in r['hits'])
    if ORDER2: return (not dead, not hit, np_ >= NPMIN and it_ok, X, np_), r
    return (not dead, np_ >= NPMIN and it_ok, not hit, X, np_), r
if EVS:
    evs = tuple(sorted((int(t), k) for t, k in (x.split(':') for x in EVS.split(','))))
else:
    evs = []; prev = set()
    for t in range(T0 - 1, END + 1):
        w = set(T(t))
        if t >= T0:
            if 'A' in w and 'A' not in prev: evs.append((t, 'A'))
            if 'B' in w and 'B' not in prev: evs.append((t, 'B'))
            if 'Left' in w and 'Right' not in w and 'Left' not in prev: evs.append((t, 'L'))
        prev = w
    evs = tuple(evs)
best, r = ev(evs); t0 = time.time()
print('start', evs, best, r, flush=True)
for rd in range(ROUNDS):
    improved = False
    cands = []
    for i, (t, k) in enumerate(evs):
        rest = evs[:i] + evs[i+1:]
        cands.append(rest)
        for d in (-3, -2, -1, 1, 2, 3):
            cands.append(tuple(sorted(rest + ((t + d, k),))))
    if ADD:
        for t in range(max(T0, ADDLO), min(END - 2, ADDHI)):
            for k in ADDK:
                cands.append(tuple(sorted(evs + ((t, k),))))
    for c in cands:
        s2, r2 = ev(c)
        if s2 > best:
            best, evs, r = s2, c, r2; improved = True
            print(f'rd {rd} better {best} {r2["last"]} evs {evs} {time.time()-t0:.0f}s', flush=True)
    if not improved: break
print('FINAL', best, r, 'evs', ','.join(f'{t}:{k}' for t, k in evs), flush=True)
rr = R.run(ov_of(evs), keep=True)
print('legal', legal_ok(rr['rows']) or 'ok')
wr(f'work/l51a/hc_{TAG}.txt', rr['rows'], f'hc {sys.argv[1:]} evs {evs}')
