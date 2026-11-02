"""Chain room row files (each file = rows from its room's control frame = room change + 23) from a start state.
python -u work/l52b/chain.py F0 <file24> [<file25> <file26> ...] [--state f.mst] [--first-room 24] [--out rows.txt] [--poke a=v]
Starts at F0 (state after row F0; the first file's row 1 = row F0+1). After each file's rows, pads blank rows until the next
room change + 22, then plays the next file. Prints room changes, hp/np/item changes, the trigger ($5C 2->0 in the last room)
and Ryu's state at each control frame vs the TAS's. --out writes all rows (from F0+1)."""
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
ST = opt('--state', ''); OUT = opt('--out', ''); POKE = opt('--poke', ''); TAIL = opt('--tail', 0); SAVEST = opt('--savest', '')
F0 = int(a[0]); files = a[1:]
def load_rows(p):
    return [row(l.strip()) for l in open(p) if l.strip() and not l.startswith('#')]
fc = core(ST) if ST else core_at(F0)
for part in [p for p in POKE.split(';') if p]:
    k, v = part.split('='); fc.poke(int(k, 0), int(v, 0))
TAS_CTL = {24: 24897, 25: 25384, 26: 25841}
allr = []; f = F0
r0 = fc.ram(); room = r0[0x6E]
def ryu(m):
    X, y = XY(m); return (X, m[0x85], y, m[0x89], m[0x87], m[0x80], m[0x84], m[0x8C], m[0x65], m[0x64], m[0xC9])
chg = None   # frame of the last room change seen
for i, p in enumerate(files):
    rows = load_rows(p)
    if i > 0:
        while chg is None:
            _, st, _ = fc.step([()], record='last'); allr.append(()); f += 1
            if st[-1]['room6e'] != room:
                room = st[-1]['room6e']; chg = f
            if f - F0 > 5000: print('no room change'); sys.exit()
        print('room', room, 'change at', chg, flush=True)
        pad = chg + 22 - f
        if pad < 0: print('FILE OVERRUNS the room change by', -pad, flush=True); sys.exit()
        if pad: fc.step([()] * pad, record='last'); allr += [()] * pad; f += pad
        m = fc.ram()
        tc = TAS_CTL.get(room)
        if tc: print(f'control {f + 1} (room {room}) = TAS {tc} + {f + 1 - tc}: ours', ryu(m), 'TAS', ryu(TM(tc - 1)), flush=True)
        chg = None
    _, st, _ = fc.step(rows, record='all'); allr += rows
    prev = None
    for j, s_ in enumerate(st):
        g = f + 1 + j
        if s_['room6e'] != room and chg is None: chg = g; room = s_['room6e']
        if prev and any(s_[k] != prev[k] for k in ('hp65', 'np64', 'item', 'room6e', 'e5c')):
            print(g, 'X,y', RXY(s_), 'hp', s_['hp65'], 'np', s_['np64'], 'it', s_['item'], 'rm', s_['room6e'], '5c', s_['e5c'], flush=True)
        prev = s_
    f += len(rows)
if TAIL:
    _, st, _ = fc.step([()] * TAIL, record='all'); allr += [()] * TAIL
    prev = None
    for j, s in enumerate(st):
        g = f + 1 + j
        if prev and any(s[k] != prev[k] for k in ('hp65', 'np64', 'item', 'room6e', 'e5c')):
            print(g, 'X,y', RXY(s), 'hp', s['hp65'], 'np', s['np64'], 'it', s['item'], 'rm', s['room6e'], '5c', s['e5c'], flush=True)
        prev = s
    f += TAIL
print('END', f, flush=True)
if SAVEST:
    fc.save('z'); fc.save_file('z', SAVEST, frame=f); print('saved', SAVEST, 'frame', f)
if OUT:
    with open(OUT + '.tmp', 'w') as fo:
        fo.write(f'# chain from frame {F0 + 1}: {" ".join(files)}\n')
        for r_ in allr: fo.write(P(r_) + '\n')
    os.replace(OUT + '.tmp', OUT)
fc.close()
