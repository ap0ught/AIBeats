# Start detached emulator workers for the stage 7 second pass:  powershell -File tools\s7_workers.ps1 w1 w2
# Stop them: create a file STOP_<name> in the job folder (tools/s7_job.py JOBDIR).
$jd = "~\AppData\Local\Temp\claude\G--AI-World-Record\d5fcfe9d-4ac8-40d5-8a32-00e8e94fae89\scratchpad\s7b\jobs"
New-Item -ItemType Directory -Force $jd | Out-Null
foreach ($n in $args) {
    if (Test-Path "$jd\STOP_$n") { Remove-Item "$jd\STOP_$n" -Confirm:$false }
    $p = Start-Process -FilePath python -ArgumentList @("tools/s6_worker.py", $n, "`"$jd`"") -WorkingDirectory "" -WindowStyle Hidden -RedirectStandardOutput "$jd\worker_$n.log" -RedirectStandardError "$jd\worker_$n.err" -PassThru
    Write-Output "$n python pid $($p.Id)"
    Start-Sleep -Seconds 6
}
