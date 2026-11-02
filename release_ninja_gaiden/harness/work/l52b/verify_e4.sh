#!/bin/bash
cd "/g/AI World Record/Ninja Gaiden"
MINGB=1.8 python -u work/l52b/nhchk.py l52a_d3_25518 states/mesen/l52b_e1_25518.mst 25518 work/l52b/e4_from25519.txt 26848,26995,27081,27360 e4
python -u -m ng.solve.verify chain coord_l52b_e4 logs/l52b_e4_poweron.inputs.txt
