"""Development helper for the base stages: keeps N emulators alive and runs Python snippets against them.

    python tools/s2_daemon.py serve [n_emulators] [port]     (run in the background)
    python tools/s2_daemon.py run <script.py> [port]         (prints the script's output)
    python tools/s2_daemon.py stop [port]

The script is exec'd with globals: E (list of BizHawk), e (= E[0]), bc (contra.stages.base_common), G (a dict that
persists between runs). Not part of any run; exploration only.
"""
import contextlib
import io
import os
import socket
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PORT = 47321


def serve(n, port):
    from contra.emulator import BizHawk
    import contra.stages.base_common as bc
    E = [BizHawk(log_name=f"s2_daemon_{i}.log", fields=bc.make_fields()) for i in range(n)]
    (ROOT / "logs" / "s2_daemon.pids").write_text(" ".join(str(x.pid) for x in E) + f" py={os.getpid()}\n")
    G = {}
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(4)
    print("daemon ready", [x.pid for x in E], flush=True)
    try:
        while True:
            c, _ = srv.accept()
            data = b""
            while not data.endswith(b"\n"):
                d = c.recv(4096)
                if not d:
                    break
                data += d
            line = data.decode().strip()
            if line == "STOP":
                c.sendall(b"bye\n")
                c.close()
                break
            buf = io.StringIO()
            try:
                src = Path(line).read_text(encoding="utf-8")
                import importlib
                for name in list(sys.modules):
                    if name.startswith("contra.stages"):
                        importlib.reload(sys.modules[name])
                import contra.stages.base_common as bc2
                glb = {"E": E, "e": E[0], "bc": bc2, "G": G, "__name__": "__snippet__", "__file__": line}
                with contextlib.redirect_stdout(buf):
                    exec(compile(src, line, "exec"), glb)
            except Exception:
                buf.write("\n" + traceback.format_exc())
            out = buf.getvalue().encode("utf-8", "replace")
            c.sendall(str(len(out)).encode() + b"\n" + out)
            c.close()
    finally:
        for x in E:
            try:
                x.close()
            except Exception:
                pass


def client(msg, port):
    c = socket.socket()
    c.connect(("127.0.0.1", port))
    c.sendall((msg + "\n").encode())
    f = c.makefile("rb")
    head = f.readline().decode().strip()
    if head == "bye":
        print("stopped")
        return
    n = int(head)
    sys.stdout.buffer.write(f.read(n))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "serve":
        serve(int(a[1]) if len(a) > 1 else 1, int(a[2]) if len(a) > 2 else PORT)
    elif a[0] == "run":
        client(str(Path(a[1]).resolve()), int(a[2]) if len(a) > 2 else PORT)
    elif a[0] == "stop":
        client("STOP", int(a[1]) if len(a) > 1 else PORT)
