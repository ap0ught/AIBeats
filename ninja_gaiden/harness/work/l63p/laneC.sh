while powershell -NoProfile -c "Get-CimInstance Win32_Process | ? { \$_.CommandLine -match 'lane[A].sh' } | % { \$_.ProcessId }" | grep -q "[0-9]"; do sleep 20; done
python work/l63p/bossbf.py 38932 logs/a56_6-5_r2d5.inputs.txt 151 > work/l63p/bf_65_r2d5.out 2>&1
python work/l63p/bossbf.py 38086 logs/a56_6-4b_r4k2.inputs.txt 151 --addr 0x3E --vals 0-5 > work/l63p/bf3e_64b_r4k2.out 2>&1
python work/l63p/bossbf.py 38932 logs/a56_6-5_r2d5.inputs.txt 151 --addr 0x3E --vals 0-5 > work/l63p/bf3e_65_r2d5.out 2>&1
