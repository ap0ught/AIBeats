#!/bin/sh
# serial queue: each line of work/r5/queue.txt = "<log name> <command...>"; done lines are moved to queue_done.txt
cd "/g/AI World Record/Ninja Gaiden"
export A34_AIRRUN=1 A34_HMAX=1 A34_SWITCH=1 A34_FINE=1
while true; do
  line=$(grep -v '^#' work/r5/queue.txt | grep . | head -1)
  if [ -z "$line" ]; then sleep 20; continue; fi
  if [ "$line" = "STOP" ]; then exit 0; fi
  name=${line%% *}; cmd=${line#* }
  grep -vxF "$line" work/r5/queue.txt > work/r5/queue.tmp; mv work/r5/queue.tmp work/r5/queue.txt
  echo "$(date +%H:%M:%S) $line" >> work/r5/queue_done.txt
  python work/r5/gate.py logs/r5/$name.out $cmd
done
