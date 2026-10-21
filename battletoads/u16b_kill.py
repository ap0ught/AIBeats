"""u16b: stop ONE of my own jobs by a command-line fragment that must contain 'u16b' (python pid + its EmuHawk child, by PID only).
    python u16b_kill.py "u16b_climb.py r4" """
import subprocess, json, sys
frag = sys.argv[1]
assert "u16b" in frag or frag.startswith("assemble.py up16b") or frag.startswith("rngfit.py") and " B" in frag, "only my own jobs"
ps = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='EmuHawk.exe'\" | "
      "Select-Object ProcessId, ParentProcessId, Name, CommandLine | ConvertTo-Json -Compress")
rows = json.loads(subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True).stdout)
if isinstance(rows, dict):
    rows = [rows]
mine = [r for r in rows if r["Name"].lower() == "python.exe" and frag in (r["CommandLine"] or "") and "u16b_kill" not in (r["CommandLine"] or "")]
for r in mine:
    kids = [k for k in rows if k["ParentProcessId"] == r["ProcessId"] and k["Name"].lower().startswith("emuhawk")]
    for k in kids + [r]:
        print("stopping", k["ProcessId"], k["Name"], (k["CommandLine"] or "")[-80:])
        subprocess.run(["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {k['ProcessId']} -Force"])
if not mine:
    print("nothing matches", frag)
