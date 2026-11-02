import sys;sys.path.insert(0,'.');from ng import legal
T=legal.TasRef()
turn=int(sys.argv[1]); jump=int(sys.argv[2]); pre=int(sys.argv[3]) if len(sys.argv)>3 else 6
seq=[f'-*{pre}']
for k in range(5101,5215):
    r=set(T.rows[k-1])
    if 'Left' in r and 'Right' in r: r.discard('Left')
    if 'Up' in r and 'Down' in r: r.discard('Down')
    if turn<=k<jump: r={'Right'}
    if k==jump: r={'Right','A'}
    if k==5120 and jump!=5120: r={'Right'} if k>turn else set()
    seq.append(('+'.join(sorted(r)) if r else '')+'*1')
print(','.join(seq))
