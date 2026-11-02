"""RAM-map proofs: experiments from savestates, each printing PASS/FAIL with the numbers, plus screenshots in
shots/verify/. Results -> knowledge/ram_verify.json (knowledge/ram_notes.md explains them).

    python tools/ram_verify.py

Needs states/intro_fastest_end (1-1, first control frame; tools/intro_skip.py) and the reference states of the
TAS replay in states/ref4751/ (tools/events.py logs/tas4751.inputs.txt --states ref4751).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ng.emulator import BizHawk, KNOWLEDGE_DIR, STATES_DIR  # noqa: E402
from ng.mode import TICKS  # noqa: E402

RES = {}


def check(name, ok, **info):
    RES[name] = {"pass": bool(ok), **info}
    print(("PASS " if ok else "FAIL ") + name, info, flush=True)


def ryu_sprites(e):
    """Sprites of the PPU OAM near Ryu: (x, y, tile, attr) of every visible sprite."""
    o = e.oam()
    return [(o[i + 3], o[i], o[i + 1], o[i + 2]) for i in range(0, 256, 4) if o[i] < 0xEF]


def main():
    e = BizHawk(log_name="ram_verify.log")
    try:
        e.tick(TICKS)
        # ---- 1. inputs, X with sub-pixel, speed ($2A held, $29 new, $86.$85 x, $AD.$AC speed) ----
        e.load("intro_fastest_end")
        s0 = e.state()
        e.trace(True)
        e.run([("Right",)] * 20)
        tr = e.last_trace
        xs = [t.x * 256 + t.xsub for t in tr]
        d = [b - a for a, b in zip(xs, xs[1:])]
        check("pad_held_$2A_new_$29", all(t.pad == 1 for t in tr) and tr[0].padnew == 1 and all(t.padnew == 0 for t in tr[1:]),
              pad=[t.pad for t in tr[:3]], padnew=[t.padnew for t in tr[:3]])
        check("x_$86_sub_$85_walk_1.5px", all(v == 384 for v in d), deltas_in_1_256px=sorted(set(d)),
              x_first=(tr[0].x, tr[0].xsub), x_last=(tr[-1].x, tr[-1].xsub), speed=(tr[-1].vx, tr[-1].vx_sub))
        sp = ryu_sprites(e)
        e.screenshot("verify/x_after_20_right")
        check("x_matches_sprite_oam", any(abs(x - tr[-1].x) <= 8 for x, *_ in sp), ram_x=tr[-1].x,
              oam_x=sorted(x for x, *_ in sp)[:6])
        # ---- 2. jump: $89.$87 vertical speed (signed), $8A y, $84 bit 2 airborne ----
        e.run([("A",)] + [()] * 70)
        tr = e.last_trace
        ys = [t.y for t in tr]
        check("jump_y_$8A_vy_$89", tr[0].vy == 0xFC and min(ys) < ys[0] - 30 and ys[-1] == s0.y and (tr[1].rflags & 4),
              vy_first=tr[0].vy, y_min=min(ys), y_start=ys[0], y_end=ys[-1], airborne_flag=tr[1].rflags)
        # ---- 3. scroll: x stops near the middle, $51/$52 stage x grows ----
        e.run([("Right",)] * 200)
        tr = e.last_trace
        sc = [t.scroll_scr * 256 + t.scroll for t in tr]
        check("scroll_$51_$52_while_x_fixed", sc[-1] > sc[0] + 100 and len(set(t.x for t in tr[-50:])) == 1,
              scroll_first=sc[0], scroll_last=sc[-1], x_last=tr[-1].x)
        e.screenshot("verify/scrolled")
        # ---- 4. timer $63 / sub-timer $62: one second = 61 play frames? count ----
        e.run([()] * 200)
        tr = e.last_trace
        secs = [i for i in range(1, len(tr)) if tr[i].timer != tr[i - 1].timer]
        # $F7E4 (DEC $62) runs from the main loop only when $4C bit 6 is clear (no background column waiting)
        gl = [sum(1 for t in tr[a + 1:b + 1] if t.gm and not (t.scroll_flags & 0x40)) for a, b in zip(secs, secs[1:])]
        check("timer_$63_ticks_with_subtimer_$62", len(secs) >= 2 and all(tr[i].subtimer == 60 for i in secs)
              and all(g == 61 for g in gl), frames_between_ticks=[b - a for a, b in zip(secs, secs[1:])],
              main_loop_frames_without_column_wait_between_ticks=gl, timer=tr[-1].timer,
              game_lag_frames_in_window=[t.frame for t in tr if not t.gm])
        e.screenshot("verify/timer")
        # ---- 5. RNG $BF: +1 every frame here ----
        r = [t.rng for t in tr]
        check("rng_$BF_plus1_per_frame", all((b - a) % 256 == 1 for a, b in zip(r, r[1:])), first=r[0], last=r[-1])
        # ---- 6. pause $1E bit 7 (Start), the main loop stops ----
        e.run([("Start",)] + [()] * 20 + [("Start",)] + [()] * 5)
        tr = e.last_trace
        check("pause_$1E_bit7_and_main_loop_skips", (tr[1].pause & 0x80) and tr[1].gm == 1 and tr[1].timer == tr[19].timer
              and tr[-1].pause == 0, pause=[t.pause for t in tr[:3]], timer_frozen=(tr[1].timer, tr[1].subtimer, tr[19].subtimer))
        # ---- 7. the poke death: $8B bit 7 -> death loop (dw), lives $76 -1, respawn ----
        lives = e.state().lives
        e.poke(0x8B, 0x80)
        e.run([()] * 260)
        tr = e.last_trace
        dw = [t.frame for t in tr if t.dw]
        check("death_$8B_lives_$76_deathloop", dw and len(dw) >= 180 and tr[-1].lives == lives - 1,
              death_wait_frames=len(dw), lives=(lives, tr[-1].lives))
    finally:
        e.close()
    ref = STATES_DIR / "ref4751"
    if ref.exists():
        verify_ref(ref)
    (KNOWLEDGE_DIR / "ram_verify.json").write_text(json.dumps(RES, indent=1), encoding="utf-8")


def verify_ref(ref):
    """Experiments on the TAS's real states: HP, boss HP, ninpo, sub-weapon, enemy slots."""
    e = BizHawk(log_name="ram_verify_ref.log")
    try:
        e.tick(TICKS)
        # boss: 2-3 Bomberhead from the stage's control state, the TAS's own inputs are not needed: just watch
        # the boss HP display and the real HP while nothing is pressed (the boss hits Ryu: HP $65 falls)
        st = sorted(ref.glob("04_2-3_control.State"))
        if st:
            e.load("ref4751/04_2-3_control")
            e.trace(True)
            e.run([()] * 300)
            tr = e.last_trace
            hp = [t.hp for t in tr]
            check("hp_$65_falls_when_hit", min(hp) < hp[0], hp_first=hp[0], hp_min=min(hp),
                  first_drop=next((t.frame for t, u in zip(tr, tr[1:]) if u.hp < t.hp), None))
            ids = e.ram(0x400, 8)
            xs = e.ram(0x460, 8)
            ys = e.ram(0x480, 8)
            hps = e.ram(0x490, 8)
            e.screenshot("verify/boss_2-3")
            sp = ryu_sprites(e)
            check("enemy_slots_$0400_id_$0460_x_$0480_y_$0490_hp", any(ids) and hps[7] > 0,
                  ids=list(ids), x=list(xs), y=list(ys), hp=list(hps), boss_display=tr[-1].bosshp,
                  oam_xy=sorted(set((x, y) for x, y, *_ in sp))[:12])
    finally:
        e.close()


if __name__ == "__main__":
    main()
