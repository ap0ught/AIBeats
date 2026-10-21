"""Track K2: simulator wrapper for room-1 searches: replay input lists from the bookmark with snapshots, report head/tail
pauses, the frames the heads/tails appear and vanish, and the toad's state.  No memory writes."""
import time
from u17k_lib import *


class Sim:
    def __init__(self, log, bookmark="B4_end0"):
        self.e = BizHawk(log_name=log)
        self.bm = bookmark
        self.snaps = {}      # frame -> (sid, tracker state)
        self.base = None

    def close(self):
        self.e.close()

    def set_base(self, ins, upto, every=10, start=0):
        """replay ins[:upto] from the bookmark (or from the last still-valid snapshot), keeping a snapshot every `every` frames"""
        keep = {}
        common = 0
        if self.base is not None:
            while common < min(len(ins), len(self.base), upto) and ins[common] == self.base[common]:
                common += 1
        for f, v in self.snaps.items():
            if f <= common:
                keep[f] = v
            else:
                self.e.mfree(v[0])
        self.snaps = keep
        self.base = list(ins)
        f0 = max(self.snaps) if self.snaps else 0
        if f0 == 0:
            self.e.load(self.bm)
            tr = new_tracker()
            self.snaps[0] = (self.e.msave(), copy_tr(tr))
        else:
            self.e.mload(self.snaps[f0][0])
            tr = copy_tr(self.snaps[f0][1])
        for n in range(f0 + 1, upto + 1):
            self.e.step(bt(ins[n - 1]), 1)
            track(tr, n, self.e.ram(0, 0x800))
            if n % every == 0:
                self.snaps[n] = (self.e.msave(), copy_tr(tr))
        return tr

    def run(self, ins, until, stop=None):
        """evaluate ins (full list from the bookmark) to frame `until`, restarting from the latest snapshot that is still on the
        base's path; stop(tr) -> True ends early"""
        common = 0
        while common < min(len(ins), len(self.base)) and ins[common] == self.base[common]:
            common += 1
        f0 = max(f for f in self.snaps if f <= common)
        self.e.mload(self.snaps[f0][0])
        tr = copy_tr(self.snaps[f0][1])
        for n in range(f0 + 1, until + 1):
            b = ins[n - 1] if n - 1 < len(ins) else ""
            self.e.step(bt(b), 1)
            track(tr, n, self.e.ram(0, 0x800))
            if stop and stop(tr):
                break
        return tr


def new_tracker():
    return dict(n=0, prev={0x4C: None, 0x4D: None}, moved={0x4C: False, 0x4D: False}, hp_min=99, ev=[], hp=[], tp=[], toad=None,
                happ=[], hgone=[], tapp=[], tgone=[], lvl=8, stand=0)


def copy_tr(tr):
    c = dict(tr)
    for k in ("prev", "moved"):
        c[k] = dict(tr[k])
    for k in ("ev", "hp", "tp", "happ", "hgone", "tapp", "tgone"):
        c[k] = list(tr[k])
    return c


def track(tr, n, m):
    tr["n"] = n
    x, H = m[0x3FD] | m[0x3EE] << 8, m[0x439] | m[0x42A] << 8
    tr["toad"] = (x, H, m[0x475], m[0x565], m[0x3B5], m[0x4A2] & 0x40)
    tr["hp_min"] = min(tr["hp_min"], m[0x51A])
    tr["lvl"] = m[0x10]
    for oid, pl, al, gl in ((0x4C, "hp", "happ", "hgone"), (0x4D, "tp", "tapp", "tgone")):
        h = None
        for q in range(1, 15):
            if m[0x3C1 + q] == oid:
                h = (m[0x3FD + q] | m[0x3EE + q] << 8, m[0x439 + q] | m[0x42A + q] << 8)
                break
        p = tr["prev"][oid]
        if h and not p:
            tr[al].append(n)
            tr["moved"][oid] = False
        if p and not h:
            tr[gl].append(n)
        if h and p:
            if h == p:
                if tr["moved"][oid]:
                    tr[pl].append(n)
            else:
                tr["moved"][oid] = True
        tr["prev"][oid] = h
    tr["head"] = tr["prev"][0x4C]
    tr["tail"] = tr["prev"][0x4D]


if __name__ == "__main__":
    s = Sim("u17k_sim_test.log")
    k6 = seg("K6")
    t0 = time.time()
    tr = s.set_base(k6, 1992, every=20)
    t1 = time.time()
    print("1992 frames with tracking:", round(t1 - t0, 2), "s")
    print("head pauses", tr["hp"]); print("tail pauses", tr["tp"]); print("happ", tr["happ"], "hgone", tr["hgone"], "tapp", tr["tapp"], "tgone", tr["tgone"])
    t0 = time.time()
    tr = s.run(k6, 1992)
    print("re-run from last snapshot:", round(time.time() - t0, 2), tr["toad"])
    s.close()
