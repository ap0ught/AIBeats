#!/bin/bash
cd "/g/AI World Record/Ninja Gaiden"
for ov in "27050=B+Down" "27049-27050=Right" "27049-27050=-"; do echo "== $ov"; python work/l52b/tweak.py logs/l52b_e6_poweron.inputs.txt "$ov" 2>&1 | tail -2; done
