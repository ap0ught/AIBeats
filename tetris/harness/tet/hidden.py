"""Launch processes on a separate, never-shown Windows desktop ("AIPlaysHidden"), so emulator windows can never
appear on any of the owner's screens or take focus (owner request 2026-11-05: emulator windows must never come
up on his primary screen, hidden if possible).

A desktop made with CreateDesktopW in the interactive window station is never switched to, so nothing on it is
visible or focusable. Rendering into the emulator's own frame buffer, Lua, sockets and screenshots work as normal.

    proc = launch([exe, args...], cwd, stdout_path)   -> HiddenProc with .pid .poll() .wait(timeout) .kill()
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import subprocess
import time

DESKTOP_NAME = "AIPlaysHidden"
GENERIC_ALL = 0x10000000
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_UNICODE_ENVIRONMENT = 0x00000400
STARTF_USESHOWWINDOW = 0x00000001
STARTF_USESTDHANDLES = 0x00000100
SW_HIDE = 0
INFINITE = 0xFFFFFFFF
WAIT_TIMEOUT = 0x102
STILL_ACTIVE = 259
HANDLE_FLAG_INHERIT = 1

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
u32 = ctypes.WinDLL("user32", use_last_error=True)


class STARTUPINFOW(ctypes.Structure):
    _fields_ = [("cb", wt.DWORD), ("lpReserved", wt.LPWSTR), ("lpDesktop", wt.LPWSTR), ("lpTitle", wt.LPWSTR),
                ("dwX", wt.DWORD), ("dwY", wt.DWORD), ("dwXSize", wt.DWORD), ("dwYSize", wt.DWORD),
                ("dwXCountChars", wt.DWORD), ("dwYCountChars", wt.DWORD), ("dwFillAttribute", wt.DWORD),
                ("dwFlags", wt.DWORD), ("wShowWindow", wt.WORD), ("cbReserved2", wt.WORD),
                ("lpReserved2", ctypes.c_void_p), ("hStdInput", wt.HANDLE), ("hStdOutput", wt.HANDLE),
                ("hStdError", wt.HANDLE)]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [("hProcess", wt.HANDLE), ("hThread", wt.HANDLE), ("dwProcessId", wt.DWORD),
                ("dwThreadId", wt.DWORD)]


u32.CreateDesktopW.restype = wt.HANDLE
u32.CreateDesktopW.argtypes = [wt.LPCWSTR, wt.LPCWSTR, ctypes.c_void_p, wt.DWORD, wt.DWORD, ctypes.c_void_p]
k32.CreateProcessW.argtypes = [wt.LPCWSTR, wt.LPWSTR, ctypes.c_void_p, ctypes.c_void_p, wt.BOOL, wt.DWORD,
                               ctypes.c_void_p, wt.LPCWSTR, ctypes.POINTER(STARTUPINFOW),
                               ctypes.POINTER(PROCESS_INFORMATION)]
k32.GetExitCodeProcess.argtypes = [wt.HANDLE, ctypes.POINTER(wt.DWORD)]
k32.WaitForSingleObject.argtypes = [wt.HANDLE, wt.DWORD]
k32.TerminateProcess.argtypes = [wt.HANDLE, wt.UINT]
k32.CloseHandle.argtypes = [wt.HANDLE]
k32.SetHandleInformation.argtypes = [wt.HANDLE, wt.DWORD, wt.DWORD]

_desk = None


def desktop() -> str:
    """Create (once per process) the hidden desktop; returns 'WinSta0\\<name>' for STARTUPINFO.lpDesktop.
    The handle stays open for the life of this Python process (the desktop disappears when the last handle and
    the last process on it are gone)."""
    global _desk
    if _desk is None:
        h = u32.CreateDesktopW(DESKTOP_NAME, None, None, 0, GENERIC_ALL, None)
        if not h:
            raise OSError(ctypes.get_last_error(), "CreateDesktopW failed")
        _desk = h
    return "WinSta0\\" + DESKTOP_NAME


class HiddenProc:
    def __init__(self, pi: PROCESS_INFORMATION):
        self._h = pi.hProcess
        self.pid = pi.dwProcessId
        self.returncode = None
        k32.CloseHandle(pi.hThread)

    def poll(self):
        if self.returncode is None:
            code = wt.DWORD()
            k32.GetExitCodeProcess(self._h, ctypes.byref(code))
            if code.value != STILL_ACTIVE:
                self.returncode = code.value
        return self.returncode

    def wait(self, timeout: float | None = None):
        ms = INFINITE if timeout is None else int(timeout * 1000)
        if k32.WaitForSingleObject(self._h, ms) == WAIT_TIMEOUT:
            raise subprocess.TimeoutExpired("EmuHawk", timeout)
        return self.poll()

    def kill(self):
        if self.poll() is None:
            k32.TerminateProcess(self._h, 1)

    def __del__(self):
        try:
            k32.CloseHandle(self._h)
        except Exception:
            pass


def launch(args: list[str], cwd: str, stdout_file) -> HiddenProc:
    """CreateProcessW on the hidden desktop, window hidden, stdout/stderr to the open file object."""
    import msvcrt
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = desktop()
    si.dwFlags = STARTF_USESHOWWINDOW | STARTF_USESTDHANDLES
    si.wShowWindow = SW_HIDE
    hout = msvcrt.get_osfhandle(stdout_file.fileno())
    k32.SetHandleInformation(hout, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT)
    si.hStdOutput = hout
    si.hStdError = hout
    si.hStdInput = None
    pi = PROCESS_INFORMATION()
    cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline(args))
    ok = k32.CreateProcessW(None, cmdline, None, None, True, CREATE_NEW_PROCESS_GROUP, None, cwd,
                            ctypes.byref(si), ctypes.byref(pi))
    if not ok:
        raise OSError(ctypes.get_last_error(), "CreateProcessW failed")
    _attach_to_job(pi.hProcess)
    return HiddenProc(pi)


# Every emulator joins one job object with KILL_ON_JOB_CLOSE, so if the Python process dies (killed, crashed),
# Windows closes the job handle and ends its emulators too (no orphaned EmuHawk processes).
_job = None


class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wt.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wt.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wt.DWORD), ("SchedulingClass", wt.DWORD)]


class _IO_COUNTERS(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint64) for n in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                                                "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION), ("IoInfo", _IO_COUNTERS),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


def _attach_to_job(hproc):
    global _job
    try:
        if _job is None:
            k32.CreateJobObjectW.restype = wt.HANDLE
            k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wt.LPCWSTR]
            k32.SetInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD]
            k32.AssignProcessToJobObject.argtypes = [wt.HANDLE, wt.HANDLE]
            j = k32.CreateJobObjectW(None, None)
            info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
            info.BasicLimitInformation.LimitFlags = 0x2000          # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            k32.SetInformationJobObject(j, 9, ctypes.byref(info), ctypes.sizeof(info))
            _job = j
        k32.AssignProcessToJobObject(_job, hproc)
    except Exception:
        pass
