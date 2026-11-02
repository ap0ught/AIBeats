#!/bin/bash
# usage: gate.sh <outfile> <command...> : waits for free RAM >= 3 GB (after 10 min: >= 2 GB, single job), then runs it
out=$1; shift; t0=$(date +%s)
while true; do
  f=$(python -c "import sys; sys.path.insert(0,'.'); from ng.fastcore import free_ram_gb; print(int(free_ram_gb()*100))")
  if [ "$f" -ge 300 ]; then break; fi
  if [ $(( $(date +%s) - t0 )) -gt 600 ] && [ "$f" -ge 200 ]; then export MINGB=1.8; break; fi
  sleep 30
done
echo "start $(date +%H:%M:%S) free ${f}" > "$out"
"$@" >> "$out" 2>&1
