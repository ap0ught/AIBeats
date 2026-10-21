#!/bin/bash
# big-boot probes on every pre-F1 Hornhead: root = first hit + 13, from the nearest earlier L12p_f bookmark
cd "/g/AI World Record/toads"
python - <<'PY' > logs/earlyboots_plan.txt
import json
for f0,f1,hp0,hit in json.load(open('knowledge/l12_hornhead_hits.json')):
    F=hit+13; bm=(F//500)*500
    print(F, f"L12p_f{bm}", bm)
PY
while read F BM B0; do
  echo "=== root $F from $BM" >> logs/earlyboots.txt
  python -u bootprobe2.py $F $BM $B0 5c >> logs/earlyboots.txt 2>&1
done < logs/earlyboots_plan.txt
echo DONE >> logs/earlyboots.txt
