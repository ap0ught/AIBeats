# Stop one of MY detached stage 7 solver processes and its emulator:  powershell -File tools\s7_stop_solve.ps1 <python pid>
# Checks the command lines first (python must be running a tools/s6_solve.py or s7_phase_scan.py job; the emulator
# must be a child of that python and use Contra\emu_tmp\<pid>_...).
$id = [int]$args[0]
$py = Get-CimInstance Win32_Process -Filter "ProcessId=$id"
if (-not $py) { Write-Output "python $id is not running"; exit 0 }
if ($py.CommandLine -notlike '*s6_solve.py*' -and $py.CommandLine -notlike '*s7_phase_scan.py*' -and $py.CommandLine -notlike '*s6_worker.py*') { Write-Output "pid $id is not one of my solver processes: $($py.CommandLine)"; exit 1 }
$emus = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'EmuHawk.exe' -and $_.ParentProcessId -eq $id -and $_.CommandLine -like "*Contra\emu_tmp\$($id)_*" }
Stop-Process -Id $id -Force -Confirm:$false
foreach ($e in $emus) { Stop-Process -Id $e.ProcessId -Force -Confirm:$false; Write-Output "stopped emulator $($e.ProcessId)" }
Start-Sleep -Seconds 2
Get-ChildItem "emu_tmp" | Where-Object { $_.Name -like "$($id)_*" } | Remove-Item -Recurse -Force -Confirm:$false
Write-Output "stopped python $id"
