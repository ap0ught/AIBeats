"""Build stage rows: prefix rows[:N] + wanted macro rows legalized by the Enforcer. 
python work/l43/mk.py <prefix|-> N <out> <spec>   spec = 'd*4,(R+U,A+L+U,A+L,R,R+U)*5,R*100' (tokens P*n, groups (..)*n)"""
import sys, re
sys.path.insert(0, 'work/l43')
from lib import *
AB = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B', 'S': 'Start', 'd': ''}
def tok(t):
    if t in ('d', '-', ''): return ()
    return tuple(sorted(AB[x] for x in t.split('+')))
def parse(spec):
    out = []
    for m in re.finditer(r'\(([^)]*)\)\*(\d+)|([^,()]+)', spec):
        if m.group(1) is not None:
            out += [tok(x.strip()) for x in m.group(1).split(',')] * int(m.group(2))
        else:
            t = m.group(3).strip()
            if not t: continue
            if '*' in t: p, n = t.split('*'); out += [tok(p)] * int(n)
            else: out.append(tok(t))
    return out
if __name__ == '__main__':
    pre = rows_file(sys.argv[1])[:int(sys.argv[2])] if sys.argv[1] != '-' else []
    want = parse(sys.argv[4]); en = enforcer(pre)
    rows = pre + [tuple(sorted(en.emit(w))) for w in want]
    print('legal:', legal_ok(rows, hist_chain()) or 'PASS', len(rows))
    write_rows(sys.argv[3], rows, 'mk ' + sys.argv[4])
