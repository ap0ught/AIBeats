#!/bin/bash
# usage: leg2.sh b1 b2 ...  (tosser-1 spawn BF values); builds the top state and beams to X>=1251 y<=96
cd "/g/AI World Record/Ninja Gaiden"
for b in "$@"; do
  p=$(( (b - 1 + 256) % 256 ))
  venv/Scripts/python.exe work/l32p/mkst.py states/mesen/l32p_tas12054.mst work/l32p/h_tas12054.inputs.txt work/l32p/noaxe179.txt top_b$b --bf $p
  FB_NW=1 venv/Scripts/python.exe -u work/l32p/zbeam.py work/l32p/h_top_b$b.inputs.txt states/mesen/l32p_top_b$b.mst "any,z:1251:96" l2_b$b --score h --hgx 1251 --hgy 96 --hx0 0 --width 40 --frames 140 --alpha "Right|A+Right|-|B+Right|A+B+Right|Left|A+Left|A" > work/l32p/zb_l2_b$b.log 2>&1
  echo "b $b: $(tail -1 work/l32p/zb_l2_b$b.log)"
done
