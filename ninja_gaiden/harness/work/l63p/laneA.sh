while ps aux | grep -v grep | grep -q bossbf; do sleep 10; done
python work/l63p/cyc.py 35981 'X<=739 and y<=128 and hp>=8' --both 1 --ks 2,3,4,5 --tail Left --n 80 --top 15 > work/l63p/cyc_r43w.out 2>&1
python work/l63p/cyc.py 36460 'X>=172 and y>=205 and rm==44' --both 1 --ks 2,3,4,5,6 --tail Right --n 110 --top 15 > work/l63p/cyc_r44e.out 2>&1
python work/l63p/cyc.py 35013 'X>=160 and y==160' --both 1 --ks 1,2,3,4 --tail Right --n 60 --top 15 > work/l63p/cyc_r42e.out 2>&1
