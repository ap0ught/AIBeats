"""Build the reference run: a published TAS re-fitted to the US ROM on this emulator, stage by stage.

    python tools/build_ref.py <name> <movie.inputs.txt> <S1,...,S8 | chain:M1> [--from K] [--to K] [--K 12] [--W 240]
                              [--scan 3]

Alignment of the movie to each stage's first playable frame L (level routine 4):
  S1,...,S8   (Japanese-ROM movies) the movie frame of the last Start press before each stage (that ROM shows a
              map screen the movie skips with Start).  m = (the movie's first input after S) - 2, because the
              player drops into every stage and the first frame on which a direction has an effect is L+2
              (measured with tools/first_effect.py).  NOTE: this is a guess wherever the movie's first press is
              not on that first frame (found wrong for the bases, see knowledge/reference_run.md).
  chain:M1    (US-ROM movies) stage 1 uses m = M1; afterwards the movie simply continues:
              m_next = m + (movie rows the stage consumed) + (empty frames to the next stage's first frame),
              then the candidates m_next-scan .. m_next+scan are each played plainly for 1500 frames and the one
              that gets furthest is used (the estimate itself unless another is clearly better): the movie was
              made on another emulator whose stage-load lag may differ by a few frames.
logs/<name>/config.json may override: {"m": {"<stage>": m}, "kinds": {"<stage>": [edit kinds]}}.

Per stage: logs/<name>/s<k>.seg.json (edits + rows), states/<name>/s<k>_pre.State (one frame before L).
At the end: logs/<name>/chain.json and logs/<name>.inputs.txt (the whole run from power-on).
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from contra.emulator import LOGS_DIR, STATES_DIR  # noqa: E402
from contra.inputs import read_inputs, write_inputs  # noqa: E402
from contra.resync import F, Pool, edit_cost, play, repair_stage  # noqa: E402


def opt(args, name, default):
    if name in args:
        i = args.index(name)
        v = args[i + 1]
        del args[i:i + 2]
        return type(default)(v)
    return default


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def main():
    args = sys.argv[1:]
    k_from, k_to = opt(args, "--from", 1), opt(args, "--to", 8)
    K, W, H = opt(args, "--K", 12), opt(args, "--W", 240), opt(args, "--H", 900)
    par, scan = opt(args, "--par", 4), opt(args, "--scan", 3)
    name, movie_path, spec = args[0], args[1], args[2]
    chain_mode = spec.startswith("chain:")
    S = [] if chain_mode else [int(x) for x in spec.split(",")]
    movie = read_inputs(movie_path)
    d = LOGS_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    (STATES_DIR / name).mkdir(parents=True, exist_ok=True)
    (STATES_DIR / "tmp" / name).mkdir(parents=True, exist_ok=True)
    cfgp = d / "config.json"
    cfg = json.loads(cfgp.read_text(encoding="utf-8")) if cfgp.exists() else {}
    chainp = d / "chain.json"
    chain = json.loads(chainp.read_text(encoding="utf-8")) if chainp.exists() else {"stages": {}}
    opening = read_inputs(LOGS_DIR / "open_nh.inputs.txt")            # 589 rows -> emulator frame 590
    chain.update({"movie": str(movie_path), "alignment": spec, "opening_rows": len(opening)})
    if "1" not in chain["stages"]:
        chain["stages"]["1"] = {"state": "ref/s1_f590", "L": 591, "R3": 57,
                                "m": int(spec.split(":")[1]) if chain_mode else S[0] + 50}

    def save_chain():
        tmp = chainp.with_name("chain.json.tmp")
        tmp.write_text(json.dumps(chain, indent=1), encoding="utf-8")
        tmp.replace(chainp)

    with Pool(par, name=f"build_{name}") as pool:
        e0 = pool.emus[0]
        for k in range(k_from, k_to + 1):
            st = chain["stages"].get(str(k))
            if not st:
                log(f"stage {k}: no start state (previous stage not finished)")
                break
            m = int(cfg.get("m", {}).get(str(k), st["m"]))
            st["m"] = m
            segp = d / f"s{k}.seg.json"
            seg = json.loads(segp.read_text(encoding="utf-8")) if segp.exists() else None
            if seg and seg.get("done") and seg.get("m") == m:
                rows = [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
                edits = seg["edits"]
                log(f"stage {k}: already fitted, {len(rows)} frames, {len(edits)} edits")
            else:
                prior = seg["edits"] if seg and seg.get("m") == m and not seg.get("done") else None
                log(f"stage {k}: fitting from state {st['state']} (L={st['L']}), movie frame m={m}"
                    + (f", resuming {len(prior)} edits" if prior else ""))
                done, rows, edits = repair_stage(pool, st["state"], movie[m - 1:m - 1 + 7500], f"{name}/s{k}",
                                                 W=W, H=H, K=K, seed=k, edits=prior,
                                                 kinds0=tuple(cfg.get("kinds", {}).get(str(k), ("B+", "B+", "B+", "P", "P", "P"))),
                                                 meta={"m": m, "movie": str(movie_path), "stage": k}, log=log)
                if not done:
                    log(f"stage {k}: NOT finished")
                    save_chain()
                    break
            consumed = len(rows) - sum(edit_cost(tuple(e)) for e in edits)
            st.update({"frames": len(rows), "edits": edits, "movie_rows_consumed": consumed})
            # transition: after the level byte changes, nothing is pressed until the next stage's first frame
            r = play(e0, st["state"], rows, stop_on_death=False, stop_on_level=False, chunk=len(rows) + 1)
            st["level_change_frame"] = r.frame
            st["lag_in_stage"] = r.lag
            e0.save(f"tmp/{name}/end{k}")
            if r.last["groutine"] == 6 or r.last["level"] >= 8:
                st["blanks_after"] = 0
                log(f"stage {k}: GAME COMPLETE at emulator frame {r.frame} (level byte {r.last['level']}, "
                    f"game routine {r.last['groutine']})")
                save_chain()
                break
            e0.set_fields(F)
            e0.trace(True)
            tr = []
            j = None
            while j is None and len(tr) < 1500:
                e0.run([()] * 60)
                tr.extend(e0.last_trace)
                j = next((i + 1 for i, s in enumerate(tr) if s["lroutine"] == 4 and s["level"] == k), None)
            e0.trace(False)
            if j is None:
                log(f"stage {k}: the next stage never started; last {tr[-1]}")
                save_chain()
                break
            R3 = sum(1 for s in tr[:j] if s["lroutine"] == 3)
            L = tr[j - 1]["frame"]
            e0.load(f"tmp/{name}/end{k}")
            if j > 1:
                e0.run([()] * (j - 1))
            nstate = f"{name}/s{k + 1}_pre"
            e0.save(nstate)
            st["blanks_after"] = j - 1
            nxt = {"state": nstate, "L": L, "R3": R3, "weapon_at_start": tr[j - 1]["weapon"]}
            if chain_mode:
                est = m + consumed + (j - 1)
                cands = list(range(est - scan, est + scan + 1))
                res = pool.map(lambda emu, mm: play(emu, nstate, movie[mm - 1:mm - 1 + 1500], stall=900), cands)
                table = {mm: (x.reason, x.frames, x.progress) for mm, x in zip(cands, res)}
                best = max(cands, key=lambda mm: (table[mm][2], table[mm][1], -abs(mm - est)))
                m_next = best if table[best][2] > table[est][2] + 300 else est
                nxt.update({"m": m_next, "m_estimate": est, "m_scan": {str(a): list(b) for a, b in table.items()}})
                log(f"stage {k}: level byte changed at frame {r.frame}; next stage L={L} (R3={R3}); movie frame for L: "
                    f"estimate {est}, scan {table} -> using {m_next}; weapon ${tr[j - 1]['weapon']:02x}")
            elif k < len(S):
                first = next((i for i in range(S[k], S[k] + 400) if movie[i]), None)     # 0-based index after S
                m_next = (first + 1 - 2) if first is not None and first + 1 - S[k] >= 20 else S[k] + 50
                nxt.update({"m": m_next, "movie_first_input_frame": (first + 1) if first is not None else None})
                log(f"stage {k}: level byte changed at frame {r.frame}; next stage's first frame L={L} "
                    f"(R3={R3}); movie frame for L: {m_next}; weapon ${tr[j - 1]['weapon']:02x}")
            if "m" in nxt:
                old = chain["stages"].get(str(k + 1), {})
                if old.get("state") == nstate and old.get("m") == nxt["m"]:
                    old.update(nxt)
                    nxt = old
                chain["stages"][str(k + 1)] = nxt
            save_chain()
        # assemble whatever is finished
        full = list(opening)
        for k in range(1, 9):
            st = chain["stages"].get(str(k))
            segp = d / f"s{k}.seg.json"
            if not st or "frames" not in st or not segp.exists():
                break
            seg = json.loads(segp.read_text(encoding="utf-8"))
            if not seg.get("done"):
                break
            full += [tuple(x for x in r.split("+") if x) for r in seg["rows"]]
            full += [()] * st.get("blanks_after", 0)
            chain["stages_in_inputs"] = k
        chain["total_rows"] = len(full)
        save_chain()
        write_inputs(LOGS_DIR / f"{name}.inputs.txt", full,
                     f"reference run: {Path(movie_path).name} re-fitted to Contra (USA) on NesHawk; stages 1..{chain.get('stages_in_inputs')}")
        log(f"wrote logs/{name}.inputs.txt: {len(full)} rows, stages 1..{chain.get('stages_in_inputs')}")


if __name__ == "__main__":
    main()
