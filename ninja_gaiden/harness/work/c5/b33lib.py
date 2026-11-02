"""3-3 Basaquer search on Mesen (FastPool) from a chained 3-3 control state. Legal by construction (Enforcer on the
power-on history), judged later on NesHawk.  Library used by work/c5/b33*.py."""
import sys, time
sys.path.insert(0, '.')
from ng.solve import common as C, legality as L, fast as FS
from ng import fastcore as F


class Ctx:
    def __init__(self, hist_file, mst, n=2):
        self.hist = C.rows_of(hist_file)
        self.n, self.mst = n, mst
        self.P = None
        self.last = 0
        self.base = L.Enforcer(self.hist[-1900:])

    def boot(self):
        P = F.FastPool(self.n, boot_rows=None, ticks=True)
        data = open(self.mst, "rb").read()
        P.put_all("s", data)
        for w in P.workers:
            w.load("s")
        return P

    def legal(self, want):
        en = self.base.copy()
        return [en.emit(w) for w in want]

    def run(self, wants, chunk=24, log=lambda s: None):
        cands = [self.legal(w) for w in wants]
        # Mesen sits blocked inside its NMI callback while Python works; a long pause (> ~10 s) there kills the
        # Lua script (Mesen script watchdog) -> idle process / reset connection. Re-boot the pool after a pause.
        if self.P is None or time.time() - self.last > 5:
            if self.P is not None:
                try:
                    self.P.close()
                except Exception:
                    pass
            self.P = self.boot()
        res = FS.run_chunked(self.P, "s", cands, chunk=chunk, log=log, record="all", reboot=self.boot,
                             stops=[(0x6D, "changed", 0), (0x65, "==", 0), (0x497, "==", 0)])
        self.P = FS.run_chunked.pool
        self.last = time.time()
        out = []
        for c, r in zip(cands, res):
            out.append((c, score(r)))
        return out

    def close(self):
        if self.P is not None:
            self.P.close()


def score(r):
    """-> dict(kill=row index of boss_real==0 or None, left=boss HP left, hits=[(i, hp)], minhp, dead)"""
    sts = r.states
    hits, prev, kill, dead = [], None, None, False
    minhp = 99
    for i, s in enumerate(sts):
        b = s["boss_real"]
        if prev is not None and b < prev:
            hits.append((i, b))
        prev = b
        minhp = min(minhp, s["hp"])
        if s["hp"] == 0 or (s["dead"] & 0x80):
            dead = True
            break
        if b == 0 and s["stage"] == 7:
            kill = i
            break
    return dict(kill=kill, left=prev if prev is not None else 16, hits=hits, minhp=minhp, dead=dead,
                n=len(sts))
