cd "/g/AI World Record/Ninja Gaiden"
python ng/stages/a56_solve.py 20 ref4751/room46_6-4b --width 8 --chunk 5 --tag b9 --hours 0.5 --prefix states/tmp/a56_blank151.inputs.txt --prefix-frames 151 > logs/a56_64b_b9.out 2>&1
python ng/stages/a56_solve.py 15 ref4751/15_5-4_control --width 8 --chunk 5 --tag b9 --hours 0.3 > logs/a56_54_b9.out 2>&1
