e.tick(0xC088); e.trace(True)
def run(rows, label):
    e.run(rows)
    for r, s in zip(rows, e.last_trace):
        print(label, '+'.join(r) or '.', s)
run([()]*3+[('Right',)]+[()]*4, 'tap')
run([('A',)]*2+[()]*6, 'jump')
run([('Right',)]*30, 'right')
run([()]*40, 'idle')
run([('B',)]+[()]*20, 'B')
