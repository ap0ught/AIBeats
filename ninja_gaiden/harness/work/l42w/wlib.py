"""Shared helpers for the 4-2 exit wall (agent "wall")."""
import sys
sys.path.insert(0, '.')
BTN = ('A', 'B', 'Left', 'Right', 'Up', 'Down')
M = {'R': 'Right', 'L': 'Left', 'U': 'Up', 'D': 'Down', 'A': 'A', 'B': 'B'}


def spec(s):
    out = []
    for tok in s.split():
        k, n = tok.split(':') if ':' in tok else (tok, '1')
        out += [tuple(sorted(M[c] for c in k if c != '-'))] * int(n)
    return out


def short(r):
    ab = {'Right': 'R', 'Left': 'L', 'Up': 'U', 'Down': 'D', 'A': 'A', 'B': 'B', 'Start': 'S', 'Select': 's'}
    return ''.join(ab[b] for b in r) or '-'


class LegState:
    """per-button (held, run length, frames since the last press started) at the end of a history"""

    def __init__(self, hist=()):
        self.st = {}
        n = len(hist)
        for b in BTN:
            held = False; run = 99; lp = None
            for i, r in enumerate(hist):
                h = b in r
                if h and not held: lp = i
                run = run + 1 if h == held else 1
                held = h
            self.st[b] = (held, run, (n - lp) if lp is not None else 999)

    def check(self, rows):
        """first index of rows that breaks a rule (None if legal)"""
        st = dict(self.st)
        for i, r in enumerate(rows):
            if ('Left' in r and 'Right' in r) or ('Up' in r and 'Down' in r) or 'Start' in r: return i
            for b in BTN:
                held, run, since = st[b]
                h = b in r
                if h != held:
                    if run < 2: return i
                    if h and since < 5: return i
                    run = 1
                    if h: since = 0
                else:
                    run += 1
                since += 1
                st[b] = (h, run, since)
        return None

    def after(self, rows):
        c = LegState.__new__(LegState); c.st = dict(self.st)
        for r in rows:
            for b in BTN:
                held, run, since = c.st[b]
                h = b in r
                if h != held:
                    run = 1
                    if h: since = 0
                else:
                    run += 1
                since += 1
                c.st[b] = (h, run, since)
        return c


FL = {'x': 0x86, 'xsub': 0x85, 'sl': 0x51, 'sh': 0x52, 'y': 0x8A, 'vy': 0x89, 'vys': 0x87, 'coll': 0x8C, 'anim': 0x80,
      'hp': 0x65, 'np': 0x64, 'it': 0xC9, 'st': 0x6D, 'c5': 0x5C, 'inv': 0x95, 'rf': 0x84, 'bf': 0xBF}
for _i in range(8):
    FL[f't{_i}'] = 0x400 + _i; FL[f'ex{_i}'] = 0x460 + _i; FL[f'ey{_i}'] = 0x480 + _i


def X(s): return s['sh'] * 256 + s['sl'] + s['x']


def trig(states):
    """index (0-based) of the first state with $5C == 0 (stage-end trigger), else None"""
    return next((i for i, s in enumerate(states) if s['c5'] == 0), None)
