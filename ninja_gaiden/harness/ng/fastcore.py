"""fastcore: Mesen 2.1.1 as a FAST search core for Ninja Gaiden (NES, US). NesHawk stays the judge.

One long-lived headless Mesen process (`Mesen.exe --testrunner <rom> <lua>`: no window, no audio, no video
output) driven over TCP by ng/fastcore.lua. Proven (knowledge/fastcore.md): with the game's controller read forced
clean, Mesen reproduces NesHawk's RAM frame for frame (TAS 4751M, all 39,084 frames, 42 fields, 0 differences when
fed NesHawk's own pad bytes). The one difference between the cores is the DMC-DMA / controller-read conflict: on
NesHawk the game sometimes keeps the previous pad (59 frames in the TAS); Mesen's conflicts fall on other frames,
so fastcore forces a clean read on every frame and NesHawk's conflicts are NOT predicted. Every result found here
must be replayed on NesHawk (open loop) before it counts - `verify_on_neshawk()` does that.

    from ng.fastcore import FastCore, MesenEmu
    with FastCore(boot_rows=rows[:N]) as fc:          # power-on replay: idle at the checkpoint after row N
        fc.save("base")                                # in-process savestate slot
        res = fc.run_batch("base", [cand1, cand2], record="all", stops=[(0x6E, "changed", 0)])
        for r in res: r.rows_played, r.status, r.states[-1].x, r.ram
        fc.save_file("base", "states/mesen/x.mst")     # Mesen savestate file (only Mesen can load it)

    MesenEmu: a BizHawk-like subset (reset/run/step/msave/mload/save/load/ram/ram_all/state/trace) for solvers
    written against ng.emulator.BizHawk.

Frame numbering = NesHawk after reset(): row k is frame k. A Mesen state is always taken at a "checkpoint" (NMI
entry), i.e. between NesHawk frames. Rows/masks: ng.inputs masks (A $80 B $40 Select $20 Start $10 U $08 D $04
L $02 R $01) or button tuples.

CLI:
    python -m ng.fastcore convert <inputs.txt> <frame> <out.mst> [--pads <trace.csv>]   power-on rows -> Mesen state
    python -m ng.fastcore speed                                                          frames/s, savestate timing
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as W
import os
import secrets
import socket
import struct
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from .inputs import from_mask, read_inputs, to_mask

PROJECT = Path(__file__).resolve().parent.parent
ROOT = PROJECT.parent
MESEN_DIR = ROOT / "Mesen2"                    # portable: settings.json next to Mesen.exe keeps everything here
MESEN = MESEN_DIR / "Mesen.exe"
ROM = PROJECT / "Ninja Gaiden (USA).nes"
LUA = Path(__file__).resolve().parent / "fastcore.lua"
RUN_DIR = PROJECT / "emu_tmp" / "mesen"
PIDS = PROJECT / "logs" / "fastcore_pids.txt"
STATES = PROJECT / "states" / "mesen"
CREATE_NO_WINDOW = 0x08000000

OPS = {"==": 0, "eq": 0, "!=": 1, "ne": 1, ">=": 2, "ge": 2, "<=": 3, "le": 3, "changed": 4, "and": 5}


def _fields():
    from .emulator import load_fields
    return dict(load_fields())


def _ticks():
    from .mode import TICKS
    rom = ROM.read_bytes()
    out = []
    for name, v in TICKS.items():
        if isinstance(v, (tuple, list)):
            a, bank = v
            off = 16 + bank * 0x4000 + (a - (0xC000 if bank == 7 else 0x8000))
            out.append((name, a, rom[off:off + 4].hex()))
        else:
            out.append((name, v, None))
    return out


def free_ram_gb() -> float:
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", W.DWORD), ("dwMemoryLoad", W.DWORD), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2 ** 30


def visible_windows(pid: int) -> list[tuple[int, str]]:
    """Visible top-level windows of a process (fastcore must never show one)."""
    u = ctypes.windll.user32
    out = []

    @ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    def cb(h, _):
        p = W.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid and u.IsWindowVisible(h):
            buf = ctypes.create_unicode_buffer(256)
            u.GetWindowTextW(h, buf, 256)
            out.append((h, buf.value))
        return True
    u.EnumWindows(cb, 0)
    return out


def masks_of(rows) -> bytes:
    if isinstance(rows, (bytes, bytearray)):
        return bytes(rows)
    out = bytearray()
    for r in rows:
        out.append(r if isinstance(r, int) else to_mask(r))
    return bytes(out)


class Row(dict):
    """One recorded row (like ng.emulator.State): RAM fields by name, tick counts, lagged, frame."""

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            return 0


@dataclass
class Result:
    rows_played: int
    status: int                 # 0 all rows, 1 stopped by a condition, 2 checkpoint after the last row came late
    states: list = field(default_factory=list)     # Row per recorded row (all rows, or the last one)
    ram: bytes | None = None    # 2 KB after the last row (record_ram=True)
    slot: str | None = None     # end-state slot (keep=True)


class FastCoreError(RuntimeError):
    pass


class FastCore:
    """One headless Mesen process. Not thread-safe; one per worker."""

    def __init__(self, boot_rows=None, fields: dict[str, int] | None = None, ticks: bool = True,
                 log_name: str | None = None, connect_timeout: float = 60.0, min_free_gb: float = 2.5):
        if free_ram_gb() < min_free_gb:
            raise FastCoreError(f"free RAM {free_ram_gb():.1f} GB < {min_free_gb} GB")
        if not (MESEN_DIR / "settings.json").exists():
            # portable mode marker; without it Mesen opens its first-run setup WINDOW
            (MESEN_DIR / "settings.json").write_text("{}", encoding="utf-8")
        self.fields = dict(fields or _fields())
        self.names = list(self.fields)
        self.addrs = [self.fields[k] for k in self.names]
        self.ticks = _ticks() if ticks else []
        self.rec_len = len(self.addrs) + len(self.ticks) + 1
        RUN_DIR.mkdir(parents=True, exist_ok=True)
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv.bind(("127.0.0.1", 0))
        self.srv.listen(1)
        self.port = self.srv.getsockname()[1]
        self.token = secrets.token_hex(8)
        tick_lua = "{" + ",".join(f'{{"{n}",{a},{("[[" + s + "]]") if s else "false"}}}' for n, a, s in self.ticks) + "}"
        self.lua_path = RUN_DIR / f"fc_{os.getpid()}_{self.port}.lua"
        self.lua_path.write_text(f"PORT = {self.port}\nTOKEN = [[{self.token}]]\nTICKS = {tick_lua}\n"
                                 + LUA.read_text(encoding="utf-8"), encoding="utf-8")
        self.log = open(PROJECT / "logs" / log_name, "a", encoding="utf-8") if log_name else None
        cmd = [str(MESEN), "--testrunner", str(ROM), str(self.lua_path),
               "--debug.scriptWindow.allowIoOsAccess=true", "--debug.scriptWindow.allowNetworkAccess=true",
               "--debug.scriptWindow.scriptTimeout=1000000", "--nes.allowInvalidInput=true",
               "--timeout=8640000"]
        self.proc = subprocess.Popen(cmd, cwd=str(MESEN_DIR), creationflags=CREATE_NO_WINDOW,
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        PIDS.parent.mkdir(parents=True, exist_ok=True)
        with open(PIDS, "a", encoding="utf-8") as f:
            f.write(f"{self.proc.pid} {time.strftime('%Y-%m-%d %H:%M:%S')} owner={os.getpid()}\n")
        self.srv.settimeout(connect_timeout)
        try:
            self.sock, _ = self.srv.accept()
        except socket.timeout:
            self.proc.kill()
            raise FastCoreError("Mesen did not connect")
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(None)
        self.rf = self.sock.makefile("rb")
        hello = self.rf.readline().decode().split()
        if hello != ["HELLO", self.token]:
            raise FastCoreError(f"bad hello {hello}")
        b = masks_of(boot_rows or [])
        self.sock.sendall(f"BOOT {len(b)}\n".encode() + b)
        self.frame = None                      # NesHawk frame number of the current checkpoint, when known
        if b:
            parts = self._line().split()       # OK BOOT <frames> <late>
            if parts[3] != "0":
                raise FastCoreError(f"boot: the checkpoint after row {len(b)} came late (NMI off): {parts}")
            self.frame = len(b)
        self._send(f"ADDRS {len(self.addrs)}", struct.pack(f"<{len(self.addrs)}H", *self.addrs))
        self._ok()
        w = visible_windows(self.proc.pid)
        if w:
            self._log(f"WARNING Mesen pid {self.proc.pid} shows windows {w}")

    # -- plumbing ------------------------------------------------------------------------------------------
    def _log(self, s):
        if self.log:
            self.log.write(time.strftime("%H:%M:%S ") + s + "\n")
            self.log.flush()

    def _send(self, line: str, payload: bytes = b""):
        self.sock.sendall(line.encode() + b"\n" + payload)

    def _line(self) -> str:
        l = self.rf.readline()
        if not l:
            raise FastCoreError(f"Mesen closed the connection (exit {self.proc.poll()})")
        return l.decode().rstrip("\n")

    def _ok(self) -> list[str]:
        l = self._line()
        if not l.startswith("OK"):
            raise FastCoreError(l)
        return l.split()[1:]

    def _ok_payload(self) -> tuple[list[str], bytes]:
        p = self._ok()
        n = int(p[-1])
        return p[:-1], self.rf.read(n) if n else b""

    def _rows(self, data: bytes, first_frame: int | None) -> list[Row]:
        out = []
        L = self.rec_len
        nt = len(self.ticks)
        for i in range(0, len(data), L):
            b = data[i:i + L]
            r = Row(zip(self.names, b))
            for j, (name, _, _) in enumerate(self.ticks):
                r[name] = b[len(self.addrs) + j]
            r["lagged"] = b[-1]
            out.append(r)
        return out

    # -- savestates ----------------------------------------------------------------------------------------
    def save(self, slot: str) -> int:
        """Savestate of the current checkpoint into an in-process slot; returns its size."""
        self._send(f"SAVE {slot}")
        return int(self._ok()[0])

    def load(self, slot: str) -> None:
        self._send(f"LOAD {slot}")
        self._ok()
        self.frame = None

    def get(self, slot: str) -> bytes:
        self._send(f"GET {slot}")
        return self._ok_payload()[1]

    def put(self, slot: str, data: bytes) -> None:
        self._send(f"PUT {slot} {len(data)}", data)
        self._ok()

    def drop(self, *slots: str) -> None:
        self._send("DROP " + " ".join(slots))
        self._ok()

    def drop_prefix(self, prefix: str) -> None:
        self._send(f"DROPPREFIX {prefix}")
        self._ok()

    def save_file(self, slot: str, path: str | Path, frame: int | None = None) -> Path:
        """Write a slot to a file (<path>; a sidecar <path>.frame holds the NesHawk frame if known)."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.get(slot)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, path)
        if frame is not None:
            path.with_name(path.name + ".frame").write_text(str(frame))
        return path

    def load_file(self, path: str | Path, slot: str = "base") -> int | None:
        """Put a state file into a slot and load it; returns its NesHawk frame if the sidecar has it."""
        path = Path(path)
        self.put(slot, path.read_bytes())
        self.load(slot)
        fr = path.with_name(path.name + ".frame")
        self.frame = int(fr.read_text()) if fr.exists() else None
        return self.frame

    # -- RAM -----------------------------------------------------------------------------------------------
    def ram(self) -> bytes:
        self._send("RAM")
        return self._ok_payload()[1]

    def poke(self, addr: int, val: int) -> None:
        """DEBUG ONLY."""
        self._send(f"POKE {addr} {val & 0xFF}")
        self._ok()

    def info(self) -> dict:
        self._send("INFO")
        return dict(t.split("=") for t in self._ok())

    # -- playing -------------------------------------------------------------------------------------------
    def step(self, rows, record: str = "last") -> tuple[int, list[Row], int]:
        """Play rows from the CURRENT checkpoint; stays at the checkpoint after the last row.
        record: 'last' or 'all'. Returns (rows played, rows recorded, status 0 / 2 = late checkpoint)."""
        m = masks_of(rows)
        self._send(f"STEP {len(m)} {4 if record == 'all' else 0}", m)
        p, data = self._ok_payload()
        played, status = int(p[0]), int(p[1])
        recs = self._rows(data, None)
        if self.frame is not None:
            self.frame += played
            if status == 2:
                self.frame = None
        for i, r in enumerate(recs):
            r["frame"] = (self.frame - (len(recs) - 1 - i)) if self.frame is not None else 0
        return played, recs, status

    def run_batch(self, slot: str, cands: Sequence, record: str = "last", stops: Sequence = (),
                  record_ram: bool = False, keep: bool = False, prefix: str = "k",
                  start_frame: int | None = None) -> list[Result]:
        """Play every candidate from the state in `slot` (each one starts from that state).
        stops: [(addr, op, value)] op in == != >= <= changed and -> stop after the row where it holds.
        keep: keep each candidate's end state in slot f"{prefix}{i+1}" (drop them with drop_prefix).
        After the call the emulator sits at the last candidate's end checkpoint."""
        body = bytearray(struct.pack("<HBH", len(cands), (1 if record_ram else 0) | (2 if keep else 0)
                                     | (4 if record == "all" else 0), len(stops)))
        for a, op, v in stops:
            body += struct.pack("<HBB", a, OPS[op], v & 0xFF)
        for c in cands:
            m = masks_of(c)
            body += struct.pack("<H", len(m)) + m
        self._send(f"RUN {slot} {prefix} {len(body)}", bytes(body))
        _, data = self._ok_payload()
        out = []
        pos = 0
        for i in range(len(cands)):
            played, status = struct.unpack_from("<HB", data, pos)
            pos += 3
            n = (played if record == "all" else (1 if played else 0)) * self.rec_len
            recs = self._rows(data[pos:pos + n], None)
            pos += n
            ram = None
            if record_ram and played:
                ram = data[pos:pos + 2048]
                pos += 2048
            if start_frame is not None:
                for j, r in enumerate(recs):
                    r["frame"] = start_frame + (j + 1 if record == "all" else played)
            out.append(Result(played, status, recs, ram, f"{prefix}{i + 1}" if keep and played else None))
        self.frame = None
        return out

    def close(self) -> None:
        try:
            self._send("QUIT")
            self._line()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=10)
        except Exception:
            self.proc.kill()
        for s in (getattr(self, "sock", None), self.srv):
            try:
                s.close()
            except Exception:
                pass
        try:
            self.lua_path.unlink()
        except Exception:
            pass
        if self.log:
            self.log.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class FastPool:
    """n FastCore processes (default 2 = this project's per-agent cap) working on one candidate list in parallel.
    Every worker boots the same rows; put_all() copies a state into every worker's slot. While logs/HOLD_FARMS
    exists only 1 worker is started."""

    def __init__(self, n: int = 2, boot_rows=None, **kw):
        if (PROJECT / "logs" / "HOLD_FARMS").exists():
            n = 1
        self.workers = [FastCore(boot_rows=boot_rows, **kw) for _ in range(n)]

    def save_all(self, slot: str) -> None:
        for w in self.workers:
            w.save(slot)

    def put_all(self, slot: str, data: bytes) -> None:
        for w in self.workers:
            w.put(slot, data)

    def run_batch(self, slot: str, cands: Sequence, **kw) -> list[Result]:
        import threading
        n = len(self.workers)
        parts = [list(range(i, len(cands), n)) for i in range(n)]
        out: list = [None] * len(cands)
        errs = []

        def work(wi, w, idx):
            try:
                res = w.run_batch(slot, [cands[i] for i in idx], **kw)
                for i, r in zip(idx, res):
                    r.worker = wi           # keep=True: r.slot lives in self.workers[r.worker]
                    out[i] = r
            except Exception as e:      # noqa: BLE001
                errs.append(e)
        th = [threading.Thread(target=work, args=(wi, w, idx)) for wi, (w, idx) in enumerate(zip(self.workers, parts))
              if idx]
        for t in th:
            t.start()
        for t in th:
            t.join()
        if errs:
            raise errs[0]
        return out

    def close(self) -> None:
        for w in self.workers:
            w.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class MesenEmu:
    """A small BizHawk-compatible face over FastCore (run/step/msave/mload/save/load/ram/state/trace), so code
    written against ng.emulator.BizHawk can search on Mesen. Frame numbers are NesHawk's when the state's frame is
    known (power-on replay, or a state file with a .frame sidecar). Not supported: reset() mid-session (Mesen's
    Lua has no power cycle: start a new MesenEmu), watch/tick changes, screenshots, run_comp."""

    def __init__(self, boot_rows=None, **kw):
        self.fc = FastCore(boot_rows=boot_rows, **kw)
        self.inputs: list = list(boot_rows or [])
        self._trace = False
        self.last_trace: list[Row] = []
        self._n = 0
        self._last = Row(frame=self.fc.frame or 0)

    def trace(self, on: bool) -> None:
        self._trace = on

    def run(self, rows, chunk: int = 0) -> Row:
        rows = [tuple(r) if not isinstance(r, int) else from_mask(r) for r in rows]
        if not rows:
            return self._last
        self.inputs.extend(rows)
        _, recs, _ = self.fc.step(rows, record="all" if self._trace else "last")
        self.last_trace = recs if self._trace else []
        self._last = recs[-1]
        return self._last

    def step(self, buttons: Iterable[str] | str = (), frames: int = 1) -> Row:
        if isinstance(buttons, str):
            buttons = tuple(b for b in buttons.replace("+", ",").split(",") if b)
        return self.run([tuple(buttons)] * frames)

    def run_ram(self, rows):
        states, rams = [], []
        for r in rows:
            states.append(self.run([r]))
            rams.append(self.fc.ram())
        return states, rams

    def state(self) -> Row:
        return self._last

    def msave(self) -> str:
        self._n += 1
        sid = f"m{self._n}"
        self.fc.save(sid)
        self._frames = getattr(self, "_frames", {})
        self._frames[sid] = (self.fc.frame, self._last, len(self.inputs))
        return sid

    def mload(self, sid: str) -> Row:
        self.fc.load(sid)
        fr, last, n = self._frames[sid]
        self.fc.frame = fr
        self._last = last
        del self.inputs[n:]
        return self._last

    def mfree(self, sid: str) -> None:
        self.fc.drop(sid)
        getattr(self, "_frames", {}).pop(sid, None)

    def save(self, name: str) -> Path:
        self.fc.save("_file")
        return self.fc.save_file("_file", STATES / f"{name}.mst", self.fc.frame)

    def load(self, name: str) -> Row:
        p = Path(name) if str(name).endswith(".mst") else STATES / f"{name}.mst"
        fr = self.fc.load_file(p, "_file")
        ram = self.fc.ram()
        self._last = Row({k: ram[a] for k, a in self.fc.fields.items() if a < 0x800}, frame=fr or 0)
        self.inputs = []
        return self._last

    def ram(self, addr: int, length: int = 1) -> bytes:
        return self.fc.ram()[addr:addr + length]

    def ram_all(self) -> bytes:
        return self.fc.ram()

    def byte(self, addr: int) -> int:
        return self.fc.ram()[addr]

    def close(self):
        self.fc.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# -- converters / verification ------------------------------------------------------------------------------------
