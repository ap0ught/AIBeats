"""Best 6-5 Demon line for an arrival phase.

    python work/l65/pick.py <bf> [--t62 29] [--e3e 4] [--all]

bf  = $BF at the checkpoint BEFORE the 6-5 control row (i.e. NesHawk frame control-1; TAS arrival = 243)
t62 = $62 (timer sub-second) at that checkpoint (TAS 29), e3e = $3E there (TAS 4; r4k2 arrival 5).
Reads work/l65/demon_all.tsv (every line that kills for that bf: bf, line, kill row, hp, T_ref, nh) and prints the line with
the earliest END seen for this (t62, e3e), plus the alternatives with --all.
Row 1 of every line file = the 6-5 control row (first row on which Right moves Ryu). END seen offset = END seen frame - control frame.
Rule (LOCKED_CHAIN "Transitions"): K = control + kill_row - 1; T = 150 - ticks with ticks on rows t62 + 1 + 61 j (<= kill row);
P = K + 3 T; E = first frame > P with $3E = 1 ($3E(f) = (e3e - (f - (control - 1))) mod 6); END seen = E + 1.
Record pace (6-5 control -> END seen): 755.2 f. Whole run beats the record iff END seen <= 41,774 on our axis.
"""
import sys, os

HERE = os.path.dirname(os.path.abspath(__file__))


def end_offset(kill_row, t62=29, e3e=4):
    ticks = 0
    r = t62 + 1
    while r <= kill_row:
        ticks += 1
        r += 61
    T = 150 - ticks
    P = (kill_row - 1) + 3 * T          # offsets from the control frame
    f = P + 1
    while (e3e - (f + 1)) % 6 != 1:
        f += 1
    return f + 1, T


def load(path=os.path.join(HERE, 'demon_all.tsv')):
    out = {}
    for l in open(path, encoding='utf-8'):
        if l.startswith('#') or not l.strip():
            continue
        p = l.rstrip('\n').split('\t')
        bf, line, k, hp, nh = int(p[0]), p[1], int(p[2]), int(p[3]), p[4] if len(p) > 4 else 'n'
        out.setdefault(bf, []).append((line, k, hp, nh))
    return out


def best(bf, t62=29, e3e=4, table=None):
    table = table or load()
    c = []
    for line, k, hp, nh in table.get(bf, []):
        e, T = end_offset(k, t62, e3e)
        c.append((e, -hp, k, line, T, hp, nh))
    c.sort()
    return c


if __name__ == '__main__':
    a = sys.argv[1:]

    def opt(n, d):
        if n in a:
            i = a.index(n); v = a[i + 1]; del a[i:i + 2]; return v
        return d
    t62 = int(opt('--t62', '29')); e3e = int(opt('--e3e', '4')); ALL = '--all' in a
    if ALL:
        a.remove('--all')
    bf = int(a[0]) % 256
    c = best(bf, t62, e3e)
    if not c:
        print(f'bf {bf}: NO line known (do not arrive on this phase)')
        sys.exit(1)
    for i, (e, _, k, line, T, hp, nh) in enumerate(c if ALL else c[:1]):
        print(f'bf {bf} t62 {t62} e3e {e3e}: {line}  kill row {k} (control + {k - 1}), T {T}, END seen = control + {e} '
              f'(record pace 755.2: {e - 755.2:+.1f}), hp left {hp}, NesHawk {nh}')
