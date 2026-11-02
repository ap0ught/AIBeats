cd "/g/AI World Record/Ninja Gaiden"
python ng/stages/a56_solve.py 15 ref4751/15_5-4_control --width 8 --chunk 5 --tag b13 --hours 0.2 > logs/a56_54_b13.out 2>&1
python ng/stages/a56_solve.py 20 ref4751/room46_6-4b --width 8 --chunk 5 --tag b13 --hours 0.5 --prefix states/tmp/a56_blank151.inputs.txt --prefix-frames 151 > logs/a56_64b_b13.out 2>&1
python ng/stages/a56_chain.py tmp/a56_5-1_c8_next states/tmp/a56_hist_A2.inputs.txt --from 13 --to 15 --tag A --width 8 --prefer none > logs/a56_chain_A.out 2>&1
