param([string]$pat = "NO_DEFAULT_PATTERN")
$py = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*$pat*" }
foreach ($p in $py) {
  $emus = Get-CimInstance Win32_Process -Filter "Name='EmuHawk.exe'" | Where-Object { $_.CommandLine -like "*Ninja Gaiden\emu_tmp\$($p.ProcessId)_*" }
  Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
  foreach ($e in $emus) { Stop-Process -Id $e.ProcessId -Force -ErrorAction SilentlyContinue; "killed emu $($e.ProcessId)" }
  "killed py $($p.ProcessId) $($p.CommandLine)"
}
