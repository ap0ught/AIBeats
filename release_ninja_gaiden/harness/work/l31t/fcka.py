"""Keepalive for ng.fastcore (import before creating FastCores).

Measured 2026-10-24: Mesen's Lua dies (connection reset) when one exec callback lasts more than ~1 s, and the
fastcore server waits for the next command INSIDE the callback, so any Python think time > ~1 s between two commands
to the same core kills it (big beams died after 10-150 generations). This module serializes each core's commands
with a lock and, every 0.2 s, sends a 1-row RUN from the core's keepalive slot (c._ka_slot, set it after the PUT) to
every core idle for > 0.3 s; the RUN returns to emulation and ends the callback. Only safe for code that never relies
on the emulator's CURRENT state between commands (run_batch always loads a slot; step()/save() sequences do not)."""
import threading, time, functools
from ng import fastcore as F

_cores = []
_reg = threading.Lock()

def _wrap(name):
    orig = getattr(F.FastCore, name)
    @functools.wraps(orig)
    def w(self, *a, **k):
        lk = self.__dict__.get('_lk')
        if lk is None:
            return orig(self, *a, **k)
        with lk:
            try:
                return orig(self, *a, **k)
            finally:
                self._t = time.time()
    setattr(F.FastCore, name, w)

for _n in ('run_batch', 'save', 'load', 'get', 'put', 'drop', 'drop_prefix', 'ram', 'step', 'poke', 'info', 'close'):
    if hasattr(F.FastCore, _n):
        _wrap(_n)

_init = F.FastCore.__init__
def _init2(self, *a, **k):
    _init(self, *a, **k)
    self._lk = threading.RLock(); self._t = time.time(); self._ka_slot = None; self._dead = False
    with _reg: _cores.append(self)
F.FastCore.__init__ = _init2

def _ka():
    while True:
        time.sleep(0.2)
        with _reg: cs = list(_cores)
        for c in cs:
            if c._dead or not c._ka_slot or time.time() - c._t < 0.3:
                continue
            if c._lk.acquire(blocking=False):
                try:
                    F.FastCore.run_batch.__wrapped__(c, c._ka_slot, [[()]], record='last')
                    c._t = time.time()
                except Exception:
                    c._dead = True
                finally:
                    c._lk.release()

def forget(c):
    c._dead = True
    with _reg:
        if c in _cores: _cores.remove(c)

threading.Thread(target=_ka, daemon=True).start()
