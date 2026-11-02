#!/bin/bash
cd "/g/AI World Record/Ninja Gaiden"
for f in e5 e6; do
MINGB=1.8 python -u work/l52b/nhchk.py l52a_d3_25518 states/mesen/l52b_e1_25518.mst 25518 work/l52b/${f}_from25519.txt - $f
python -u -m ng.solve.verify chain coord_l52b_$f logs/l52b_${f}_poweron.inputs.txt
done
