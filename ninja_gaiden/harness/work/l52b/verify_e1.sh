#!/bin/bash
cd "/g/AI World Record/Ninja Gaiden"
python -u work/l52b/nhchk.py l52a_d3_25518 states/mesen/l52b_e1_25518.mst 25518 work/l52b/e1_from25519.txt 26025,26506,26852,27118,27397 e1
python -u -m ng.solve.verify chain coord_l52b_e1 logs/l52b_e1_poweron.inputs.txt
