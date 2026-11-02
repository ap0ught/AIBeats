# wait until free RAM >= ${GATE_GB:-3.0} GB (poll every 2 min), then run the command
until python -c "from ng.fastcore import free_ram_gb; import sys,os; sys.exit(0 if free_ram_gb() >= float(os.environ.get('GATE_GB','3.0')) else 1)"; do sleep 120; done
"$@"
