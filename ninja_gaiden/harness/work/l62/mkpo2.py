import sys
src=open('work/l62/l62_hs_k2_poweron.inputs.txt').read().split('\n')[1:33590]
add=[l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
add=['' if x=='-' else x for x in add]
R=src+add
open(sys.argv[2],'w').write(f'# frames={len(R)}\n'+'\n'.join(R)+'\n'); print(len(R))
