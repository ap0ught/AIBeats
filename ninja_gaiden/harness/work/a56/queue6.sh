cd "/g/AI World Record/Ninja Gaiden"
until [ -f logs/a56_65_b10.out ]; do sleep 15; done
sleep 30
while powershell -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*tag b10*' } | Select -First 1" | grep -q python; do sleep 20; done
python ng/stages/a56_solve.py 15 ref4751/15_5-4_control --width 8 --chunk 5 --tag b9 --hours 0.3 > logs/a56_54_b9.out 2>&1
