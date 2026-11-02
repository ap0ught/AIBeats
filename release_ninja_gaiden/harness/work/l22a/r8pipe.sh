#!/bin/bash
# Room-8 art pipeline on a Star-line prefix that ends in room 8 near X 1400 (after the +5 +5 lanterns, ninpo 30, Star).
# usage: bash work/l22a/r8pipe.sh <prefix rows file> <tag> [lag] [width]
# -> work/l22a/<tag>_full.txt (stage rows to room-8 exit X 40, J&S + exactly 10), then run verify finish yourself.
set -e
cd "/g/AI World Record/Ninja Gaiden"
P=$1; T=$2; LAG=${3:-171}; W=${4:-64}
AL="Left|A+Left|B+Left|A+B+Left|-|Down+B|Right|A+Right"
N=$(python -c "import sys;sys.path.insert(0,'.');from ng.solve import common as C;print(len(C.rows_of('$P')))")
python work/l22a/mkst.py $P $N ${T}0
for WJ in $W 48 80 32; do
  FB_NW=2 python -u work/l22a/abeam.py work/l22a/h_${T}0.inputs.txt states/mesen/l22a_${T}0.mst item:133 ${T}j --alpha "$AL" --score tas --lag $LAG --width $WJ --frames 200 --minhp 15 --need 10 --items 129,133 --jsby 1250 > work/l22a/${T}j.log 2>&1
  grep -q GOAL work/l22a/${T}j.log && break
done
python work/l22a/cat.py work/l22a/${T}_a.txt "$P + ${T}j" $P work/l22a/fb_${T}j.inputs.txt
N=$(python -c "import sys;sys.path.insert(0,'.');from ng.solve import common as C;print(len(C.rows_of('work/l22a/${T}_a.txt')))")
python work/l22a/mkst.py work/l22a/${T}_a.txt $N ${T}1
FB_NW=2 python -u work/l22a/abeam.py work/l22a/h_${T}1.inputs.txt states/mesen/l22a_${T}1.mst x:8:le:900 ${T}b --alpha "$AL" --score xl --width $W --frames 400 --minhp 15 --need 10 --npw 0.2 --ymax 193 > work/l22a/${T}b.log 2>&1
python work/l22a/cat.py work/l22a/${T}_b.txt "${T}_a + ${T}b" work/l22a/${T}_a.txt work/l22a/fb_${T}b.inputs.txt
N=$(python -c "import sys;sys.path.insert(0,'.');from ng.solve import common as C;print(len(C.rows_of('work/l22a/${T}_b.txt')))")
python work/l22a/mkst.py work/l22a/${T}_b.txt $N ${T}2
FB_NW=2 python -u work/l22a/abeam.py work/l22a/h_${T}2.inputs.txt states/mesen/l22a_${T}2.mst g:8:0:40:192 ${T}c --alpha "$AL" --score xl --width $W --frames 750 --minhp 15 --need 10 --npeq 10 --npw 0.2 --ymax 193 --needs 816:30 > work/l22a/${T}c.log 2>&1
python work/l22a/cat.py work/l22a/${T}_full.txt "${T}_b + ${T}c (room-8 exit)" work/l22a/${T}_b.txt work/l22a/fb_${T}c.inputs.txt
tail -n 1 work/l22a/${T}c.log
