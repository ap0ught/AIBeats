"""EARLY track helper (2026-10-09): decode a contact sheet that the browser pane's JS returned as a data URL (the tool
result file) into logs/fix/<name>.jpg.     python early_b64.py <tool-result file> <name>"""
import base64, json, re, sys
src, name = sys.argv[1], sys.argv[2]
txt = open(src, encoding="utf-8").read()
try:
    txt = "".join(p.get("text", "") for p in json.loads(txt))
except Exception:
    pass
m = re.search(r"data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)", txt)
out = f"logs/fix/{name}.{'jpg' if m.group(1) == 'jpeg' else 'png'}"
open(out, "wb").write(base64.b64decode(m.group(2)))
print(out, len(m.group(2)))
