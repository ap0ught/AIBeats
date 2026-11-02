cd "/g/AI World Record/Ninja Gaiden"
while powershell -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*a56_solve.py 20*' } | Select -First 1" | grep -q python; do sleep 20; done
python ng/stages/a56_solve.py 21 ref4751/room47_6-5 --width 8 --chunk 5 --tag b7 --hours 0.4 --prefix states/tmp/a56_blank151.inputs.txt --prefix-frames 151 > logs/a56_65_b7.out 2>&1
python ng/stages/a56_solve.py 19 ref4751/19_6-4a_control --width 8 --chunk 5 --tag b7 --hours 0.35 > logs/a56_64a_b7.out 2>&1
python ng/stages/a56_chain.py tmp/a56_5-1_c8_next states/tmp/a56_hist_A2.inputs.txt --from 13 --to 15 --tag A --width 8 --prefer none > logs/a56_chain_A.out 2>&1
