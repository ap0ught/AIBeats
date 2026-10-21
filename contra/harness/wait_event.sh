#!/bin/sh
# chain2 helper: wait until chain $1's log gets a new VERIFIED/FAILED line or chain.py with PID $2 exits; print the tail.
cd "/g/AI World Record/Contra/chain2"
L=logs/chain/$1/chain.log
n0=$(grep -cE "VERIFIED|FAILED|FAILS|finished" $L)
while [ $(grep -cE "VERIFIED|FAILED|FAILS|finished" $L) -eq $n0 ] && tasklist //FI "PID eq $2" | grep -q python; do sleep 30; done
grep -E "VERIFIED|FAILED|FAILS|finished" $L | tail -2
