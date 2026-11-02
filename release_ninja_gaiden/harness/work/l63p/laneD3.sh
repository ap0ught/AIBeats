python work/l63p/mdjs3.py > work/l63p/mdjs3.out 2>&1
python -u work/l63p/b63.py 34880 34880 r41n --goal 'rm==42' --score 'X-y' --frames 140 --width 100 --minhp 12 --alpha 'Right|A+Right|B+Right|-|Left|A+Left|A' --dbg 20 > work/l63p/b_r41n.out 2>&1
python -u work/l63p/b63.py 35950 35950 r43w --goal 'X<=739 and y<=128' --score '-X-y' --frames 100 --width 100 --minhp 8 --alpha 'Left|A+Left|B+Left|-|Right|A+Right|A' --dbg 20 > work/l63p/b_r43w.out 2>&1
