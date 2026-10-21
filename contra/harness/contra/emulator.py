"""Python side of the BizHawk bridge for Contra (NES, US). Launches EmuHawk with bridge.lua and drives it over TCP.

Adapted from toads/toads/emulator.py (nothing is imported from there). Same launch method: a private copy of
BizHawk's config per instance with rewind off, the Lua bridge given on the command line, the port in --userdata.
The helper harness/tools/hide_emus.py (already running) hides the windows.

    CONTRA_CORE=NesHawk|quickerNES   which NES core this instance loads (default: NesHawk, see DEFAULT_CORE)
    CONTRA_CONNECT_TIMEOUT=seconds   how long to wait for EmuHawk to connect (default 240)

RAM fields reported with every state line come from knowledge/ram.json ("fields" section).
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import uuid
from pathlib import Path
from typing import Iterable, Sequence

from .inputs import BUTTONS, to_hex, write_inputs

PROJECT = Path(__file__).resolve().parent.parent          # 
ROOT = PROJECT.parent
BIZHAWK_DIR = ROOT / "BizHawk-2.11.1-win-x64"
EMUHAWK = BIZHAWK_DIR / "EmuHawk.exe"
ROM = PROJECT / "Contra (USA).nes"
ROM_CRC32 = "C50A8304"
BRIDGE_LUA = PROJECT / "bridge.lua"
STATES_DIR = PROJECT / "states"
SHOTS_DIR = PROJECT / "shots"
LOGS_DIR = PROJECT / "logs"
VIDEO_DIR = PROJECT / "video"
KNOWLEDGE_DIR = PROJECT / "knowledge"

DEFAULT_CORE = "NesHawk"          # the accurate core; quickerNES is ~3x faster (see README_HARNESS.md)

FIELDS: dict[str, int] = {}


def load_fields() -> dict[str, int]:
    """name -> address from knowledge/ram.json. Accepts either a flat {name: addr} map or {"fields": {...}}."""
    p = KNOWLEDGE_DIR / "ram.json"
    if p.exists():
        j = json.loads(p.read_text(encoding="utf-8"))
        j = j.get("fields", j)
        FIELDS.clear()
        for k, v in j.items():
            if isinstance(v, dict):
                v = v.get("addr")
            if v is None:
                continue
            FIELDS[k] = int(v, 0) if isinstance(v, str) else int(v)
    return FIELDS


def _click_really_quit(proc, timeout: float = 8.0) -> bool:
    """EmuHawk asks 'Really quit?' when it exits while recording A/V. Find THIS process's dialog (by pid, so
    parallel sessions do not click each other's) and press Yes, repeatedly, until the process is gone."""
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        BM_CLICK = 0x00F5
        EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        pid = proc.pid
        clicked = False
        t0 = time.time()
        while time.time() - t0 < timeout:
            if proc.poll() is not None:
                return clicked
            dialogs = []

            def top(h, _):
                buf = ctypes.create_unicode_buffer(64)
                u.GetWindowTextW(h, buf, 64)
                if buf.value == "Really quit?":
                    owner = wintypes.DWORD()
                    u.GetWindowThreadProcessId(h, ctypes.byref(owner))
                    if owner.value == pid:
                        dialogs.append(h)
                return True
            u.EnumWindows(EnumProc(top), 0)
            for dlg in dialogs:
                found = []

                def cb(h, _):
                    buf = ctypes.create_unicode_buffer(64)
                    u.GetWindowTextW(h, buf, 64)
                    if "yes" in buf.value.replace("&", "").lower():
                        found.append(h)
                    return True
                u.EnumChildWindows(dlg, EnumProc(cb), 0)
                if found:
                    u.PostMessageW(found[0], BM_CLICK, 0, 0)
                    clicked = True
            time.sleep(0.05)
    except Exception:
        pass
    return False


