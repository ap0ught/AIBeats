cd "/g/AI World Record/Ninja Gaiden"
while powershell -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*a56_solve.py 20*' } | Select -First 1" | grep -q python; do sleep 20; done
python ng/stages/a56_chain.py tmp/a56_5-1_c8_next states/tmp/a56_hist_A2.inputs.txt --from 13 --to 15 --tag A --width 8 --prefer none > logs/a56_chain_A.out 2>&1
