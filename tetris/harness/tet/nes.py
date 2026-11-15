"""Exact frame-level model of the game, tier 1: the ROM's own 6502 code run in Python.

This is not a general NES emulator. It executes the PRG of the owner's Tetris ROM instruction by instruction with
exact cycle counts, and models only the hardware the game's LOGIC can observe:
  * the vertical-blank flag ($2002 bit 7) and the NMI it raises (enable bit in $2000), on the real NTSC dot clock
    (341 dots x 262 lines, one dot dropped on odd frames while rendering is on, 3 dots per CPU cycle);
  * the controller shift register ($4016/$4017);
  * the 513/514-cycle CPU stall of a sprite DMA ($4014).
Picture and sound are not produced. Writes to the PPU ($2006/$2007) are kept in a 16 KB VRAM image so the
background tiles (text such as SUCCESS!, scores, the level menu) can be read back; APU and mapper writes are ignored.

A frame is the same thing as a BizHawk (NesHawk) frame: it starts when vertical blank starts (the NMI handler,
which also reads the controller, runs first) and RAM is compared at the end of it.

Speed: the code is translated block by block into Python functions the first time it is reached, and the game's
"wait for NMI" loop is skipped arithmetically; see bench() at the bottom.

    m = Machine()                 # power-on
    m.frame(buttons)              # advance one frame holding the button mask (A=0x80 B=0x40 Sel=0x20 Start=0x10
                                  # Up=0x08 Down=0x04 Left=0x02 Right=0x01)
    m.ram                         # the 2 KB of console RAM (bytearray)
    s = m.save(); m.load(s)       # snapshot / restore
"""
from __future__ import annotations

from .dis6502 import OPS, LEN, IMP, ACC, IMM, ZP, ZPX, ZPY, ABS, ABX, ABY, IND, IZX, IZY, REL
from .rom import prg as _prg

DOTS_PER_FRAME = 341 * 262
VBL_CLEAR_AFTER = 20 * 341            # vblank flag: set at line 241 dot 1, cleared at line 261 dot 1
SKIP_DECISION_AFTER = 20 * 341 + 338  # line 261 dot 339: the odd-frame dot skip is decided here

BRANCH = {"BPL": "not (n & 128)", "BMI": "n & 128", "BVC": "not v", "BVS": "v", "BCC": "not c", "BCS": "c",
          "BNE": "z", "BEQ": "not z"}
VARS = ("a", "x", "y", "sp", "c", "n", "z", "v")
MAX_BLOCK = 24


