#!/bin/bash
# block until free RAM >= $1 GB (default 2.5) and no HOLD_FARMS file (prints the value)
need=${1:-2.5}
while true; do
  f=$(powershell -NoProfile -c "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)")
  if [ ! -e "/g/AI World Record/Ninja Gaiden/logs/HOLD_FARMS" ] && python -c "import sys; sys.exit(0 if $f >= $need else 1)"; then echo "free $f"; exit 0; fi
  sleep 20
done
