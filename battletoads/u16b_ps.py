"""u16b: list python / EmuHawk processes (pid, parent, MB, command tail) - to stop only my own jobs by PID."""
import subprocess, json, sys
ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='EmuHawk.exe'\" | "
      "Select-Object ProcessId, ParentProcessId, Name, WorkingSetSize, CommandLine | ConvertTo-Json -Compress")
out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout
rows = json.loads(out) if out.strip() else []
if isinstance(rows, dict):
    rows = [rows]
by = {r["ProcessId"]: r for r in rows}
for r in sorted(rows, key=lambda r: (r["Name"], r["ProcessId"])):
    c = r["CommandLine"] or ""
    if r["Name"].lower().startswith("emuhawk"):
        par = by.get(r["ParentProcessId"])
        c = "EmuHawk of: " + ((par["CommandLine"] or "")[-90:] if par else "(parent gone)")
    else:
        c = c[-110:]
    print(r["ProcessId"], r["ParentProcessId"], r["Name"], int(r["WorkingSetSize"] / 1e6), "MB |", c)
