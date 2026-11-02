P="python work/l63p/nh_trans63.py ref4751/room47_6-5 39084 --n 470 --dir none --start none"
for t in 147 146 145; do for v in 0 1 2 3 4 5; do $P --poke 0x63=$t,0x3E=$v | grep "^K"; done; done
$P --poke 0x64=5 | grep "^K"
