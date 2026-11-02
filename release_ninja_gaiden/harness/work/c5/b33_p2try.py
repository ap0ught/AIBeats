import sys
sys.path.insert(0, '.'); sys.path.insert(0, 'work/c5')
from b33lib import Ctx
from ng.solve import common as C
p2 = C.rows_of('logs/a34/3-3_p2.inputs.txt')[:400]
H = C.rows_of('logs/tk_to33.inputs.txt')[:15139]
C.write_inputs('states/tmp/c5_h15139.inputs.txt', H, 'tk_to33 rows 1-15139')
ctx = Ctx('states/tmp/c5_h15139.inputs.txt', 'states/mesen/c5_33m1.mst')
wants = [[('Right',)] + p2]
for c, s in ctx.run(wants):
    print(s)
ctx.close()