def neshawk_pads(trace_csv: str | Path, n: int) -> bytes:
    """The pad byte the game really used on NesHawk, frames 1..n, from a harness trace CSV (column 'pad')."""
    import csv
    pads = {}
    with open(trace_csv, newline="") as f:
        for r in csv.DictReader(f):
            pads[int(r["row"])] = int(r["pad"])
    return bytes(pads.get(k, 0) for k in range(1, n + 1))


def apply_conflicts(rows, conflicts: Iterable[int], first_frame: int, prev_pad: int = 0) -> bytes:
    """NesHawk's view of `rows` (frame of rows[0] = first_frame): on each conflict frame the game keeps the
    previous pad. Feeding the result to fastcore reproduces NesHawk exactly (proven: fc_validate step 3)."""
    m = bytearray(masks_of(rows))
    for fr in sorted(conflicts):
        k = fr - first_frame
        if 0 <= k < len(m):
            m[k] = m[k - 1] if k > 0 else prev_pad
    return bytes(m)


def convert(rows, frame: int, out: str | Path, pads: bytes | None = None) -> Path:
    """Reproduce the NesHawk situation 'power-on rows 1..frame' in Mesen and save a Mesen state file.
    pads: NesHawk's effective pad bytes (neshawk_pads) when NesHawk had DMC conflicts in that history; without
    them the rows are fed as clean reads (equal to NesHawk whenever no conflict hit a changing input)."""
    boot = pads[:frame] if pads is not None else masks_of(list(rows)[:frame])
    with FastCore(boot_rows=boot, ticks=False) as fc:
        fc.save("conv")
        return fc.save_file("conv", out, frame)