class Machine:
    __slots__ = ("ram", "prg", "vram", "a", "x", "y", "sp", "c", "n", "z", "v", "i", "d", "pc", "cyc",
                 "d0", "t_set", "t_clear", "vbl", "nmi_en", "rendering", "odd", "strobe", "shift", "buttons",
                 "flag", "pend", "nmi_req", "frames", "ppu_w", "ppu_addr", "ppu_inc", "blocks", "single", "env",
                 "dmc_seen", "io_log", "polls", "ppuctrl", "ppumask")

    # calibration against BizHawk (see knowledge/simulator.md): state of the dot clock at CPU cycle 0
    POWERON_VBL = False      # no vertical-blank flag at the start of the very first frame (measured on NesHawk)
    POWERON_ODD = 0
    POWERON_CYC = 7          # the reset sequence

    def __init__(self, prg: bytes | None = None):
        self.prg = prg if prg is not None else _prg()
        self.ram = bytearray(0x800)
        self.vram = bytearray(0x4000)
        self.blocks = {}
        self.single = {}
        self.env = {"ram": self.ram, "prg": self.prg}
        self.io_log = None
        self.power_on()

    # ------------------------------------------------------------------ power / snapshots
    def power_on(self):
        ram = self.ram
        # NesHawk's power-on RAM (read from BizHawk 2.11.1 at frame 0): 00 00 00 00 FF FF FF FF repeating.
        # The game clears $0000-$06FF itself; page 7 keeps this pattern except where the high-score table goes.
        for k in range(0x800):
            ram[k] = 0xFF if k & 4 else 0x00
        for k in range(0x4000):
            self.vram[k] = 0
        self.a = self.x = self.y = 0
        self.sp = 0xFD
        self.c = self.v = self.d = 0
        self.n = 0
        self.z = 1
        self.i = 1
        self.pc = self.prg[0x7FFC] | (self.prg[0x7FFD] << 8)
        self.cyc = self.POWERON_CYC
        self.d0 = 0
        self.t_set = 1                      # dot time of the vblank-flag edge that starts the next frame()
        self.t_clear = 0
        self.vbl = False
        self.nmi_en = False
        self.rendering = False
        self.odd = self.POWERON_ODD
        self.strobe = False
        self.shift = 0
        self.buttons = 0
        self.flag = 0
        self.pend = 0
        self.nmi_req = False
        self.frames = 0
        self.ppu_w = 0
        self.ppu_addr = 0
        self.ppu_inc = 1
        self.ppuctrl = 0
        self.ppumask = 0
        self.dmc_seen = 0
        self.polls = 0

    _SCALARS = ("a", "x", "y", "sp", "c", "n", "z", "v", "i", "d", "pc", "cyc", "d0", "t_set", "t_clear", "vbl",
                "nmi_en", "rendering", "odd", "strobe", "shift", "buttons", "flag", "pend", "nmi_req", "frames",
                "ppu_w", "ppu_addr", "ppu_inc", "dmc_seen", "polls", "ppuctrl", "ppumask")

    def save(self, vram: bool = False):
        return (bytes(self.ram), tuple(getattr(self, k) for k in self._SCALARS), bytes(self.vram) if vram else None)

    def load(self, s):
        self.ram[:] = s[0]
        for k, val in zip(self._SCALARS, s[1]):
            setattr(self, k, val)
        if s[2] is not None:
            self.vram[:] = s[2]

    # ------------------------------------------------------------------ bus
    def vbl_now(self, cyc):
        if self.vbl and 3 * cyc + self.d0 >= self.t_clear:
            self.vbl = False
        return self.vbl

    def read(self, ad, cyc):
        if ad >= 0x8000:
            return self.prg[ad - 0x8000]
        if ad < 0x2000:
            return self.ram[ad & 0x7FF]
        return self.io_read(ad, cyc)

    def io_read(self, ad, cyc):
        if ad < 0x4000:
            if ad & 7 == 2:
                val = 0x80 if self.vbl_now(cyc) else 0
                self.vbl = False
                self.ppu_w = 0
                return val
            return 0
        if ad == 0x4016:
            if self.strobe:
                bit = (self.buttons >> 7) & 1
            else:
                bit = (self.shift >> 7) & 1
                self.shift = ((self.shift << 1) | 1) & 0xFF
            self.polls += 1
            return 0x40 | bit
        if ad == 0x4017:
            return 0x40
        return 0

    def write(self, ad, val, cyc):
        if ad < 0x2000:
            self.ram[ad & 0x7FF] = val
        elif ad < 0x8000:
            self.io_write(ad, val, cyc)

    def io_write(self, ad, val, cyc):
        if self.io_log is not None:
            self.io_log.append((self.frames, cyc, ad, val))
        if ad < 0x4000:
            r = ad & 7
            if r == 0:
                en = (val & 0x80) != 0
                if en and not self.nmi_en and self.vbl_now(cyc):
                    self.nmi_req = True
                    self.flag = 1
                self.nmi_en = en
                self.ppu_inc = 32 if val & 4 else 1
                self.ppuctrl = val
            elif r == 1:
                self.rendering = (val & 0x18) != 0
                self.ppumask = val
            elif r == 5:
                self.ppu_w ^= 1
            elif r == 6:
                if self.ppu_w == 0:
                    self.ppu_addr = (self.ppu_addr & 0x00FF) | ((val & 0x3F) << 8)
                else:
                    self.ppu_addr = (self.ppu_addr & 0xFF00) | val
                self.ppu_w ^= 1
            elif r == 7:
                self.vram[self.ppu_addr & 0x3FFF] = val
                self.ppu_addr = (self.ppu_addr + self.ppu_inc) & 0x7FFF
        elif ad == 0x4014:
            self.pend += 513 + (cyc & 1)
            self.flag = 1
        elif ad == 0x4016:
            if val & 1:
                self.strobe = True
            elif self.strobe:
                self.strobe = False
                self.shift = self.buttons
        elif ad == 0x4015:
            if val & 0x10:
                self.dmc_seen += 1

    # ------------------------------------------------------------------ translation of 6502 code to Python
    def _rd(self, mode, op, acc):
        """(lines, expression, cycles, possible extra cycle) for an instruction that reads its operand."""
        prg = self.prg
        if mode == IMM:
            return [], str(op), 2, 0
        if mode == ZP:
            return [], f"ram[{op}]", 3, 0
        if mode == ZPX:
            return [], f"ram[({op} + x) & 255]", 4, 0
        if mode == ZPY:
            return [], f"ram[({op} + y) & 255]", 4, 0
        if mode == ABS:
            if op < 0x2000:
                return [], f"ram[{op & 0x7FF}]", 4, 0
            if op >= 0x8000:
                return [], str(prg[op - 0x8000]), 4, 0
            return [], f"S.io_read({op}, cyc + {acc + 3})", 4, 0
        if mode in (ABX, ABY):
            r = "x" if mode == ABX else "y"
            lines = []
            lo = op & 0xFF
            if lo:
                lines.append(f"if {r} > {255 - lo}: cyc += 1")
            if op >= 0x8000 and op + 255 <= 0xFFFF:
                expr = f"prg[{op - 0x8000} + {r}]"
            elif op + 255 < 0x800:
                expr = f"ram[{op} + {r}]"
            else:
                lines.append(f"ad = ({op} + {r}) & 65535")
                expr = f"(ram[ad] if ad < 2048 else S.read(ad, cyc + {acc + 3}))"
            return lines, expr, 4, 1 if lo else 0
        if mode == IZX:
            lines = [f"p = ({op} + x) & 255", "ad = ram[p] | (ram[(p + 1) & 255] << 8)"]
            return lines, f"(ram[ad] if ad < 2048 else S.read(ad, cyc + {acc + 5}))", 6, 0
        if mode == IZY:
            lines = [f"p = ram[{op}]", "if p + y > 255: cyc += 1",
                     f"ad = ((p | (ram[{(op + 1) & 255}] << 8)) + y) & 65535"]
            return lines, f"(ram[ad] if ad < 2048 else S.read(ad, cyc + {acc + 4}))", 5, 1
        raise ValueError(mode)

    def _wr(self, mode, op, val, acc):
        """(lines, cycles, touches io) for a store."""
        if mode == ZP:
            return [f"ram[{op}] = {val}"], 3, False
        if mode == ZPX:
            return [f"ram[({op} + x) & 255] = {val}"], 4, False
        if mode == ZPY:
            return [f"ram[({op} + y) & 255] = {val}"], 4, False
        if mode == ABS:
            if op < 0x2000:
                return [f"ram[{op & 0x7FF}] = {val}"], 4, False
            if op >= 0x8000:
                return [], 4, False                       # mapper register: no effect on the logic
            return [f"S.io_write({op}, {val}, cyc + {acc + 3})"], 4, True
        if mode in (ABX, ABY):
            r = "x" if mode == ABX else "y"
            if op + 255 < 0x800:
                return [f"ram[{op} + {r}] = {val}"], 5, False
            return [f"ad = ({op} + {r}) & 65535", f"if ad < 2048: ram[ad] = {val}",
                    f"else: S.write(ad, {val}, cyc + {acc + 4})"], 5, True
        if mode == IZX:
            return [f"p = ({op} + x) & 255", "ad = ram[p] | (ram[(p + 1) & 255] << 8)",
                    f"if ad < 2048: ram[ad] = {val}", f"else: S.write(ad, {val}, cyc + {acc + 5})"], 6, True
        if mode == IZY:
            return [f"ad = ((ram[{op}] | (ram[{(op + 1) & 255}] << 8)) + y) & 65535",
                    f"if ad < 2048: ram[ad] = {val}", f"else: S.write(ad, {val}, cyc + {acc + 5})"], 6, True
        raise ValueError(mode)

    _RMW = {"INC": ["m = (m + 1) & 255", "n = z = m"], "DEC": ["m = (m - 1) & 255", "n = z = m"],
            "ASL": ["c = m >> 7", "m = (m << 1) & 255", "n = z = m"], "LSR": ["c = m & 1", "m >>= 1", "n = z = m"],
            "ROL": ["m = (m << 1) | c", "c = m >> 8", "m &= 255", "n = z = m"],
            "ROR": ["m |= c << 8", "c = m & 1", "m >>= 1", "n = z = m"]}

    def _instr(self, pc, acc):
        """Translate one instruction. Returns (lines, length, cycles, extra, end) where end is None or
        ('ret', expr) / ('br', cond, target, taken_cycles) / ('io',)."""
        prg = self.prg
        opc = prg[pc - 0x8000]
        if opc not in OPS:
            raise RuntimeError(f"illegal opcode ${opc:02X} at ${pc:04X}")
        mn, mode = OPS[opc]
        ln = LEN[mode]
        op = 0
        if ln == 2:
            op = prg[pc + 1 - 0x8000]
        elif ln == 3:
            op = prg[pc + 1 - 0x8000] | (prg[pc + 2 - 0x8000] << 8)
        nxt = (pc + ln) & 0xFFFF
        L = []
        if mn in ("LDA", "LDX", "LDY"):
            pre, e, cy, ex = self._rd(mode, op, acc)
            r = mn[2].lower()
            return pre + [f"{r} = {e}", f"n = z = {r}"], ln, cy, ex, None
        if mn in ("AND", "ORA", "EOR"):
            pre, e, cy, ex = self._rd(mode, op, acc)
            o = {"AND": "&", "ORA": "|", "EOR": "^"}[mn]
            return pre + [f"a {o}= {e}", "n = z = a"], ln, cy, ex, None
        if mn in ("ADC", "SBC"):
            pre, e, cy, ex = self._rd(mode, op, acc)
            m = f"m = {e}" if mn == "ADC" else f"m = ({e}) ^ 255"
            return pre + [m, "t = a + m + c", "v = ((~(a ^ m)) & (a ^ t) & 128) >> 7", "c = t >> 8", "a = t & 255",
                          "n = z = a"], ln, cy, ex, None
        if mn in ("CMP", "CPX", "CPY"):
            pre, e, cy, ex = self._rd(mode, op, acc)
            r = {"CMP": "a", "CPX": "x", "CPY": "y"}[mn]
            return pre + [f"t = {r} - {e}", "c = 0 if t < 0 else 1", "n = z = t & 255"], ln, cy, ex, None
        if mn == "BIT":
            pre, e, cy, ex = self._rd(mode, op, acc)
            return pre + [f"m = {e}", "z = a & m", "n = m", "v = (m >> 6) & 1"], ln, cy, ex, None
        if mn in ("STA", "STX", "STY"):
            lines, cy, io = self._wr(mode, op, mn[2].lower(), acc)
            return lines, ln, cy, 0, ("io",) if io else None
        if mn in self._RMW:
            body = self._RMW[mn]
            if mode == ACC:
                return [x.replace("m", "a") for x in body], ln, 2, 0, None
            if mode == ZP:
                idx, cy = str(op), 5
            elif mode == ZPX:
                idx, cy = f"({op} + x) & 255", 6
            elif mode == ABS:
                if op >= 0x8000:                          # INC on ROM: resets the MMC1 shift register, RAM unchanged
                    return [f"m = {prg[op - 0x8000]}"] + body, ln, 6, 0, None
                if op >= 0x2000:
                    raise RuntimeError(f"read-modify-write on I/O at ${pc:04X}")
                idx, cy = str(op & 0x7FF), 6
            elif mode == ABX:
                if op + 255 >= 0x800:
                    raise RuntimeError(f"read-modify-write abs,X outside RAM at ${pc:04X}")
                idx, cy = f"{op} + x", 7
            else:
                raise ValueError(mode)
            return [f"q = {idx}", "m = ram[q]"] + body + ["ram[q] = m"], ln, cy, 0, None
        if mn in BRANCH:
            taken = 3 + (1 if (nxt & 0xFF00) != (op_target(pc, op) & 0xFF00) else 0)
            return [], ln, 2, 0, ("br", BRANCH[mn], op_target(pc, op), taken)
        if mn == "JMP":
            if mode == ABS:
                return [], ln, 3, 0, ("ret", str(op))
            lo = f"(ram[{op}] if {op} < 2048 else S.read({op}, cyc))"
            hi_ad = (op & 0xFF00) | ((op + 1) & 0xFF)
            hi = f"(ram[{hi_ad}] if {hi_ad} < 2048 else S.read({hi_ad}, cyc))"
            return [], ln, 5, 0, ("ret", f"{lo} | ({hi} << 8)")
        if mn == "JSR":
            ra = (pc + 2) & 0xFFFF
            return [f"ram[256 + sp] = {ra >> 8}", "sp = (sp - 1) & 255", f"ram[256 + sp] = {ra & 255}",
                    "sp = (sp - 1) & 255"], ln, 6, 0, ("ret", str(op))
        if mn == "RTS":
            return ["sp = (sp + 1) & 255", "t = ram[256 + sp]", "sp = (sp + 1) & 255",
                    "t |= ram[256 + sp] << 8"], ln, 6, 0, ("ret", "(t + 1) & 65535")
        if mn == "RTI":
            return ["sp = (sp + 1) & 255", "p = ram[256 + sp]", "c = p & 1", "z = 0 if p & 2 else 1",
                    "S.i = (p >> 2) & 1", "S.d = (p >> 3) & 1", "v = (p >> 6) & 1", "n = p & 128",
                    "sp = (sp + 1) & 255", "t = ram[256 + sp]", "sp = (sp + 1) & 255",
                    "t |= ram[256 + sp] << 8"], ln, 6, 0, ("ret", "t")
        simple = {
            "NOP": ([], 2), "CLC": (["c = 0"], 2), "SEC": (["c = 1"], 2), "CLV": (["v = 0"], 2),
            "CLD": (["S.d = 0"], 2), "SED": (["S.d = 1"], 2), "CLI": (["S.i = 0"], 2), "SEI": (["S.i = 1"], 2),
            "TAX": (["x = a", "n = z = x"], 2), "TAY": (["y = a", "n = z = y"], 2),
            "TXA": (["a = x", "n = z = a"], 2), "TYA": (["a = y", "n = z = a"], 2),
            "TSX": (["x = sp", "n = z = x"], 2), "TXS": (["sp = x"], 2),
            "INX": (["x = (x + 1) & 255", "n = z = x"], 2), "INY": (["y = (y + 1) & 255", "n = z = y"], 2),
            "DEX": (["x = (x - 1) & 255", "n = z = x"], 2), "DEY": (["y = (y - 1) & 255", "n = z = y"], 2),
            "PHA": (["ram[256 + sp] = a", "sp = (sp - 1) & 255"], 3),
            "PLA": (["sp = (sp + 1) & 255", "a = ram[256 + sp]", "n = z = a"], 4),
            "PHP": (["ram[256 + sp] = (n & 128) | (v << 6) | 48 | (S.d << 3) | (S.i << 2) | (0 if z else 2) | c",
                     "sp = (sp - 1) & 255"], 3),
            "PLP": (["sp = (sp + 1) & 255", "p = ram[256 + sp]", "c = p & 1", "z = 0 if p & 2 else 1",
                     "S.i = (p >> 2) & 1", "S.d = (p >> 3) & 1", "v = (p >> 6) & 1", "n = p & 128"], 4),
        }
        if mn in simple:
            lines, cy = simple[mn]
            return list(lines), ln, cy, 0, None
        raise RuntimeError(f"unhandled {mn} at ${pc:04X}")

    def _compile(self, pc0, max_instr):
        import re
        body = []
        acc = 0            # static cycles so far
        maxcyc = 0
        pc = pc0
        n_ins = 0
        end = None
        first = None
        while True:
            lines, ln, cy, ex, e = self._instr(pc, acc)
            if first is None:
                first = (self.prg[pc - 0x8000], lines, e)
            body.append(f"# {pc:04X}")
            body.extend(lines)
            n_ins += 1
            pc = (pc + ln) & 0xFFFF
            if e is not None and e[0] == "br":
                _, cond, target, taken = e
                maxcyc = acc + max(taken, cy) + maxcyc_extra(body)
                end = ("br", cond, target, acc + taken, acc + cy, pc)
                break
            acc += cy
            if e is not None and e[0] == "ret":
                end = ("ret", e[1], acc)
                break
            if e is not None or n_ins >= max_instr:
                end = ("ret", str(pc), acc)
                break
        text = "\n".join(body)
        used = [v for v in VARS if re.search(rf"\b{v}\b", text + " " + " ".join(str(x) for x in end))]
        load = "".join(f"    {v} = S.{v}\n" for v in used) + "    cyc = S.cyc\n"

        def store(cycles):
            return "".join(f"S.{v} = {v}; " for v in used) + f"S.cyc = cyc + {cycles}"
        src = [f"def blk(S):\n{load}"]
        for line in body:
            src.append("    " + line + "\n")
        if end[0] == "br":
            _, cond, target, cyt, cyn, nxt = end
            src.append(f"    if {cond}:\n        {store(cyt)}\n        return {target}\n")
            src.append(f"    {store(cyn)}\n    return {nxt}\n")
            mx = max(cyt, cyn)
        else:
            _, expr, cy = end
            src.append(f"    {store(cy)}\n    return {expr}\n")
            mx = cy
        mx += sum(1 for line in body if "cyc += 1" in line)
        code = "".join(src)
        ns = {}
        exec(compile(code, f"<blk {pc0:04X}>", "exec"), self.env, ns)
        f = ns["blk"]
        # the game's "wait for NMI" loop: LDA zp / BEQ self  ->  (zp address, cycles per turn)
        idle = None
        if max_instr > 1 and n_ins == 2 and end[0] == "br" and end[2] == pc0 and end[1] == "not z" \
                and self.prg[pc0 - 0x8000] == 0xA5:
            idle = (self.prg[pc0 + 1 - 0x8000], end[3])
        return f, mx, idle

    # ------------------------------------------------------------------ running
    def _run(self, lim):
        blocks = self.blocks
        single = self.single
        ram = self.ram
        S = self
        pc = self.pc
        while S.cyc < lim:
            ent = blocks.get(pc)
            if ent is None:
                ent = blocks[pc] = self._compile(pc, MAX_BLOCK)
            f, mx, idle = ent
            if S.cyc + mx < lim:
                if idle is not None and ram[idle[0]] == 0:
                    k = (lim - S.cyc) // idle[1] - 2
                    if k > 0:
                        S.cyc += k * idle[1]
                pc = f(S)
            else:
                g = single.get(pc)
                if g is None:
                    g = single[pc] = self._compile(pc, 1)[0]
                pc = g(S)
            if S.flag:
                S.flag = 0
                if S.pend:
                    S.cyc += S.pend
                    S.pend = 0
                if S.nmi_req:
                    S.nmi_req = False
                    self.pc = pc
                    self._nmi()
                    pc = self.pc
        self.pc = pc

    def _nmi(self):
        ram = self.ram
        pc = self.pc
        sp = self.sp
        ram[256 + sp] = pc >> 8
        sp = (sp - 1) & 255
        ram[256 + sp] = pc & 255
        sp = (sp - 1) & 255
        ram[256 + sp] = (self.n & 128) | (self.v << 6) | 32 | (self.d << 3) | (self.i << 2) | \
                        (0 if self.z else 2) | self.c
        self.sp = (sp - 1) & 255
        self.i = 1
        self.pc = self.prg[0x7FFA] | (self.prg[0x7FFB] << 8)
        self.cyc += 7

    def frame(self, buttons: int = 0):
        """One BizHawk frame: vertical blank starts (flag, NMI), then the CPU runs until the next one."""
        self.buttons = buttons
        if self.frames or self.POWERON_VBL:
            self.vbl = True
            self.t_clear = self.t_set + VBL_CLEAR_AFTER
            if self.nmi_en:
                self._nmi()
        t_dec = self.t_set + SKIP_DECISION_AFTER
        self._run((t_dec - self.d0 + 2) // 3)
        skip = 1 if (self.odd and self.rendering) else 0
        self.odd ^= 1
        self.t_set += DOTS_PER_FRAME - skip
        self._run((self.t_set - self.d0) // 3 + 2)
        self.frames += 1

    def run(self, masks):
        for b in masks:
            self.frame(b)

    # ------------------------------------------------------------------ helpers
    def tiles(self, row: int, col: int, n: int, table: int = 0x2000) -> bytes:
        """n background tile numbers from the nametable image, starting at (row, col)."""
        a = table + row * 32 + col
        return bytes(self.vram[a:a + n])


def op_target(pc, op):
    return (pc + 2 + (op - 256 if op > 127 else op)) & 0xFFFF


def maxcyc_extra(body):
    return 0


def bench(frames=3000):
    import time
    m = Machine()
    t0 = time.perf_counter()
    for k in range(frames):
        m.frame(0x10 if k % 40 < 2 else 0)
    dt = time.perf_counter() - t0
    print(f"{frames} frames in {dt:.2f} s = {frames / dt:.0f} fps; blocks {len(m.blocks)} single {len(m.single)}; "
          f"mode {m.ram[0xC0]} frameCounter {m.ram[0xB1]} rng {m.ram[0x17]:02X}{m.ram[0x18]:02X}")


if __name__ == "__main__":
    bench()
