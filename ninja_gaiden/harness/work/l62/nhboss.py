"""l62: NesHawk boss chain. From NesHawk state ST (frame f0) play stage rows RF (row i = frame 35,799 + i) up to the 6-3 trigger
($5C 4 in room 44), then: Start T+5/T+6 -> 6-4a; MD rows; earliest Start after the kill (scan) -> 6-4b; JQ rows; earliest Start (+ delay d
chosen with l65's pick for the 6-5 arrival) -> 6-5; demon line; END seen (P = $63 0 after the kill, E = first $3E 1 after P, seen E+1).
Writes OUT_rows (from 35,799 to the last demon row) and OUT_poweron. python work/l62/nhboss.py ST RF OUT_rows OUT_poweron [--md file]
[--jq file] [--dmax 60] [--dfix d]"""
import sys, os
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l62'); sys.path.insert(0, 'work/l65')
from ng.solve import common as C
from ng.mode import TICKS
import pick
a = sys.argv[1:]
def opt(n, d):
    if n in a:
        i = a.index(n); v = a[i+1]; del a[i:i+2]; return type(d)(v)
    return d
MD = opt('--md', 'work/l63p/md_js10.txt'); JQ = opt('--jq', 'work/l63p/jq_r4k2_kill.txt'); DMAX = opt('--dmax', 60); DFIX = opt('--dfix', -1)
ST, RF, OR, OP = a[0], a[1], a[2], a[3]
def rf(p):
    L = open(p).read().split(chr(10))
    if L and L[-1] == '': L = L[:-1]
    return [() if l.strip() in ('', '-') else tuple(sorted(l.strip().split('+'))) for l in L if not l.startswith('#')]
F0 = 35799
rows = rf(RF)
e = C.open_emu('l62_nhboss.log')
def run(w):
    _, rams = e.run_ram(w); return rams
