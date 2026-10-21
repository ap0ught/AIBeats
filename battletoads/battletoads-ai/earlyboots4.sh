#!/bin/bash
cd "/g/AI World Record/toads"
for spec in "6240 L12p_f6000 6000" "86 L12p_f0 0" "756 L12p_f500 500" "1387 L12p_f1000 1000" "1908 L12p_f1500 1500" "2545 L12p_f2500 2500" "2843 L12p_f2500 2500"; do
  set -- $spec
  echo "=== root $1 from $2" >> logs/earlyboots4.txt
  python -u bootprobe4.py $1 $2 $3 5c >> logs/earlyboots4.txt 2>&1
  sleep 3
done
echo DONE >> logs/earlyboots4.txt