def verify_on_neshawk(history_rows, new_rows, mesen_trace: Sequence[Row] | None = None,
                      fields: Sequence[str] = ("x", "y", "stage", "room", "hp", "timer", "rng", "bosshp", "pad")):
    """Open-loop NesHawk replay of history + new rows from power-on (reset()); compares per-frame fields of the
    new rows with a Mesen trace (if given). Returns (first differing frame or None, NesHawk trace of the new rows,
    list of NesHawk pad-conflict frames inside the new rows)."""
    from .emulator import BizHawk
    hist = [tuple(r) if not isinstance(r, int) else from_mask(r) for r in history_rows]
    new = [tuple(r) if not isinstance(r, int) else from_mask(r) for r in new_rows]
    with BizHawk(log_name="fastcore_verify_emu.log") as e:
        e.reset()
        if hist:
            e.run(hist)
        e.trace(True)
        e.run(new)
        tr = e.last_trace
    first = None
    conflicts = []
    prev = None
    for i, s in enumerate(tr):
        want = to_mask(new[i])
        if s.get("lagged", 0) == 0 and s["pad"] != want:
            conflicts.append(s["frame"])
        if mesen_trace is not None and first is None:
            m = mesen_trace[i]
            if any(m.get(k) != s.get(k) for k in fields):
                first = s["frame"]
    return first, tr, conflicts


