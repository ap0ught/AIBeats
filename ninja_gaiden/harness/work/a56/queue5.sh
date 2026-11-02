cd "/g/AI World Record/Ninja Gaiden"
while powershell -c "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*tag b9*' } | Select -First 1" | grep -q python; do sleep 20; done
python ng/stages/a56_solve.py 21 ref4751/room47_6-5 --width 8 --chunk 5 --tag b10 --hours 0.5 --prefix states/tmp/a56_blank151.inputs.txt --prefix-frames 151 > logs/a56_65_b10.out 2>&1
