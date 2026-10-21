import subprocess, sys
def run(args):
    print(">>", " ".join(args), flush=True); rc = subprocess.run([sys.executable, "-u"] + args, stdout=sys.stdout, stderr=subprocess.STDOUT).returncode; print("<< rc", rc, flush=True); return rc
if run(["assemble.py", "up11", "L1b", "L3u", "L3skipu", "L4c5", "L6c", "L8c", "L9c", "L10t", "L11r", "L12r", "L13w6"]): sys.exit(1)
run(["video_text2.py", "up11"]); run(["render_overlay.py", "up11"]); print("PIPELINE DONE", flush=True)
