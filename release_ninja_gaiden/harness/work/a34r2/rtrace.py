"""Acts 3-4 record trace (agent a34 round 2): work/a12r2/rtrace.py (a56's record_trace.py, HUD mask y 60) on
states/tmp/a34r2_vid/<seg>.
    python work/a34r2/rtrace.py <seg> <control video frame> <end video frame> <out.json>"""
import sys
sys.path.insert(0, "work/a12r2")
sys.path.insert(0, "work/a56r2")
import rtrace as RT  # noqa: E402
RT.R.D0 = "states/tmp/a34r2_vid/"
if __name__ == "__main__":
    RT.R.main()
