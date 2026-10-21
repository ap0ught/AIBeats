# Start a detached stage 7 phase scan process:  powershell -File tools\s7_scan_bg.ps1 <tag> <fc list> [--force-lead]
# Log: logs\s7\scan\<tag>.log ; results: logs\s7\scan\<tag>.jsonl
$tag = $args[0]
$root = ""
New-Item -ItemType Directory -Force "$root\logs\s7\scan" | Out-Null
$al = @("-u", "tools/s7_phase_scan.py", $tag, $args[1])
for ($i = 2; $i -lt $args.Count; $i++) { $al += $args[$i] }
$p = Start-Process -FilePath python -ArgumentList $al -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput "$root\logs\s7\scan\$tag.log" -RedirectStandardError "$root\logs\s7\scan\$tag.err" -PassThru
Write-Output "started scan $tag (python pid $($p.Id))"
