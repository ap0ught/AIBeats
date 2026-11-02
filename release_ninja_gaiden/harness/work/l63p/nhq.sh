while powershell -NoProfile -c "Get-CimInstance Win32_Process | ? { \$_.CommandLine -match 'nh[b]f.py' } | % { \$_.ProcessId }" | grep -q "[0-9]"; do sleep 20; done
python work/l63p/nhtf.py ref4751/room43_6-3 36007 36437 --tail Left --n 440 > work/l63p/nhtf_r43b.out 2>&1
python work/l63p/nhtf.py ref4751/room43_6-3 36007 36437 --tail Left --n 440 --poke 0xC9=133 > work/l63p/nhtf_r43b_js.out 2>&1
python work/l63p/nhtf.py ref4751/room44_6-3 36850 37117 --tail Right --n 280 > work/l63p/nhtf_r44b.out 2>&1
python work/l63p/nhtf.py ref4751/18_6-3_control 34562 34562 --rows logs/r4/r4_63_h4.inputs.txt --every 50 > work/l63p/nhtf_h4.out 2>&1
python work/l63p/nhtf.py ref4751/room43_6-3 35230 35982 --out work/l63p/leg_35231_35982.txt > /dev/null 2>&1
python work/l63p/nhbf.py ref4751/room43_6-3 35230 work/l63p/leg_35231_35982.txt --vals 0-255:8 --goal "X<=763 and y<=162" > work/l63p/nhbf_r43a.out 2>&1
python work/l63p/nhbf.py ref4751/room46_6-4b 38086 work/l63p/r4k2_fight.txt --vals 0-255:37 --goal "boss==0" > work/l63p/nhbf_64b.out 2>&1
python work/l63p/nhbf.py ref4751/room47_6-5 38932 work/l63p/r2d5_fight.txt --vals 0-255:37 --goal "boss==0 and m[0x6D]==21" > work/l63p/nhbf_65.out 2>&1
