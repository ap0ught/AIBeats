"""Unzip downloaded TAS movie archives as DATA. Run with:  python -I tools/unzip_tas.py

Lists every entry, refuses anything whose name is not a plain file name with a known movie extension, and
writes the entries next to the zip in dl/tas/. Nothing in there is ever executed.
"""
import hashlib
import sys
import zipfile
from pathlib import Path

D = Path(r"dl\tas")
OK_EXT = {".fm2", ".bk2", ".fmv", ".fcm", ".txt"}
for z in sorted(D.glob("*.zip")):
    with zipfile.ZipFile(z) as zf:
        for info in zf.infolist():
            name = info.filename
            safe = Path(name).name == name and Path(name).suffix.lower() in OK_EXT and info.file_size < 20_000_000
            print(f"{z.name}: {name!r} {info.file_size} bytes {'OK' if safe else 'REFUSED'}")
            if not safe:
                continue
            data = zf.read(info)
            out = D / f"{z.stem}_{name}"
            out.write_bytes(data)
            print("   ->", out.name, hashlib.sha1(data).hexdigest())
