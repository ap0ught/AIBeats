"""Stage (area) table of Ninja Gaiden (NES, US): RAM $6D value -> name, first room ($6E), boss.
Verified: HUD "STAGE-x-y" screenshots of every value (shots/lvl_hud.png) and the bank-0 table $AF2C."""

NAMES = ["1-1", "1-2", "2-1", "2-2", "2-3", "3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "4-4",
         "5-1", "5-2", "5-3", "5-4", "6-1", "6-2", "6-3", "6-4a", "6-4b", "6-5"]
FIRST_ROOM = [0, 1, 2, 6, 9, 10, 11, 12, 13, 16, 17, 21, 22, 23, 27, 34, 35, 36, 41, 45, 46, 47]   # ROM bank 0 $AF2C
CUTSCENE = [0, 1, 255, 255, 2, 255, 255, 3, 4, 255, 255, 5, 255, 255, 6, 7, 255, 255, 8, 9, 10, 11]  # bank 0 $AF9A
BOSS = {1: "Barbarian", 4: "Bomberhead", 7: "Basaquer", 11: "Kelbeross", 15: "Bloody Malth",
        19: "Masked Devil", 20: "Jaquio", 21: "Demon (statue)"}
LAST = 21


def name(stage: int) -> str:
    return NAMES[stage] if 0 <= stage < len(NAMES) else f"?{stage}"
