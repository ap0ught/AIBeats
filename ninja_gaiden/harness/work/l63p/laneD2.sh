while powershell -NoProfile -c "Get-CimInstance Win32_Process | ? { \$_.CommandLine -match 'seqgri[d]' } | % { \$_.ProcessId }" | grep -q "[0-9]"; do sleep 15; done
python work/l63p/mdjs2.py --t2 37299,37301 --dr 2-26 --step 4 > work/l63p/mdjs2.out 2>&1
python -u work/l63p/b63.py 34880 34880 r41n --goal 'rm==42' --score 'X-y' --frames 140 --width 100 --minhp 12 --alpha 'Right|A+Right|B+Right|-|Left|A+Left|A' --dbg 20 > work/l63p/b_r41n.out 2>&1
python -u work/l63p/b63.py 35950 35950 r43w --goal 'X<=739 and y<=128' --score '-X-y' --frames 100 --width 100 --minhp 8 --alpha 'Left|A+Left|B+Left|-|Right|A+Right|A' --dbg 20 > work/l63p/b_r43w.out 2>&1
