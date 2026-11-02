"""Bird simulator on our recorded base path (work/l51c/base_path.json) with inserted waits.
B = bird abs x * 256, V = vel * 256, Y. Frame k of the path = state after row f."""
import json
BP = json.load(open('work/l51c/base_path.json'))
def init(k=0):
    a = BP[k]; return (a['cam'] + a['bx']*256 + a['bs'], a['v'], a['by'])
def step(b, cam, rx, y, fz, variant=0):
    B, V, Y = b
    if fz: return b
    Y = Y + 1 if y >= Y else Y - 1
    sx = (B - cam) >> 8
    V = V - 16 if sx >= rx else V + 16
    return (B + V, V, Y)
def run(b, k1, k2, waits=None, rec=None):
    """from path index k1 (state after it) to k2; waits {k: w}: Ryu stands w frames before path index k.
    rec[k] = (b, extra) with extra = frames waited so far."""
    W = 0
    for k in range(k1 + 1, k2 + 1):
        if waits and k in waits:
            p = BP[k - 1]
            for _ in range(waits[k]):
                b = step(b, p['cam'], p['rx'], p['y'], 0)
            W += waits[k]
        a = BP[k]
        b = step(b, a['cam'], a['rx'], a['y'], a['fz'])
        if rec is not None: rec[k] = b
    return b
