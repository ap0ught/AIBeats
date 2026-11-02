"""bang-bang bird model. sim(x0 (float screen x), sp0 (px/f), scroll0 (float), moves list of per-frame scroll deltas)
returns list of (frame idx, screen x, speed) until despawn (x<8 or >=248)."""
import math
def sim(x0, sp0, scr0, deltas, ryu_sx=128):
    x, sp, scr = x0, sp0, scr0; out = []
    for i, d in enumerate(deltas):
        nscr = scr + d
        frozen = d > 0 and math.floor(nscr / 16) != math.floor(scr / 16)
        if not frozen:
            sp += (1/16) if x < ryu_sx else (-1/16)
            nx = x + sp
            if nx < 8 or nx >= 248: return out, i
            x = nx
        x -= d; scr = nscr
        out.append((i, x, sp))
    return out, None
if __name__ == '__main__':
    # validate vs gt0: spawn row 12486: x 240+176/256, sp 0, scroll 1185.5
    import ast
    gt = {}
    for ln in open('work/l32b/gt0.txt'):
        p = ln.split(None, 8)
        f = int(p[0]); rest = ln.split()
        b = ln[ln.index('('):ln.index(')')+1] if '(' in ln else None
        gt[f] = (int(rest[2]), int(rest[6]) / 256 + int(rest[7]), ast.literal_eval(b) if b else None)
    scr = [gt[f][1] for f in range(12486, 12600) if f in gt]
    deltas = [scr[i+1] - scr[i] for i in range(len(scr)-1)]
    b0 = gt[12486][2]
    out, gone = sim(b0[1] + b0[2]/256, b0[3]/256, scr[0], deltas)
    for i, x, sp in out[::5]:
        g = gt[12487 + i][2]
        print(12487 + i, round(x, 3), sp, '| gt', None if g is None else (round(g[1] + g[2]/256, 3), g[3]/256))
    print('gone at', None if gone is None else 12487 + gone)
