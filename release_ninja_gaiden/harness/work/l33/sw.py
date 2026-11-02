"""Batch sweep helpers for 3-3 (Mesen FastPool from states/mesen/l33_<tag>_ctl.mst, legal by Enforcer).
    from sw import *; X = Ctx('cB'); res = X.run([want_rows, ...])  -> list of dicts (see ev())
Spec strings: 'Right*3,A+Right*2,-*4,Up+B*2' (row*count, comma separated)."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'work/l31t')
import fcka  # noqa: F401  (keepalive)
sys.path.insert(0, 'work/l33')
from lib import CANDS, mst, C, L, F, FLD, row

FLD2 = dict(FLD)
for _j in range(3):
    FLD2[f'fx{_j}'] = 0x4BB + _j; FLD2[f'fy{_j}'] = 0x4BE + _j


def spec(s):
    out = []
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        w, k = part.split('*') if '*' in part else (part, '1')
        out += [row(w)] * int(k)
    return out


class Ctx:
    def __init__(self, tag, n=2):
        self.tag = tag
        self.hist = C.rows_of(CANDS[tag]['pow'])
        self.base = L.Enforcer(self.hist[-1900:])
        self.n = n
        self.data = open(mst(tag), 'rb').read()
        self.boot()

    def boot(self):
        self.P = F.FastPool(self.n, boot_rows=None, ticks=True, fields=FLD2)
        for w in self.P.workers:
            w.put('s', self.data); w.load('s'); w._ka_slot = 's'

    def legal(self, want):
        en = self.base.copy()
        return [tuple(sorted(en.emit(w))) for w in want]

    def run(self, wants, chunk=40, log=False):
        cands = [self.legal(w) for w in wants]
        out = []
        t0 = time.time()
        for i in range(0, len(cands), chunk):
            for att in range(3):
                try:
                    rr = self.P.run_batch('s', cands[i:i + chunk], record='all',
                                          stops=[(0x6D, 'changed', 0), (0x65, '==', 0), (0x66, '==', 0)])
                    break
                except Exception as ex:   # noqa: BLE001
                    print('pool error', ex, flush=True)
                    for w in self.P.workers:
                        fcka.forget(w)
                        try: w.proc.kill()
                        except Exception: pass
                    time.sleep(1); self.boot()
            for c, r in zip(cands[i:i + chunk], rr):
                out.append(ev(c, r.states))
            if log:
                print(f'  {min(i + chunk, len(cands))}/{len(cands)} {time.time() - t0:.0f}s', flush=True)
        return out

    def run_from(self, prefix, suffixes, chunk=48):
        """prefix = LEGAL rows from control (played once per worker, kept in a slot); suffixes = wanted rows, legalized
        after hist+prefix. Returns ev() dicts whose rows/kill/hits are relative to control (prefix included)."""
        en0 = L.Enforcer((self.hist + list(prefix))[-1900:])
        cands = []
        for w in suffixes:
            en = en0.copy(); cands.append([tuple(sorted(en.emit(x))) for x in w])
        out = []
        for att in range(3):
            try:
                if prefix:
                    for w in self.P.workers:
                        w.drop_prefix('q')
                        rr = w.run_batch('s', [list(prefix)], record='last', keep=True, prefix='q')
                        w._q = rr[0].slot
                    slot = self.P.workers[0]._q
                else:
                    slot = 's'
                res = []
                for i in range(0, len(cands), chunk):
                    res += self.P.run_batch(slot, cands[i:i + chunk], record='all',
                                            stops=[(0x6D, 'changed', 0), (0x65, '==', 0), (0x66, '==', 0)])
                break
            except Exception as ex:   # noqa: BLE001
                print('pool error', ex, flush=True)
                for w in self.P.workers:
                    fcka.forget(w)
                    try: w.proc.kill()
                    except Exception: pass
                time.sleep(1); self.boot()
        n0 = len(prefix)
        for c, r in zip(cands, res):
            e = ev(list(prefix) + c, r.states)
            # ev on suffix states: shift indices
            e['kill'] = (e['kill'] + n0) if e['kill'] else None
            if e['kill']:
                e['M'] = e['kill'] + 3 * (e['last']['timer'] + e['last']['ninpo']) if e['hp'] > 0 else None
            e['hits'] = [(i + n0, h) for i, h in e['hits']]
            e['rhit'] = [i + n0 for i in e['rhit']]
            e['rows'] = list(prefix) + c[:len(r.states)]
            e['n0'] = n0
            out.append(e)
        return out

    def close(self):
        for w in self.P.workers:
            fcka.forget(w)
        self.P.close()


def ev(rows, sts):
    """kill = row (1-based) where $66 hits 0; M = kill + 3*(timer + ninpo); hits = [(row, bosshp)]; rhit = rows Ryu lost hp."""
    hits, rh = [], []
    pb, ph = 16, None
    kill = None
    for i, s in enumerate(sts):
        if s['bosshp'] < pb:
            hits.append((i + 1, s['bosshp']))
        pb = s['bosshp']
        if ph is not None and s['hp'] < ph:
            rh.append(i + 1)
        ph = s['hp']
        if s['bosshp'] == 0 and s['stage'] == 7:
            kill = i + 1
            break
    last = sts[-1] if sts else None
    M = kill + 3 * (last['timer'] + last['ninpo']) if kill and last['hp'] > 0 else None
    return dict(rows=rows[:len(sts)], kill=kill, M=M, boss=pb, hits=hits, rhit=rh, hp=last['hp'] if last else 0,
                np=last['ninpo'] if last else 0, last=last, sts=sts)
