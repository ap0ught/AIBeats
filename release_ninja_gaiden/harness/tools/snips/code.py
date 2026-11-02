import json
out={}
for a in (0x8390, 0x8040):
    out[hex(a)] = e.ram_domain('System Bus', a, 64).hex()
s=e.step(('Start',),2)
out['after']= e.ram_domain('System Bus', 0x8040, 64).hex()
json.dump(out, open('logs/code.json','w'))
