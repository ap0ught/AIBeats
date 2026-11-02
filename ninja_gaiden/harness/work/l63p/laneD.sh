while powershell -NoProfile -c "Get-CimInstance Win32_Process | ? { \$_.CommandLine -match 'lane[C]\.sh' } | % { \$_.ProcessId }" | grep -q "[0-9]"; do sleep 20; done
python work/l63p/mdjs2.py > work/l63p/mdjs2.out 2>&1
python work/l63p/seqgrid.py 35981 'X<=739 and y<=128 and hp>=8' --gen work/l63p/gen_r43w.py > work/l63p/sg_r43w.out 2>&1
python -u work/l63p/b63.py 34880 34880 r41n --goal 'rm==42' --score 'X-y' --frames 140 --width 100 --minhp 12 --alpha 'Right|A+Right|B+Right|-|Left|A+Left|A' --dbg 20 > work/l63p/b_r41n.out 2>&1
