# Start a detached stage 7 solve:  powershell -File tools\s7_solve_bg.ps1 <state> <out name> [--param k=v ...]
# Output goes to logs\s7\<out>.solve.log ; the solver itself writes logs\s7\<out>.inputs.txt / .seg.json
$state = $args[0]
$out = $args[1]
$root = ""
$al = @("-u", "tools/s6_solve.py", "7", $state, $out)
for ($i = 2; $i -lt $args.Count; $i++) { $al += $args[$i] }
$p = Start-Process -FilePath python -ArgumentList $al -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput "$root\logs\s7\$out.solve.log" -RedirectStandardError "$root\logs\s7\$out.solve.err" -PassThru
Write-Output "started $out (python pid $($p.Id))"
