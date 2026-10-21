"""Edit tools/s7_phase_table.py: the main table uses the solves made with the FINAL code (scan files F1/F2/F3 and
'final'); solves from earlier code versions of the second pass are listed separately."""
from pathlib import Path

p = Path(r"tools\s7_phase_table.py")
s = p.read_text(encoding="utf-8")


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''rows = [slim(r) for r in scan if not r.get("name")]
others = [slim(r) for r in scan if r.get("name")]
rows.sort(key=lambda r: (r["start_phase_mod128"] if r["start_phase_mod128"] is not None else 999, r["start_fc"] or 0))
good = [r for r in rows if r["ok"] and r["verified"] and str(r["check_inputs"]).endswith("PASS")]
by_phase = {}
for r in good:
    k = r["start_phase_mod128"]
    if k not in by_phase or r["frames"] < by_phase[k]["frames"]:
        by_phase[k] = r
''', '''FINAL = ("F1.jsonl", "F2.jsonl", "F3.jsonl", "final.jsonl")
srt = lambda r: (r["start_phase_mod128"] if r["start_phase_mod128"] is not None else 999, r["start_fc"] or 0)  # noqa: E731
rows = sorted([slim(r) for r in scan if r["scan_file"] in FINAL], key=srt)        # final code: phases and chains
earlier = sorted([slim(r) for r in scan if r["scan_file"] not in FINAL], key=srt)
others = [r for r in rows if r["name"]]
others_earlier = [r for r in earlier if r["name"]]
good = [r for r in rows if r["ok"] and r["verified"] and str(r["check_inputs"]).endswith("PASS")]
by_phase = {}
for r in good:
    k = r["start_phase_mod128"]
    if k not in by_phase or r["frames"] < by_phase[k]["frames"]:
        by_phase[k] = r
''')
rep('''    chains = []
    for r in others:
        if r["state"] and r["state"].startswith("s6/") and r["frames"]:
            n6 = next((f for f in s6["full_solves"] if r["state"] == f"s6/{f['name']}_end"), None)
            chains.append({"s6_run": n6["name"] if n6 else r["state"], "s6_start_fc": n6["start_fc"] if n6 else None,
                           "s6_frames": n6["frames"] if n6 else None, "s7_start_fc": r["start_fc"],
                           "s7_frames": r["frames"], "s7_lag": r["lag"], "s7_verified": r["verified"],
                           "sum": (n6["frames"] + r["frames"]) if n6 else None,
                           "vs_record_pair": (n6["frames"] + r["frames"] - REC6 - REC7) if n6 else None})''',
    '''    def chain_list(src):
        out_c = []
        for r in src:
            if r["state"] and r["state"].startswith("s6/") and r["frames"]:
                n6 = next((f for f in s6["full_solves"] if r["state"] == f"s6/{f['name']}_end"), None)
                out_c.append({"s6_run": n6["name"] if n6 else r["state"], "s6_start_fc": n6["start_fc"] if n6 else None,
                              "s6_frames": n6["frames"] if n6 else None, "s7_run": r["name"],
                              "s7_start_fc": r["start_fc"], "s7_frames": r["frames"], "s7_lag": r["lag"],
                              "s7_verified": r["verified"], "sum": (n6["frames"] + r["frames"]) if n6 else None,
                              "vs_record_pair": (n6["frames"] + r["frames"] - REC6 - REC7) if n6 else None})
        return sorted(out_c, key=lambda c: (c["sum"] is None, c["sum"]))

    chains = chain_list(others)''')
rep('''        "measured_chains": sorted(chains, key=lambda c: (c["sum"] is None, c["sum"])),''',
    '''        "measured_chains": chains,
        "measured_chains_earlier_code": chain_list(others_earlier),''')
rep('''    "table": rows,
    "other_solves_from_named_states": others,''', '''    "table": rows,
    "solves_with_earlier_code_versions_of_the_second_pass": earlier,''')
rep('''for r in others:
    print("named:", r["name"], r["state"], "fc", r["start_fc"], "frames", r["frames"], "lag", r["lag"], "verified", r["verified"])''',
    '''print("earlier code versions:", [(r["start_fc"], r["frames"], r["name"]) for r in earlier])''')
p.write_text(s, encoding="utf-8")
print("ok")
