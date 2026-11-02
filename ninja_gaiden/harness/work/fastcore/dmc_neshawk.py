"""Predict NesHawk's DMC-DMA / $4016 conflicts from a Mesen log (dmc2_tpl.lua) with a model of NesHawk's DMC unit
(read from BizHawk.Emulation.Cores.dll 2.11.1 IL: APU+DMCUnit.Run/Clock/Fetch/set_lenctr_en, NES.RunCpuOne,
NES.read_joyport). Event driven; calibration parameters: c0 (NesHawk cycle = Mesen cycle + c0), W (read - DMA
request offsets that delete a bit), stall costs.

    python work/fastcore/dmc_neshawk.py <mesen dmc log> <inputs> <neshawk trace csv> [frames]
"""
import bisect
import collections
import csv
import sys

sys.path.insert(0, '.')
from ng.inputs import read_inputs, to_mask  # noqa: E402

RATE = [428, 380, 340, 320, 286, 254, 226, 214, 190, 160, 142, 128, 106, 84, 72, 54]


def load(path, nmax=None):
    W, N, R = [], {}, collections.defaultdict(list)
    for line in open(path):
        p = line.split()
        if p[0] == 'W':
            W.append((int(p[3]), int(p[1]), int(p[2])))      # cycle, addr, value
        elif p[0] == 'N':
            N[int(p[2])] = int(p[1])                         # frame -> NMI cycle
        elif p[0] == 'F':
            cur = int(p[1])
        elif p[0] == 'R':
            R[cur].append(int(p[1]))
    W.sort()
    return W, N, R


def simulate(W, c0, t_end):
    """NesHawk DMC from power-on: list of DMA request cycles (in Mesen cycle units: NesHawk cycle - c0)."""
    # NesHawk cycle k: Run() decrements the timer; timer starts at 1020 -> first expiry at k = 1019 (0-based)
    reload = RATE[0]
    nxt = 1019                     # next expiry (NesHawk cycle)
    bits = 7
    filled = False
    length = 0
    user_len = 1
    dmas = []
    pend_len_dec = []              # cycles at which sample_length -= 1 happens
    wi = 0
    Wn = [(c + c0, a, v) for c, a, v in W]
    t_end += c0
    fill_at = None                 # cycle at which the buffer becomes filled (fetch)

    def request(d):
        nonlocal fill_at
        dmas.append(d - c0)
        fill_at = d + 3
        pend_len_dec.append(d + 5)

    while nxt < t_end:
        # apply register writes up to (and including) the expiry cycle - writes take effect at RunOneLast of their
        # cycle, i.e. for Run() calls at later cycles
        while wi < len(Wn) and Wn[wi][0] < nxt:
            c, a, v = Wn[wi]
            # settle pending fill / length decrements before the write
            if fill_at is not None and fill_at <= c:
                filled = True; fill_at = None
            while pend_len_dec and pend_len_dec[0] <= c:
                pend_len_dec.pop(0); length = max(0, length - 1)
            if a == 0x4010:
                reload = RATE[v & 15]
            elif a == 0x4013:
                user_len = v * 16 + 1
            elif a == 0x4015:
                if v & 0x10:
                    if length == 0:
                        length = user_len
                    if not filled and fill_at is None:
                        # call_from_write: Run(c+1) sets delay 3 (timer even) or 2, decremented in the same Run
                        timer_at = nxt - (c + 1)
                        delay = 3 if timer_at % 2 == 0 else 2
                        request(c + 1 + delay - 1)
                else:
                    length = 0
            wi += 1
        if fill_at is not None and fill_at <= nxt:
            filled = True; fill_at = None
        while pend_len_dec and pend_len_dec[0] <= nxt:
            pend_len_dec.pop(0); length = max(0, length - 1)
        # expiry: Clock()
        if bits == 0:
            bits = 7
            if filled:
                filled = False
                if length > 0 and fill_at is None:
                    request(nxt)
        else:
            bits -= 1
        nxt += reload
    return dmas


def main():
    log, inputs, trace = sys.argv[1:4]
    W, N, R = load(log)
    rows = [to_mask(r) for r in read_inputs(inputs)]
    tr = {int(r['row']): r for r in csv.DictReader(open(trace))}
    conf = set(k for k in tr if tr[k]['lagged'] == '0' and int(tr[k]['pad']) != rows[k - 1])
    chg = set(k for k in tr if tr[k]['lagged'] == '0' and k >= 2 and int(tr[k - 1]['pad']) != rows[k - 1])
    t_end = max(N.values()) + 40000
    print('writes', len(W), 'frames', len(N), 'conflicts', len(conf), 'change frames', len(chg))
    best = []
    for c0 in range(-40, 41):
        d = simulate(W, c0, t_end)
        # offsets read - request for every read within 12 cycles of a request
        hist_c, hist_n = collections.Counter(), collections.Counter()
        for f in chg:
            rr = R.get(f, [])[:16]
            if not rr:
                continue
            i = bisect.bisect_left(d, rr[0] - 12)
            near = set()
            while i < len(d) and d[i] <= rr[-1] + 12:
                for r in rr:
                    if -12 <= r - d[i] <= 12:
                        near.add(r - d[i])
                i += 1
            for o in near:
                (hist_c if f in conf else hist_n)[o] += 1
        # best single offset: conflicts explained minus non-conflict change frames hit
        for o in range(-12, 13):
            best.append((hist_c[o] - hist_n[o] * 0.2, c0, o, hist_c[o], hist_n[o]))
    best.sort(reverse=True)
    for b in best[:15]:
        print('c0 %d offset %d: conflicts %d / %d, non-conflict change frames %d' % (b[1], b[2], b[3], len(conf), b[4]))


if __name__ == '__main__':
    main()
