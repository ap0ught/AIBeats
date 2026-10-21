#!/usr/bin/env bash
# Robustness runs of the stage 1 and stage 5 solvers from other start conditions, one after the other
# (3 emulators at a time). Logs: logs/s1/solve_<w>.log, logs/s5/solve_<w>.log.
cd "/g/AI World Record/Contra" || exit 1
python tools/s5_mkstates.py 0,1,37 > logs/s5/mkstates.log 2>&1
for w in "$@"; do
  case "$w" in
    s5:*) k="${w#s5:}"; python -m contra.stages.s5 "s5/pre_$k" "$k" > "logs/s5/solve_$k.log" 2>&1
          python tools/s5_finish.py "s5/pre_$k" "$k" > "logs/s5/finish_$k.log" 2>&1 ;;
    s1:*) k="${w#s1:}"; python -m contra.stages.s1 "s1/pre_$k" "$k" --open "logs/s1/open_$k.inputs.txt" > "logs/s1/solve_$k.log" 2>&1
          python tools/s1_finish.py "$k" > "logs/s1/finish_$k.log" 2>&1 ;;
  esac
done
echo "queue done" > logs/s1/queue_done.txt
