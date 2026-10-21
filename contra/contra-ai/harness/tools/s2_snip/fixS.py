old = G["snap_after"]
S = bc.Sess(e)
S.rows = list(G["rows_to_boss"]); S.pad = old[2].copy(); S.s = old[3]
e.cmd(f"mload {old[0]}")
G["S"] = S
G["snap_after"] = S.snapshot()
print(len(S.rows), S.s["frame"], S.e.state()["frame"])
