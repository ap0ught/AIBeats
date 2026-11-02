#!/bin/bash
# stages b+c of work/l22a/r8pipe.sh from a prefix that already holds J&S. usage: r8tail.sh <prefix> <tag> [width]
set -e
cd "/g/AI World Record/Ninja Gaiden"
P=$1; T=$2; W=${3:-64}
AL="Left|A+Left|B+Left|A+B+Left|-|Down+B|Right|A+Right"
cp $P work/l22a/${T}_a.txt
N=$(python -c "import sys;sys.path.insert(0,'.');from ng.solve import common as C;print(len(C.rows_of('work/l22a/${T}_a.txt')))")
python work/l22a/mkst.py work/l22a/${T}_a.txt $N ${T}1
FB_NW=2 python -u work/l22a/abeam.py work/l22a/h_${T}1.inputs.txt states/mesen/l22a_${T}1.mst x:8:le:900 ${T}b --alpha "$AL" --score xl --width $W --frames 400 --minhp 15 --need 10 --npw 0.2 > work/l22a/${T}b.log 2>&1
python work/l22a/cat.py work/l22a/${T}_b.txt "${T}_a + ${T}b" work/l22a/${T}_a.txt work/l22a/fb_${T}b.inputs.txt
N=$(python -c "import sys;sys.path.insert(0,'.');from ng.solve import common as C;print(len(C.rows_of('work/l22a/${T}_b.txt')))")
python work/l22a/mkst.py work/l22a/${T}_b.txt $N ${T}2
FB_NW=2 python -u work/l22a/abeam.py work/l22a/h_${T}2.inputs.txt states/mesen/l22a_${T}2.mst x:8:le:40 ${T}c --alpha "$AL" --score xl --width $W --frames 750 --minhp 15 --need 10 --npeq 10 --npw 0.2 > work/l22a/${T}c.log 2>&1
python work/l22a/cat.py work/l22a/${T}_full.txt "${T}_b + ${T}c (room-8 exit)" work/l22a/${T}_b.txt work/l22a/fb_${T}c.inputs.txt
tail -n 1 work/l22a/${T}c.log
