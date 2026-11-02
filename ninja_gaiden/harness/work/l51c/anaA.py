import json, collections
R = [json.loads(l) for l in open('work/l51c/thrA.jsonl')]
print(len(R))
ok = [r for r in R if r['hp'] == 15 and len(r['hits']) == 1]
print('health, no other hit:', len(ok))
c = collections.Counter((len(r['birds']), r['bat'], r['x391'][0]) for r in ok)
for k, v in sorted(c.items()): print(k, v)
good = [r for r in ok if r['birds'] and r['x391'][0] >= 2595]
for r in good[:40]: print(r['k'], r['np'], r['birds'], r['bat'], r['x391'], r['end'])
