#!/bin/bash
# usage: t.sh tag spec n [from] -> compact trace
cd "/g/AI World Record/Ninja Gaiden"
python work/l33/wtest.py $1 "$2" $3 | awk -v f=${4:-1} '$1>=f {printf "%s %s ryu %s %s an %s np %s boss %s bx %s by %s C8 %s hp %s\n",$1,$2,$4,$5,$7,$9,$11,$12,$13,$15,$NF}'
