while pgrep -f "tallyscan.sh" > /dev/null || ps aux | grep -q "[t]allyscan"; do sleep 5; done
bash work/l63p/endscan.sh > work/l63p/endscan.out 2>&1
