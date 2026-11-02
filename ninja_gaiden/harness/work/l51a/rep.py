"""Repair search: prefix (first N rows of a stage-rows file) + legalized TAS rows at lag LG to TAS END, with edit sets.
Each variant = dict TAS frame -> wanted row. Reports first hp loss, death/pit, X at the end, np.
Library use: from rep import Rep; R = Rep(prefix, N, LG, END); R.run(ov) -> dict."""
import sys; sys.path.insert(0, 'work/l51a')
from lib import *
BIRD = None   # (our f1, f2, X1, X2): require a type-11 slot with abs X in [X1,X2] in that frame window
SF = None  # our frame where X is scored
EMPTY = None  # our frame at which no enemy slot may be active
HITOK = None  # our frame from which hits are allowed (the wall boost)
class Rep:
    def __init__(self, prefix, N, LG, END, base_ov=None):
        self.pre = rows_file(prefix)[:N] if isinstance(prefix, str) else list(prefix)[:N]
        self.N = len(self.pre); self.LG = LG; self.END = END; self.base_ov = base_ov or {}
        self.H = hist()
        self.fc, _k = start_core(self.pre); self.fc.step(self.pre[_k:], record='last'); self.fc.save('p'); self.fc._ka_slot = 'p'
        r = self.fc.ram(); self.hp0 = r[0x65]; self.np0 = r[0x64]
    def rows(self, ov):
        want = []
        o = dict(self.base_ov); o.update(ov)
        for t in range(CTL + self.N - self.LG, self.END + 1):
            w = set(T(t))
            if 'Left' in w and 'Right' in w: w -= {'Left'}
            if 'Up' in w and 'Down' in w: w -= {'Up', 'Down'}
            if t in (22793, 22794): w = {'Left'}
            if t in (23279, 23280): w = {'A', 'Right'}
            if t in o: w = set(o[t])
            want.append(w)
        en = A.Enforcer(self.H[-1900:] + self.pre)
        return [tuple(sorted(en.emit(w))) for w in want]
    def run(self, ov, keep=False):
        rows = self.rows(ov)
        self.fc.load('p')
        _, recs, _ = self.fc.step(rows, record='all')
        hit = None; dead = None; hp = self.hp0; lastX = None; bird = None; hits = []; empty_ok = None; sfx = None
        for i, s in enumerate(recs):
            f = CTL + self.N + i; X, y = RXY(s)
            if SF and f == SF: sfx = X
            if EMPTY and f == EMPTY: empty_ok = (s['eact'] == 0)
            if bird is None and BIRD and BIRD[0] <= f <= BIRD[1]:
                scr = X - s['x86']
                for j in range(8):
                    if s['eact'] >> j & 1 and s[f't{j}'] == 11 and BIRD[2] <= scr + s[f'ex{j}'] <= BIRD[3] and s[f'ey{j}'] <= 72: bird = f; break
            if s['hp65'] < hp:
                hits.append((f, X, y))
                if hit is None and not (HITOK and f >= HITOK): hit = (f, X, y)
            hp = s['hp65']
            if y >= 232 or s['hp65'] == 0: dead = (f, X, y); break
            lastX = (f, X, y, s['hp65'], s['np64'], s['item'])
        res = dict(hit=hit, dead=dead, last=lastX, bird=bird, hits=hits, empty=empty_ok, sfx=sfx)
        if keep: res['rows'] = self.pre + rows
        return res
