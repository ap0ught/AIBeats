"""python work/l22a/jedit.py <in rows> <out rows>: apply the J&S-keeping room-6 edit (rows 478-479 Left, 489-490 B+Left)"""
import sys
L=open(sys.argv[1]).read().splitlines()
hdr,b=(L[0],L[1:]) if L[0].startswith('#') else ('# rows',L)
assert b[477]=='B+Left' and b[478]=='B+Left' and b[488]=='Left' and b[489]=='Left', (b[477:479],b[488:490])
b[477]=b[478]='Left'; b[488]=b[489]='B+Left'
open(sys.argv[2],'w').write(hdr+' [art: J&S edit 478-479 -> 489-490]\n'+'\n'.join(b)+'\n')
