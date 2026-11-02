"""Launch Mesen test runner and list the top-level windows of its PID (visible or not) while it runs."""
import ctypes, ctypes.wintypes as W, subprocess, sys, time
user32 = ctypes.windll.user32
def wins(pid):
    out = []
    @ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    def cb(h, l):
        p = W.DWORD(); user32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == pid:
            buf = ctypes.create_unicode_buffer(256); user32.GetWindowTextW(h, buf, 256)
            cls = ctypes.create_unicode_buffer(256); user32.GetClassNameW(h, cls, 256)
            r = W.RECT(); user32.GetWindowRect(h, ctypes.byref(r))
            out.append((h, bool(user32.IsWindowVisible(h)), buf.value, cls.value, (r.left, r.top, r.right, r.bottom)))
        return True
    user32.EnumWindows(cb, 0)
    return out
args = sys.argv[1:]
p = subprocess.Popen(args, creationflags=0x08000000)
seen = {}
while p.poll() is None:
    for w in wins(p.pid):
        if w[0] not in seen or seen[w[0]] != w[1:]:
            seen[w[0]] = w[1:]; print("win", w, flush=True)
    time.sleep(0.05)
print("exit", p.returncode)
