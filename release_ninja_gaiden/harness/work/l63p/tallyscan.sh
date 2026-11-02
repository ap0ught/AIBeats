P="python work/l63p/nh_trans63.py ref4751/room46_6-4b 38188 --n 800 --dir none"
$P --poke 0x64=5 --start 38791,38792,38793,38794,38795,38796 | grep "^K"
$P --poke 0x64=1 --start 38780,38781,38782 | grep "^K"
$P --poke 0x63=147 --start 38774,38775,38776 | grep "^K"
$P --poke 0x63=145 --start 38768,38769,38770 | grep "^K"
for v in 0 1 30 58 59 60; do $P --poke 0x62=$v --start 38777,38778,38779 | grep "^K"; done
for v in 0 1 2 3 5; do $P --poke 0x3E=$v --start 38777,38778,38779 | grep "^K"; done
