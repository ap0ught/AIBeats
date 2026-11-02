#!/bin/sh
# usage: runw2.sh <start> <step> <out>
cd "/g/AI World Record/Ninja Gaiden"
b=$1
while [ $b -le 113 ]; do
  timeout 900 python -u work/l42p/beam42.py $b 2 --width 24 --frames 200 --tag w2_$b >> $3 2>&1
  b=$((b + $2))
done
echo DONE >> $3
