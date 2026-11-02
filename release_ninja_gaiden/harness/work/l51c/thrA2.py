"""Stage A: Windmill / jump variants from the c3a platform state (24,270). Keep a bird alive?
rows: Right.., jump A+Right x2 at a, Up+B x2 at b (Right released on those rows), optional 2nd Up+B x2 at c, Right after.
Report per variant: hits, hp/np at 24,400, birds alive at 24,400 (+ their rel. x/y), bat alive, Ryu X at 24,391."""
import sys, json; sys.path.insert(0, 'work/l51c')
from lc import *
F0 = 24270; MST = 'states/mesen/l51c_c3a_24270.mst'
rows = [tuple(sorted(r)) for r in C.rows_of('logs/l51_c3a_poweron.inputs.txt')]; hist = rows[:F0]
END = 24400
out = open('work/l51c/thrA2.jsonl', 'w')
cands = []; seen = set()
for a in range(24274, 24292):
    for b in range(max(a + 8, 24298), 24330):
        for c in [None]:
            want = [{'Right'} for _ in range(END - F0)]
            for f in (a, a + 1): want[f - F0 - 1] = {'A', 'Right'}
            for t in (b, c):
                if t:
                    for f in (t, t + 1):
                        s = want[f - F0 - 1]; s.discard('Right'); s |= {'B', 'Up'}
            rr = enforce(want, hist)
            if legal_ok(rr, hist) or tuple(rr) in seen: continue
            seen.add(tuple(rr)); cands.append(((a, b, c), rr))
print('cands', len(cands), flush=True)
fc = core(MST); fc.save('b'); fc._ka_slot = 'b'
for i in range(0, len(cands), 50):
    ch = cands[i:i+50]
    res = fc.run_batch('b', [r for _, r in ch], record='all')
    for (k, rr), r in zip(ch, res):
        st = r.states; hp = 9; hits = []
        for t, s in enumerate(st):
            if s['hp65'] != hp: hits.append((F0 + 1 + t, RXY(s), hp, s['hp65'])); hp = s['hp65']
        s = st[-1]; X, y = RXY(s); hi = s['scr_hi']; hi = hi - 256 if hi >= 128 else hi
        birds = [(j, hi*256 + s['scr_lo'] + s[f'ex{j}'] - X, s[f'ey{j}'] - y) for j in range(8) if s['eact'] >> j & 1 and s[f't{j}'] == 11]
        bat = any(s['eact'] >> j & 1 and s[f't{j}'] == 8 for j in range(8))
        x391 = RXY(st[24391 - F0 - 1])
        out.write(json.dumps(dict(k=k, hits=hits, hp=s['hp65'], np=s['np64'], birds=birds, bat=bat, x391=x391, end=(X, y))) + '\n')
    out.flush()
fc.close()