def _speed():
    rows = read_inputs(PROJECT / "logs" / "tas4751.inputs.txt")
    t = time.time()
    with FastCore(boot_rows=rows[:174], ticks=False) as fc:
        t_boot = time.time() - t
        fc.save("a")
        n = 3000
        t = time.time()
        fc.step(rows[174:174 + n])
        dt = time.time() - t
        print(f"boot 174 frames + start {t_boot:.2f}s; step {n} frames {dt:.2f}s = {n / dt:.0f} f/s (no ticks)")
        t = time.time()
        for i in range(200):
            fc.save("b")
        ts = (time.time() - t) / 200
        t = time.time()
        for i in range(200):
            fc.load("a")
        tl = (time.time() - t) / 200
        print(f"savestate {len(fc.get('a'))} bytes; save {ts * 1000:.2f} ms, load {tl * 1000:.2f} ms (incl. TCP)")
        cands = [rows[174:174 + 60]] * 50
        t = time.time()
        fc.run_batch("a", cands, record="all")
        dt = time.time() - t
        print(f"batch 50 x 60 rows record=all: {dt:.2f}s = {50 * 60 / dt:.0f} f/s incl. 50 loads")
    with FastCore(boot_rows=rows[:174], ticks=True) as fc:
        fc.save("a")
        t = time.time()
        fc.step(rows[174:174 + 3000], record="all")
        dt = time.time() - t
        print(f"with ticks + record every row: {3000 / dt:.0f} f/s")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("convert")
    c.add_argument("inputs")
    c.add_argument("frame", type=int)
    c.add_argument("out")
    c.add_argument("--pads", help="NesHawk trace CSV with the game's pad byte per frame")
    sub.add_parser("speed")
    a = ap.parse_args()
    if a.cmd == "convert":
        rows = read_inputs(a.inputs)
        pads = neshawk_pads(a.pads, a.frame) if a.pads else None
        print(convert(rows, a.frame, a.out, pads))
    elif a.cmd == "speed":
        _speed()
    else:
        ap.print_help()
