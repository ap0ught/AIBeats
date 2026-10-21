# Stop one of MY solver processes and the emulators it started (by PID, after checking the command lines).
#   powershell -File tools\s1_kill_mine.ps1 <pattern in the python command line, e.g. contra.stages.s1>
param([string]$pattern)
$py = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like "*$pattern*" }
foreach ($p in $py) {
    $kids = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'EmuHawk.exe' -and $_.ParentProcessId -eq $p.ProcessId -and $_.CommandLine -like '*Contra\emu_tmp*' }
    Write-Output ("stopping python " + $p.ProcessId + " and " + @($kids).Count + " emulators")
    Stop-Process -Id $p.ProcessId -Force -Confirm:$false
    foreach ($k in $kids) { Stop-Process -Id $k.ProcessId -Force -Confirm:$false }
    Start-Sleep -Seconds 1
    Remove-Item -Recurse -Force ("emu_tmp\" + $p.ProcessId + "_*") -ErrorAction SilentlyContinue
}
