"""prefix rows (from TAS frame F0+1) + legalized TAS rows T1..T2 appended (lag = len(prefix) - (T1 - F0 - 1)); trace room changes, hp,
first divergence from the TAS path shifted by the lag. python work/l61p/shift.py F0 prefix T1 T2 [--lags -2,-1,0,1,2]"""
import sys
sys.path.insert(0, 'work/l61p')
from lib import *
a = sys.argv[1:]
LG = [0]
if '--lags' in a: i = a.index('--lags'); LG = [int(x) for x in a[i+1].split(',')]; del a[i:i+2]
F0, PF, T1, T2 = int(a[0]), a[1], int(a[2]), int(a[3])
pre = [row(l.strip()) for l in open(PF) if l.strip() and not l.startswith('#')]
fc = core_at(F0); fc.save('b'); fc._ka_slot = 'b'
for dl in LG:
    p = pre[:len(pre) + dl] if dl <= 0 else pre + [pre[-1]] * dl
    lag = len(p) - (T1 - F0 - 1)
    tail = legalize_tas(T1, T2, list(p)[-150:])
    rows = p + tail
    st = fc.run_batch('b', [rows], record='all')[0].states
    div = None; ev = []
    for i, s in enumerate(st):
        f = F0 + 1 + i
        if i and s['room6e'] != st[i-1]['room6e']: ev.append(f'room {s["room6e"]} @{f} (TAS+{f - 0})')
        if i and s['hp65'] < st[i-1]['hp65']: ev.append(f'hit {st[i-1]["hp65"]}->{s["hp65"]} @{f}')
        if i >= len(p) and div is None and RXY(s) != tas_xy(f - lag): div = (f, f - lag, RXY(s), tas_xy(f - lag))
    print(f'dl {dl} lag {lag} legal {legal_ok(rows) or "ok"} div {div} end {RXY(st[-1])} rm {st[-1]["room6e"]} hp {st[-1]["hp65"]}', ev[:6], flush=True)
fc.close()
