"""Is each TAS 5-3 spin needed? From the TAS state before spin frame s, play the TAS pad bytes to s+N with the spin's B
replaced: 'slash' = Down added on the B frame (normal air sword, free), 'none' = B removed. Report hp drop, death, ninpo,
first divergence vs the TAS, and the room at the end.  python work/l53p/spintest.py [N]"""
import sys, glob
sys.path.insert(0, 'work/l53p')
from lib import *
N = int(sys.argv[1]) if len(sys.argv) > 1 else 90
SP = [26855, 27199, 27241, 27327, 27620, 27712, 27803, 28145, 28209, 28508, 28782]
have = sorted(int(p.split('tas')[-1].split('.')[0]) for p in glob.glob('states/mesen/l53p_tas*.mst'))
for s in SP:
    g = max(h for h in have if h < s)
    fc = core(tas_mst(g)); fc.save('b'); fc._ka_slot = 'b'
    base = [TM(k)[0x2A] for k in range(g + 1, s + N + 1)]
    i = s - g - 1
    var = {}
    v = list(base); v[i] = (base[i] & ~0x0F) | 0x04; var["slash"] = v          # Down+B only (no L/R: Down+Left+B would still spin)
    v = list(base); v[i] = base[i] & ~0x40; var['none'] = v          # no B
    v = list(base); var['tas'] = v
    rr = fc.run_batch('b', [var[k] for k in ('tas', 'slash', 'none')], record='all')
    out = []
    for k, r in zip(('tas', 'slash', 'none'), rr):
        st = r.states; hp0 = st[0]['hp65']; hpm = min(x['hp65'] for x in st); div = None
        for j, x in enumerate(st):
            f = g + 1 + j
            if div is None and RXY(x) != tas_xy(f): div = f
        e = st[-1]
        out.append(f'{k}: hpmin {hpm} end hp {e["hp65"]} np {e["np64"]} rm {e["room6e"]} X,y {RXY(e)} div {div}')
    print(f'spin {s} (rm {TM(s)[0x6E]} X,y {tas_xy(s)}) |', ' | '.join(out), flush=True)
    fc.close()