try:
    e.tick(TICKS)
    st = e.load(ST); f0 = st['frame']; print('state', ST, f0, flush=True)
    # 1. trigger
    rams = run(rows[f0 - F0 + 1:])
    T = next(f0 + 1 + i for i, r in enumerate(rams) if r[0x6E] == 44 and r[0x5C] == 4)
    rT = rams[T - f0 - 1]; print('trigger', T, 'hp', rT[0x65], 'np', rT[0x64], 'item', rT[0xC9], flush=True)
    rows = rows[:T - F0 + 1]
    e.load(ST); run(rows[f0 - F0 + 1:]); bT = e.msave()
    def scan_start(base, K, lo, hi, nxt):
        """earliest S in [lo, hi] whose Start (S, S+1) loads stage nxt by S+6; returns (S, load)."""
        for S in range(lo, hi + 1):
            e.mload(base)
            w = [()] * (S - K - 1) + [('Start',), ('Start',)] + [()] * 8
            rr = run(w)
            ld = next((K + 1 + i for i, r in enumerate(rr) if r[0x6D] == nxt), None)
            if ld is not None: return S, ld
        return None, None
    # 2. 6-3 -> 6-4a
    S1, L1 = scan_start(bT, T, T + 1, T + 12, 19); C1 = L1 + 152
    print('6-3 Start', S1, 'load', L1, '6-4a control', C1, flush=True)
    rows += [()] * (S1 - 1 - (F0 + len(rows) - 1)) + [('Start',), ('Start',)]
    rows += [()] * (C1 - 1 - (F0 + len(rows) - 1))
    md = rf(MD); e.mload(bT); rr = run(rows[T - F0 + 1:] + md + [()] * 5)
    base_f = T
    K1 = next(base_f + 1 + i for i, r in enumerate(rr) if base_f + 1 + i >= C1 and r[0x6D] == 19 and r[0x66] == 0)
    rk = rr[K1 - base_f - 1]; print('6-4a kill', K1, '(control +', K1 - C1, ') T', rk[0x63], 'np', rk[0x64], 'hp', rk[0x65], flush=True)
    rows = (rows + md)[:K1 - F0 + 1]
    e.mload(bT); run(rows[T - F0 + 1:]); bK1 = e.msave()
    est = K1 + 3 * rk[0x63] + 3 * rk[0x64] + 140
    S2, L2 = scan_start(bK1, K1, est, est + 20, 20); C2 = L2 + 152
    print('6-4a Start', S2, 'load', L2, '6-4b control', C2, flush=True)
    rows += [()] * (S2 - 1 - (F0 + len(rows) - 1)) + [('Start',), ('Start',)]
    rows += [()] * (C2 - 1 - (F0 + len(rows) - 1))
    jq = rf(JQ); e.mload(bK1); rr = run(rows[K1 - F0 + 1:] + jq + [()] * 5)
    K2 = next(K1 + 1 + i for i, r in enumerate(rr) if K1 + 1 + i >= C2 and r[0x6D] == 20 and r[0x66] == 0)
    rk = rr[K2 - K1 - 1]; print('6-4b kill', K2, '(control +', K2 - C2, ') T', rk[0x63], 'np', rk[0x64], 'hp', rk[0x65], flush=True)
    rows = (rows + jq)[:K2 - F0 + 1]
    e.mload(bK1); run(rows[K1 - F0 + 1:]); bK2 = e.msave()
    est = K2 + 3 * rk[0x63] + 3 * rk[0x64] + 140
    S3, L3 = scan_start(bK2, K2, est, est + 20, 21); C3 = L3 + 152
    # arrival values at C3 - 1 for d = 0
    e.mload(bK2); rr = run([()] * (S3 - K2 - 1) + [('Start',), ('Start',)] + [()] * (C3 - 1 - S3 - 1))
    r = rr[-1]; bf, t62, e3e = r[0xBF], r[0x62], r[0x3E]
    print('6-4b Start', S3, 'load', L3, '6-5 control', C3, '| at control-1: bf', bf, 't62', t62, 'e3e', e3e, flush=True)
    tab = pick.load(); best = None
    for d in (range(0, DMAX + 1) if DFIX < 0 else [DFIX]):
        c = pick.best((bf + d) % 256, t62, e3e, tab)
        if c:
            tot = d + c[0][0]
            if best is None or tot < best[0]: best = (tot, d, c[0])
    tot, d, (eo, _, k, line, Tt, hp, nh) = best
    print('6-5 choice: delay', d, 'line', line, 'kill row', k, 'END seen offset', eo, 'total', tot, 'NesHawk-table', nh, flush=True)
    S3d = S3 + d; L3d = L3 + d; C3d = C3 + d
    rows += [()] * (S3d - 1 - (F0 + len(rows) - 1)) + [('Start',), ('Start',)]
    rows += [()] * (C3d - 1 - (F0 + len(rows) - 1))
    dm = rf(line); e.mload(bK2); rr = run(rows[K2 - F0 + 1:] + dm + [()] * 700)
    fK = K2 + 1
    K3 = next((fK + i for i, r in enumerate(rr) if fK + i >= C3d and r[0x6D] == 21 and r[0x66] == 0), None)
    P = next((fK + i for i, r in enumerate(rr) if K3 and fK + i > K3 and r[0x6D] == 21 and r[0x63] == 0), None)
    E = next((fK + i for i, r in enumerate(rr) if P and fK + i > P and r[0x3E] == 1), None)
    deaths = [fK + i for i, r in enumerate(rr) if r[0x6E] == 35]
    print('6-5 kill', K3, '(control +', (K3 - C3d) if K3 else None, ') P', P, 'E', E, 'END seen', E + 1 if E else None,
          '| record line 41,774:', (E + 1 - 41774) if E else None, '| back to 6-1:', deaths[:1], flush=True)
    rows = rows + dm
    tmp = OR + '.tmp'
    open(tmp, 'w').write(f'# l62 6-3 + bosses rows from 35,799; 6-4a ctl {C1}, 6-4b ctl {C2}, 6-5 ctl {C3d}, END seen {E + 1 if E else None}\n' +
                         '\n'.join('+'.join(x) for x in rows) + '\n'); os.replace(tmp, OR)
    src = open('logs/l62_LOCKED_v2_to63_poweron.inputs.txt').read().split(chr(10))[1:35799]
    R = src + ['+'.join(x) for x in rows]
    open(OP + '.tmp', 'w').write(f'# frames={len(R)}\n' + '\n'.join(R) + '\n'); os.replace(OP + '.tmp', OP)
    print('wrote', OR, OP, len(R), 'rows; stage marks: 6-4a', C1, '6-4b', C2, '6-5', C3d, flush=True)
finally:
    e.close()
