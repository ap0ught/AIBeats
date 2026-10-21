"""Track K helper: decode a data URL returned by the browser pane's JS (tool-result file) into logs/fix/u16k_<name>.jpg|png.
    python u16k_b64.py <tool-result file> <name>"""
import base64, json, re, sys
src, name = sys.argv[1], sys.argv[2]
txt = open(src, encoding="utf-8").read()
try:
    txt = "".join(p.get("text", "") for p in json.loads(txt))
except Exception:
    pass
ms = re.findall(r"data:image/(jpeg|png);base64,([A-Za-z0-9+/=]+)", txt)
for k, m in enumerate(ms):
    out = f"logs/fix/u16k_{name}{'' if len(ms) == 1 else '_' + str(k)}.{'jpg' if m[0] == 'jpeg' else 'png'}"
    open(out, "wb").write(base64.b64decode(m[1]))
    print(out, len(m[1]))
print(re.sub(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+", "<img>", txt)[:1500])
