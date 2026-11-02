import sys, csv; sys.path.insert(0, '.')
from ng.fastcore import FastCore
from ng.inputs import read_inputs, to_mask
base = [to_mask(r) for r in read_inputs('logs/a12r3_to22.inputs.txt')]
new = [to_mask(r) for r in read_inputs('logs/fcv_s11.inputs.txt')]
pads = {int(r['row']): int(r['pad']) for r in csv.DictReader(open('logs/fc_to22.trace.csv'))}
boot = bytes(pads[k] for k in range(1, 175))
with FastCore(boot_rows=boot) as fc:
    fc.save('s')
    rb, rn = fc.run_batch('s', [base[174:2450], new[174:2405]], record='all')
    def summ(res, label):
        prev = None
        for i, r in enumerate(res.states):
            key = (r.room, r.stage)
            if key != prev:
                print(label, 'frame', 175 + i, 'stage', r.stage, 'room', r.room, 'x', r.x, 'hp', r.hp, 'timer', r.timer, 'scroll', r.scroll_scr, r.scroll)
                prev = key
    summ(rb, 'BASE'); summ(rn, 'NEW ')
    for f in (800, 805, 809, 812, 820, 840, 900, 1000):
        a, b = rb.states[f - 175], rn.states[f - 175]
        print(f, 'base x', a.x, 'y', a.y, 'scr', a.scroll_scr, a.scroll, 'anim', a.anim, 'hp', a.hp, '| new x', b.x, 'y', b.y, 'scr', b.scroll_scr, b.scroll, 'anim', b.anim, 'hp', b.hp)
