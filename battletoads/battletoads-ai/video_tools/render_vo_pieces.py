"""re-render the pieces whose timing follows the narration: s04 (panels on the words) and the outro background"""
from sections import *
from vo_find import find, length
V0 = 0.35
st = [V0 + find("04", p) - 0.15 for p in ["the left side", "over on the right", "got the controller", "there's the timer",
                                           "some of the numbers", "at the bottom"]]
p_screen("s04_screen", starts=st, end=V0 + length("04") + 0.9)
print("s04", [round(x, 2) for x in st], flush=True)
p_outro_bg()
print("s11 done", flush=True)
