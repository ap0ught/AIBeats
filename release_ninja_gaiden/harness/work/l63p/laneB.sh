until grep -q "^kills" work/l63p/mdjs1.out; do sleep 10; done
python work/l63p/cyc.py 36790 'X>=603 and y<=100' --both 1 --ks 3,4,5,6,7 --tail Right --n 110 --top 15 > work/l63p/cyc_r44w.out 2>&1
python work/l63p/cyc.py 35168 'X<=1879 and y>=190 and y<=192' --both 1 --ks 2,3,4,5,6 --tail Left --n 100 --top 15 > work/l63p/cyc_r43e.out 2>&1
python work/l63p/cyc.py 35095 'rm==43' --both 1 --ks 2,3,4,5 --tail Left --n 80 --top 15 > work/l63p/cyc_r42x.out 2>&1
python -u work/l63p/b63.py 36790 36790 r44w --goal 'X>=603 and y<=100' --score 'X*2-y' --frames 130 --width 100 --alpha 'Left|A+Left|-|Right|A+Right|A' --dbg 20 > work/l63p/b_r44w.out 2>&1
python work/l63p/seqgrid.py 36120 'X<=554 and y<=128 and hp>=8' --gen work/l63p/gen_r43w2.py > work/l63p/sg_r43w2.out 2>&1
python -u work/l63p/b63.py 35073 35073 r42x --goal 'rm==43' --score '-y-0.3*abs(X-184)' --frames 120 --width 100 --alpha 'Left|A+Left|-|Right|A+Right|A' --dbg 20 > work/l63p/b_r42x.out 2>&1