class State(dict):
    """One frame's reported RAM fields. Attribute access for convenience: s.frame, s.x, ... (0 if unknown)."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            return 0

    @classmethod
    def parse(cls, line: str) -> "State":
        s = cls()
        for tok in line.split():
            k, _, v = tok.partition("=")
            s[k] = int(v)
        return s

    def __str__(self) -> str:
        return " ".join(f"{k}={v}" for k, v in self.items())


class BizHawk:
    """One EmuHawk instance driven frame by frame."""

    def __init__(self, rom: Path = ROM, fast: bool = True, log_name: str | None = None, record: str | None = None,
                 fields: dict[str, int] | None = None, movie: str | Path | None = None, core: str | None = None):
        """record=<session name>: dump A/V live and keep every frame's input and state in memory.
        movie=<.bk2 path>: play a BizHawk movie (research only); use step_movie().
        core=: NES core for this instance (overrides CONTRA_CORE)."""
        for d in (STATES_DIR, SHOTS_DIR, LOGS_DIR, KNOWLEDGE_DIR):
            d.mkdir(parents=True, exist_ok=True)
        self.record = record
        self.trace_lines: list[str] = []
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        (PROJECT / ".bridge_port").write_text(str(port))
        log_name = log_name or f"emuhawk_{int(time.time())}.log"
        log_path = LOGS_DIR / log_name
        try:
            if log_path.exists() and log_path.stat().st_size > 0:
                log_path.replace(log_path.with_name(log_path.stem + ".prev" + log_path.suffix))
        except OSError:
            pass
        self._logfile = open(log_path, "w")
        # private config per instance with rewind off: the 512 MB rewind buffer makes every EmuHawk ~800 MB
        self.private_dir = PROJECT / "emu_tmp" / f"{os.getpid()}_{uuid.uuid4().hex[:8]}"
        self.private_dir.mkdir(parents=True, exist_ok=True)
        conf = json.loads((BIZHAWK_DIR / "config.ini").read_text(encoding="utf-8-sig"))
        if "Rewind" in conf:
            conf["Rewind"]["Enabled"] = False
        self.core = core or os.environ.get("CONTRA_CORE") or DEFAULT_CORE
        conf["PreferredCores"]["NES"] = self.core
        cfg = self.private_dir / "config.ini"
        cfg.write_text(json.dumps(conf, indent=1), encoding="utf-8")
        args = [str(EMUHAWK), f"--config={cfg}", f"--lua={BRIDGE_LUA}", f"--userdata=port:{port}"]
        if record:
            VIDEO_DIR.mkdir(parents=True, exist_ok=True)
            self.video_path = VIDEO_DIR / f"{record}.mkv"
            args += ["--dump-type=ffmpeg", f"--dump-name={self.video_path}"]
        if movie:
            args.append(f"--movie={movie}")
        args.append(str(rom))
        self.proc = subprocess.Popen(args, cwd=str(BIZHAWK_DIR), stdout=self._logfile, stderr=subprocess.STDOUT)
        self.pid = self.proc.pid
        srv.settimeout(float(os.environ.get("CONTRA_CONNECT_TIMEOUT", 240)))
        try:
            self.conn, _ = srv.accept()
        except socket.timeout:
            self.proc.kill()
            raise RuntimeError("EmuHawk never connected to the bridge; see " + str(log_path))
        finally:
            srv.close()
        self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.conn.settimeout(300)
        self._rf = self.conn.makefile("rb")
        self.inputs: list[tuple[str, ...]] = []   # one entry per emulated frame since power-on
        self.events: list[tuple[int, str]] = []   # (frame, text) notes, for overlays
        self.input_log_valid = True                 # False once a savestate load breaks the frame chain
        assert self.cmd("ping") == "pong"
        self.info = self.coreinfo()
        if self.info["core_seen"].lower() != self.core.lower():
            self.close()
            raise RuntimeError(f"wrong NES core loaded: wanted {self.core}, memory domains say {self.info['core_seen']}")
        self.set_fields(fields if fields is not None else (FIELDS or load_fields()))
        if record:
            self.cmd("trace on")
        if fast:
            self.fast()

    # -- low level -------------------------------------------------------
    def cmd(self, line: str) -> str:
        self.conn.sendall((line + "\n").encode())
        resp = self._rf.readline()
        if not resp:
            code = None
            try:
                code = self.proc.wait(timeout=2)
            except Exception:
                pass
            how = "still running" if code is None else f"exit code {code} (0x{code & 0xFFFFFFFF:08X})"
            raise RuntimeError(f"bridge connection lost at {time.strftime('%H:%M:%S')}: EmuHawk {how}; "
                               f"log {getattr(self._logfile, 'name', '?')}")
        resp = resp.decode().rstrip("\n")
        if resp.startswith("err "):
            raise RuntimeError(resp)
        return resp

    def coreinfo(self) -> dict:
        d = {}
        for part in self.cmd("coreinfo").split(";"):
            k, _, v = part.partition("=")
            d[k] = v
        d["domains"] = d.get("domains", "").split("|")
        # NesHawk exposes the PPU's address space as a memory domain; quickerNES does not
        d["core_seen"] = "NesHawk" if "PPU Bus" in d["domains"] else "quickerNES"
        return d

    def set_fields(self, fields: dict[str, int]) -> None:
        """Tell the bridge which RAM bytes to report with every state line."""
        self.fields = dict(fields)
        spec = ",".join(f"{k}:{v}" for k, v in fields.items())
        self.cmd(f"fields {spec}")

    def trace(self, on: bool) -> None:
        self._trace = on
        self.cmd("trace on" if on else "trace off")

    # -- control ---------------------------------------------------------
    def step(self, buttons: Iterable[str] | str = (), frames: int = 1) -> State:
        if isinstance(buttons, str):
            buttons = tuple(b for b in buttons.replace("+", ",").split(",") if b)
        btn = tuple(buttons)
        for b in btn:
            if b not in BUTTONS:
                raise ValueError(f"unknown button {b!r}")
        self.inputs.extend([btn] * frames)
        resp = self.cmd(f"step {frames} {','.join(btn) or '-'}")
        if self.record or getattr(self, "_trace", False):
            lines = resp.split(";")
            if self.record:
                self.trace_lines.extend(lines)
            self.last_trace = [State.parse(l) for l in lines]
            return self.last_trace[-1]
        return State.parse(resp)

    def run(self, rows: Sequence[Iterable[str]], chunk: int = 2000) -> State:
        """Play a list of per-frame inputs (one bridge round trip per `chunk` frames). With trace on, returns the
        last state and leaves every frame's state in self.last_trace."""
        rows = [tuple(r) for r in rows]
        s = None
        tr = []
        for i in range(0, len(rows), chunk):
            part = rows[i:i + chunk]
            self.inputs.extend(part)
            resp = self.cmd("stepx " + to_hex(part))
            if self.record or getattr(self, "_trace", False):
                lines = resp.split(";")
                if self.record:
                    self.trace_lines.extend(lines)
                tr.extend(State.parse(l) for l in lines)
                s = tr[-1]
            else:
                s = State.parse(resp)
        self.last_trace = tr
        return s if s is not None else self.state()

    def run_comp(self, rows: Sequence[Iterable[str]], chunk: int = 2000, pad_addr: int = 0xF1, carry: int = 0):
        """Like run(), with lost-press compensation (bridge command stepc): a button that was sent but that the
        game's own controller byte does not show after the frame (NesHawk's DMC/controller conflict made the game
        reuse the previous frame's read) is pressed again on the next frame. Returns (last state, rows really
        sent, carry mask left over). self.inputs gets the rows really sent, so the log replays open-loop."""
        from .inputs import from_mask
        rows = [tuple(r) for r in rows]
        s = None
        tr = []
        sent_all = []
        for i in range(0, len(rows), chunk):
            part = rows[i:i + chunk]
            resp = self.cmd(f"stepc {pad_addr} {carry} " + to_hex(part))
            hx, c, rest = resp.split("|", 2)
            carry = int(c)
            sent = [from_mask(int(hx[k:k + 2], 16)) for k in range(0, len(hx), 2)]
            sent_all.extend(sent)
            self.inputs.extend(sent)
            if self.record or getattr(self, "_trace", False):
                lines = rest.split(";")
                if self.record:
                    self.trace_lines.extend(lines)
                tr.extend(State.parse(l) for l in lines)
                s = tr[-1]
            else:
                s = State.parse(rest)
        self.last_trace = tr
        return (s if s is not None else self.state()), sent_all, carry

    def press(self, *buttons: str, hold: int = 1, release: int = 1) -> State:
        s = self.step(buttons, hold)
        if release:
            s = self.step((), release)
        return s

    def state(self) -> State:
        return State.parse(self.cmd("state"))

    def ram(self, addr: int, length: int = 1) -> bytes:
        return bytes.fromhex(self.cmd(f"ram {addr} {length}"))

    def ram_all(self) -> bytes:
        """The whole 2 KB of console RAM."""
        return self.ram(0, 0x800)

    def byte(self, addr: int) -> int:
        return self.ram(addr, 1)[0]

    def ram_domain(self, domain: str, addr: int, length: int) -> bytes:
        return bytes.fromhex(self.cmd(f"ramd {domain.replace(' ', '_')} {addr} {length}"))

    def oam(self) -> bytes:
        """The PPU's 256 bytes of sprite memory: what the PPU drew sprites from on the frame just emulated
        (the game copies its buffer at $0200 there in NMI, at the START of a frame)."""
        return self.ram_domain("OAM", 0, 256)

    def save(self, name: str) -> Path:
        p = STATES_DIR / f"{name}.State"
        p.parent.mkdir(parents=True, exist_ok=True)
        self.cmd(f"save {p}")
        return p

    def load(self, name: str) -> State:
        p = STATES_DIR / f"{name}.State"
        r = self.cmd(f"load {p}")
        if r != "ok":
            raise RuntimeError(f"savestate load failed: {p}")
        self.input_log_valid = False
        return self.state()

    def poke(self, addr: int, val: int) -> None:
        """DEBUG ONLY: write one RAM byte. For mechanics experiments on snapshots; a run never calls this."""
        self.cmd(f"poke {addr} {val & 0xFF}")

    def step_movie(self, frames: int = 1) -> None:
        """Advance frames while a movie plays, without setting any input (see movie= in __init__)."""
        raise NotImplementedError("movie playback goes through verify_bk2.py (hands-off, no bridge)")

    def msave(self) -> str:
        return self.cmd("msave")

    def mload(self, sid: str) -> State:
        self.cmd(f"mload {sid}")
        self.input_log_valid = False
        return self.state()

    def mfree(self, sid: str) -> None:
        self.cmd(f"mfree {sid}")

    def screenshot(self, name: str) -> Path:
        p = SHOTS_DIR / f"{name}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        self.cmd(f"screenshot {p}")
        return p

    def fast(self) -> None:
        self.cmd("fast")

    def normal(self) -> None:
        self.cmd("normal")

    def frameskip(self, n: int) -> None:
        self.cmd(f"frameskip {n}")

    def reset(self) -> State:
        self.inputs.clear()
        self.input_log_valid = True
        return State.parse(self.cmd("reset"))

    def wait(self, frames: int) -> State:
        return self.step((), frames)

    def note(self, text: str) -> None:
        """Record what the bot is doing right now (attached to the next frame)."""
        self.events.append((len(self.inputs) + 1, text))

    def save_inputs(self, name: str) -> Path:
        p = write_inputs(LOGS_DIR / f"{name}.inputs.txt", self.inputs,
                         f"valid_from_poweron={self.input_log_valid} core={self.core}")
        with open(LOGS_DIR / f"{name}.events.txt", "w", encoding="utf-8") as f:
            for frame, text in self.events:
                f.write(f"{frame}\t{text}\n")
        return p

    def save_session(self) -> None:
        """Write logs/<record>.{inputs,events,trace}.txt indexed by video frame (frames stepped since launch)."""
        name = self.record
        write_inputs(LOGS_DIR / f"{name}.inputs.txt", self.inputs, "session=1")
        with open(LOGS_DIR / f"{name}.events.txt", "w", encoding="utf-8") as f:
            for frame, text in self.events:
                f.write(f"{frame}\t{text}\n")
        with open(LOGS_DIR / f"{name}.trace.txt", "w", encoding="utf-8") as f:
            for i, (btn, line) in enumerate(zip(self.inputs, self.trace_lines)):
                f.write(f"{i + 1}\t{'+'.join(btn)}\t{line}\n")

    def close(self) -> None:
        if self.record:
            try:
                self.save_session()
            except Exception as e:
                print("session save failed:", e)
        try:
            self.cmd("quit")
        except Exception:
            pass
        try:
            self.conn.close()
        except Exception:
            pass
        if self.record:
            _click_really_quit(self.proc)
        try:
            self.proc.wait(timeout=12 if self.record else 5)
        except Exception:
            self.proc.kill()                      # our own child, by handle (never by name)
            try:
                self.proc.wait(timeout=5)
            except Exception:
                pass
        try:
            self._logfile.close()
        except Exception:
            pass
        shutil.rmtree(self.private_dir, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
