"""Find where a played line joins the TAS (same Ryu state as some TAS frame), then splice legalized TAS rows.
python -u work/l52b/sync.py F0 <rows spec or @file> --tas a-b [--state f.mst] [--hist file] [--upto G] [--out file] [--ov 'a-b=Row;..']
 Plays the rows from the state at F0; for each of our frames finds TAS frames in [a,b] with equal (X,xsub,y,vy,vy_sub,anim,rflags,coll).
 With --upto G: splices our rows to the first joined frame f (TAS g) + legalized TAS rows g+1..G (Enforcer), plays it and reports
 divergence vs the shifted TAS; --out writes the spliced rows (from F0+1)."""
import sys
sys.path.insert(0, 'work/l52p')
from lib import *
if os.environ.get('MINGB'):
    import fcka as _fk; d = list(_fk._init.__defaults__); d[-1] = float(os.environ['MINGB']); _fk._init.__defaults__ = tuple(d)
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
ST = opt('--state', ''); HIST = opt('--hist', ''); TAS = opt('--tas', ''); UPTO = opt('--upto', 0); OUT = opt('--out', ''); OV = opt('--ov', '')
JOIN = opt('--join', 0); LOOSE = opt('--loose', 0); FORCE = opt('--force', '')
F0 = int(a[0]); spec = a[1]
def rr(spec):
    out = []
    for part in [p for p in spec.split(',') if p]:
        r, n = part.split('*') if '*' in part else (part, '1')
        out += [row(r)] * int(n)
    return out
def load_rows(p):
    return [row(l.strip()) for l in open(p) if l.strip() and not l.startswith('#')]
rows = load_rows(spec[1:]) if spec.startswith('@') else rr(spec)
ta, tb = map(int, TAS.split('-'))
def want(f):
    w = set(T(f))
    if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
    if 'Left' in w and 'Right' in w: w -= {'Left'}
    return tuple(sorted(w))
hist = load_rows(HIST)[-1900:] if HIST else [want(f) for f in range(F0 - 300, F0 + 1)]
def key_m(m):
    X, y = XY(m)
    if LOOSE: return (X, m[0x85], y, m[0x80], m[0x84], m[0x8C]) + (() if m[0x8C] & 16 else (m[0x89], m[0x87]))
    return (X, m[0x85], y, m[0x89], m[0x87], m[0x80], m[0x84], m[0x8C])
def key_s(s):
    X, y = RXY(s)
    if LOOSE: return (X, s['xsub'], y, s['anim'], s['rflags'], s['coll']) + (() if s['coll'] & 16 else (s['vy'], s['vy_sub']))
    return (X, s['xsub'], y, s['vy'], s['vy_sub'], s['anim'], s['rflags'], s['coll'])
TK = {}
for g in range(ta, tb + 1):
    TK.setdefault(key_m(TM(g)), []).append(g)
fc = core(ST) if ST else core_at(F0)
fc.save('b'); fc._ka_slot = 'b'
_, st, _ = fc.step(rows, record='all')
join = None
for i, s in enumerate(st):
    f = F0 + 1 + i
    gs = TK.get(key_s(s))
    if gs:
        if join is None and (not JOIN or f >= JOIN): join = (f, gs[0])
        if i < 400 and (join and f <= join[0] + 3): print('match', f, '-> TAS', gs, 'lag', f - gs[0], flush=True)
if FORCE:
    join = tuple(map(int, FORCE.split(':')))
if not join:
    print('no join'); fc.close(); sys.exit()
f, g = join
print(f'JOIN our {f} = TAS {g}: lag {f - g}', flush=True)
if UPTO:
    ov = {}
    for part in [p for p in OV.split(';') if p]:
        k, v = part.split('=')
        x, y = (map(int, k.split('-')) if '-' in k else (int(k), int(k)))
        for q in range(x, y + 1): ov[q] = tuple(sorted(row(v)))
    ours = rows[:f - F0]
    en = A.Enforcer(hist + ours)
    tail = [tuple(sorted(en.emit(ov.get(q, want(q))))) for q in range(g + 1, UPTO + 1)]
    allr = ours + tail
    bad = legal_ok(allr, hist)
    print('legal:', bad or 'ok', flush=True)
    fc.load('b')
    _, st2, _ = fc.step(allr, record='all')
    lag = f - g; div = None; prev = None
    for i, s in enumerate(st2):
        q = F0 + 1 + i
        if q <= f: prev = s; continue
        tg = q - lag
        if div is None and key_s(s)[:3] != key_m(TM(tg))[:3]:
            div = q; print('DIVERGE at our', q, '(TAS', tg, ') ours', key_s(s), 'TAS', key_m(TM(tg)), flush=True)
        if prev and any(s[k] != prev[k] for k in ('hp65', 'np64', 'item', 'room6e')):
            print(q, 'TAS', tg, 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'rm', s['room6e'], flush=True)
        prev = s
    s = st2[-1]
    print('END', F0 + len(allr), 'X,y', RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'rm', s['room6e'], 'div', div, flush=True)
    if OUT:
        with open(OUT + '.tmp', 'w') as fo:
            fo.write(f'# sync {spec} join our {f} = TAS {g} lag {f-g}, TAS rows to {UPTO} (rows from frame {F0 + 1})\n')
            for r_ in allr: fo.write(P(r_) + '\n')
        os.replace(OUT + '.tmp', OUT)
fc.close()
