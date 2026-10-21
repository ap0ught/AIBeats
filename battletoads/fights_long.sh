#!/bin/bash
# the pre-F1 fights again with the long run-up boots (FB_LONG): a = spawn frame, join window = 10..50 frames after the body is gone
cd "/g/AI World Record/toads"
for spec in "702 839-879 5c e2" "1343 1711-1751 5c e3" "1859 1992-2032 5c e4" "2502 2709-2749 5c e5" "2805 2978-3018 5c e6" "2160 2379-2419 62 w1" "3038 3429-3469 62 w2" "3421 3769-3809 62 w3"; do
  set -- $spec
  echo "=== fight $4: a=$1 window $2 id $3" >> logs/fights_long.txt
  FB_LONG=1 python -u fightbeam.py L12r $1 $2 $3 $4 >> logs/fights_long.txt 2>&1
  sleep 3
done
echo DONE >> logs/fights_long.txt
