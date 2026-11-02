"""Mesen (run_batch, = NesHawk for the cutscene Start): from a state on the 5-4 kill row K (default TAS l61p_tas29314.mst, K 29314),
blank rows, a 2-f Start on K + 595 + k, then the 6-1 head-start rows from the 6-1 control (= load + 152).
Reports per k: control, c, hits / room changes relative to the control, TAS-equivalent or not.
python work/l61p/kscan.py [--mst file --kill K] [--ks 0-40] [--rows work/l61p/pre61_32595.txt]"""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
MST = opt('--mst', tas_mst(29314)); K = opt('--kill', 29314); KS = opt('--ks', '0-40'); RF = opt('--rows', 'work/l61p/pre61_32595.txt')
ks = list(range(int(KS.split('-')[0]), int(KS.split('-')[1]) + 1)) if '-' in KS else [int(x) for x in KS.split(',')]
HS = [row(l.strip()) for l in open(RF) if l.strip() and not l.startswith('#')]
fc = core(MST); fc.save('k'); fc._ka_slot = 'k'
good = []; bad = []
for k in ks:
    S = K + 595 + k
    pre = [()] * (S - K - 1) + [('Start',)] * 2 + [()] * 160
    st = fc.run_batch('k', [pre], record='all')[0].states
    load = next(K + 1 + i for i, s in enumerate(st) if s['st6d'] == 16); ctl = load + 152
    rows = [()] * (ctl - 1 - K)
    for f in (S, S + 1): rows[f - K - 1] = ('Start',)
    rows += HS
    st = fc.run_batch('k', [rows], record='all')[0].states
    c = st[ctl - K - 1]['bf']
    rel = lambda f: f - ctl + 1
    hits = [rel(K + 1 + i) for i in range(ctl - K, len(st)) if st[i]['hp65'] < st[i-1]['hp65']]
    rooms = [rel(K + 1 + i) for i in range(ctl - K, len(st)) if st[i]['room6e'] != st[i-1]['room6e']]
    ok = rooms == [1425, 2511] and hits == [2498]
    (good if ok else bad).append(k)
    print(f'k {k}: Start {S} load {load} control {ctl} c {c} hits(rel) {hits[:3]} rooms(rel) {rooms} {"OK" if ok else "BAD"}', flush=True)
print('good k', good); print('bad k', bad)
fc.close()
