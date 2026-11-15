"""A small recursive-descent 6502 disassembler for the Tetris PRG (32 KB at $8000-$FFFF, no bank switching).

    python -m tet.dis6502 [out.txt]         # writes work/disasm/tetris.asm.txt by default

It follows code from the three vectors, through branches, JMP and JSR, and through the game's jump-table helper
(a JSR to a routine that pops its return address and jumps through the word table that follows the JSR: found by
its byte pattern, not by a hard-coded address). Bytes never reached as code are printed as data. Labels and
comments come from knowledge/labels.json when it exists ({"8005": "nmi", ...} and {"zp": {"40": "tetriminoX"}}).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .rom import prg, PROJECT

# mnemonic, addressing mode for the official opcodes
IMP, ACC, IMM, ZP, ZPX, ZPY, ABS, ABX, ABY, IND, IZX, IZY, REL = range(13)
LEN = {IMP: 1, ACC: 1, IMM: 2, ZP: 2, ZPX: 2, ZPY: 2, ABS: 3, ABX: 3, ABY: 3, IND: 3, IZX: 2, IZY: 2, REL: 2}
OPS: dict[int, tuple[str, int]] = {}


def _add(mn, modes):
    for mode, op in modes.items():
        OPS[op] = (mn, mode)


_add("ADC", {IMM: 0x69, ZP: 0x65, ZPX: 0x75, ABS: 0x6D, ABX: 0x7D, ABY: 0x79, IZX: 0x61, IZY: 0x71})
_add("AND", {IMM: 0x29, ZP: 0x25, ZPX: 0x35, ABS: 0x2D, ABX: 0x3D, ABY: 0x39, IZX: 0x21, IZY: 0x31})
_add("ASL", {ACC: 0x0A, ZP: 0x06, ZPX: 0x16, ABS: 0x0E, ABX: 0x1E})
_add("BIT", {ZP: 0x24, ABS: 0x2C})
_add("CMP", {IMM: 0xC9, ZP: 0xC5, ZPX: 0xD5, ABS: 0xCD, ABX: 0xDD, ABY: 0xD9, IZX: 0xC1, IZY: 0xD1})
_add("CPX", {IMM: 0xE0, ZP: 0xE4, ABS: 0xEC})
_add("CPY", {IMM: 0xC0, ZP: 0xC4, ABS: 0xCC})
_add("DEC", {ZP: 0xC6, ZPX: 0xD6, ABS: 0xCE, ABX: 0xDE})
_add("EOR", {IMM: 0x49, ZP: 0x45, ZPX: 0x55, ABS: 0x4D, ABX: 0x5D, ABY: 0x59, IZX: 0x41, IZY: 0x51})
_add("INC", {ZP: 0xE6, ZPX: 0xF6, ABS: 0xEE, ABX: 0xFE})
_add("JMP", {ABS: 0x4C, IND: 0x6C})
_add("JSR", {ABS: 0x20})
_add("LDA", {IMM: 0xA9, ZP: 0xA5, ZPX: 0xB5, ABS: 0xAD, ABX: 0xBD, ABY: 0xB9, IZX: 0xA1, IZY: 0xB1})
_add("LDX", {IMM: 0xA2, ZP: 0xA6, ZPY: 0xB6, ABS: 0xAE, ABY: 0xBE})
_add("LDY", {IMM: 0xA0, ZP: 0xA4, ZPX: 0xB4, ABS: 0xAC, ABX: 0xBC})
_add("LSR", {ACC: 0x4A, ZP: 0x46, ZPX: 0x56, ABS: 0x4E, ABX: 0x5E})
_add("ORA", {IMM: 0x09, ZP: 0x05, ZPX: 0x15, ABS: 0x0D, ABX: 0x1D, ABY: 0x19, IZX: 0x01, IZY: 0x11})
_add("ROL", {ACC: 0x2A, ZP: 0x26, ZPX: 0x36, ABS: 0x2E, ABX: 0x3E})
_add("ROR", {ACC: 0x6A, ZP: 0x66, ZPX: 0x76, ABS: 0x6E, ABX: 0x7E})
_add("SBC", {IMM: 0xE9, ZP: 0xE5, ZPX: 0xF5, ABS: 0xED, ABX: 0xFD, ABY: 0xF9, IZX: 0xE1, IZY: 0xF1})
_add("STA", {ZP: 0x85, ZPX: 0x95, ABS: 0x8D, ABX: 0x9D, ABY: 0x99, IZX: 0x81, IZY: 0x91})
_add("STX", {ZP: 0x86, ZPY: 0x96, ABS: 0x8E})
_add("STY", {ZP: 0x84, ZPX: 0x94, ABS: 0x8C})
for _mn, _op in (("BPL", 0x10), ("BMI", 0x30), ("BVC", 0x50), ("BVS", 0x70), ("BCC", 0x90), ("BCS", 0xB0),
                 ("BNE", 0xD0), ("BEQ", 0xF0)):
    OPS[_op] = (_mn, REL)
for _mn, _op in (("BRK", 0x00), ("CLC", 0x18), ("CLD", 0xD8), ("CLI", 0x58), ("CLV", 0xB8), ("DEX", 0xCA),
                 ("DEY", 0x88), ("INX", 0xE8), ("INY", 0xC8), ("NOP", 0xEA), ("PHA", 0x48), ("PHP", 0x08),
                 ("PLA", 0x68), ("PLP", 0x28), ("RTI", 0x40), ("RTS", 0x60), ("SEC", 0x38), ("SED", 0xF8),
                 ("SEI", 0x78), ("TAX", 0xAA), ("TAY", 0xA8), ("TSX", 0xBA), ("TXA", 0x8A), ("TXS", 0x9A),
                 ("TYA", 0x98)):
    OPS[_op] = (_mn, IMP)

BASE = 0x8000
# asl a / tay / iny / pla / sta zp / pla / sta zp : start of the "jump through the table after the JSR" helper
SWITCH_SIG = bytes([0x0A, 0xA8, 0xC8, 0x68, 0x85])


def find_switch(p: bytes) -> list[int]:
    out, i = [], 0
    while True:
        i = p.find(SWITCH_SIG, i)
        if i < 0:
            return out
        if p[i + 6] == 0x68 and p[i + 7] == 0x85:
            out.append(BASE + i)
        i += 1


class Dis:
    def __init__(self, p: bytes | None = None):
        self.p = p if p is not None else prg()
        self.code: dict[int, tuple[str, int, int]] = {}      # addr -> (mnemonic, mode, operand)
        self.covered = bytearray(len(self.p))                # 1 = part of an instruction
        self.labels: set[int] = set()
        self.subs: set[int] = set()
        self.tables: dict[int, list[int]] = {}               # table address -> entries (jump tables)
        self.switch = find_switch(self.p)
        self.xref: dict[int, set[int]] = {}
        # routines that take a 2-byte argument stored right after the JSR: their first instruction is a JSR to a
        # helper that starts with TSX / LDA $0103,X (reads the caller's return address) and adds 2 to it
        self.inline2: set[int] = set()
        p = self.p
        for i in range(len(p) - 3):
            if p[i] == 0x20:
                h = p[i + 1] | (p[i + 2] << 8)
                if BASE <= h <= 0xFFFF - 4 and p[h - BASE:h - BASE + 4] == bytes([0xBA, 0xBD, 0x03, 0x01]):
                    self.inline2.add(BASE + i)

    def rd(self, a):
        return self.p[a - BASE]

    def rd16(self, a):
        return self.p[a - BASE] | (self.p[a - BASE + 1] << 8)

    def trace(self, entries):
        work = list(entries)
        while work:
            a = work.pop()
            while BASE <= a <= 0xFFFF and a not in self.code:
                if self.covered[a - BASE]:
                    break                                    # lands inside an instruction: leave it
                op = self.rd(a)
                if op not in OPS:
                    break                                    # illegal opcode: not code
                mn, mode = OPS[op]
                n = LEN[mode]
                if a + n - 1 > 0xFFFF:
                    break
                operand = 0
                if n == 2:
                    operand = self.rd(a + 1)
                elif n == 3:
                    operand = self.rd16(a + 1)
                if mode == REL:
                    operand = a + 2 + (operand - 256 if operand > 127 else operand)
                self.code[a] = (mn, mode, operand)
                for k in range(n):
                    self.covered[a - BASE + k] = 1
                nxt = a + n
                if mode == REL:
                    self.labels.add(operand)
                    self.xref.setdefault(operand, set()).add(a)
                    work.append(operand)
                elif mn == "JSR":
                    self.subs.add(operand)
                    self.xref.setdefault(operand, set()).add(a)
                    if operand >= BASE:
                        work.append(operand)
                    if operand in self.inline2:
                        self.tables[nxt] = [self.rd16(nxt)]           # the inline argument (a data address)
                        self.covered[nxt - BASE] = self.covered[nxt - BASE + 1] = 2
                        self.inline_args = getattr(self, "inline_args", set()) | {nxt}
                        nxt += 2
                    if operand in self.switch:
                        # word table follows; it ends where the first of its own targets (or other code) begins
                        t, ents, lo = nxt, [], 0x10000
                        while t + 1 <= 0xFFFF and t < lo and t not in self.code:
                            w = self.rd16(t)
                            if w < BASE:
                                break
                            ents.append(w)
                            lo = min(lo, w) if w > nxt else lo
                            t += 2
                        self.tables[nxt] = ents
                        for w in ents:
                            self.labels.add(w)
                            self.xref.setdefault(w, set()).add(a)
                            work.append(w)
                        for k in range(nxt - BASE, nxt - BASE + 2 * len(ents)):
                            self.covered[k] = 2
                        break
                elif mn == "JMP":
                    if mode == ABS:
                        self.labels.add(operand)
                        self.xref.setdefault(operand, set()).add(a)
                        if operand >= BASE:
                            work.append(operand)
                    break
                elif mn in ("RTS", "RTI", "BRK"):
                    break
                a = nxt

    def run(self):
        vec = [self.rd16(0xFFFA), self.rd16(0xFFFC), self.rd16(0xFFFE)]
        for v in vec:
            self.subs.add(v)
        self.trace(vec)
        return self

    # -- output ------------------------------------------------------------
    def fmt_operand(self, mode, v, names, zp):
        def sym(x, w):
            if x in names:
                return names[x]
            if x < 0x100 and x in zp:
                return zp[x]
            if x in zp:
                return zp[x]
            return ("$%02X" if w == 2 else "$%04X") % x
        if mode in (IMP,):
            return ""
        if mode == ACC:
            return "A"
        if mode == IMM:
            return "#$%02X" % v
        if mode == ZP:
            return sym(v, 2)
        if mode == ZPX:
            return sym(v, 2) + ",X"
        if mode == ZPY:
            return sym(v, 2) + ",Y"
        if mode in (ABS, REL):
            return sym(v, 4)
        if mode == ABX:
            return sym(v, 4) + ",X"
        if mode == ABY:
            return sym(v, 4) + ",Y"
        if mode == IND:
            return "(" + sym(v, 4) + ")"
        if mode == IZX:
            return "(" + sym(v, 2) + ",X)"
        if mode == IZY:
            return "(" + sym(v, 2) + "),Y"
        return "?"

    def listing(self, names=None, zp=None, comments=None) -> str:
        names = dict(names or {})
        zp = zp or {}
        comments = comments or {}
        for a in sorted(self.subs | self.labels):
            if a >= BASE and a not in names:
                names[a] = ("sub_%04X" if a in self.subs else "L%04X") % a
        out = []
        a = BASE
        while a <= 0xFFFF:
            if a in comments:
                for line in comments[a].split("\n"):
                    out.append("; " + line)
            if a in self.code:
                mn, mode, v = self.code[a]
                n = LEN[mode]
                if a in names:
                    if a in self.subs:
                        out.append("")
                    xr = sorted(self.xref.get(a, ()))
                    out.append("%s:%s" % (names[a], ("        ; from " + " ".join("%04X" % x for x in xr[:8]) +
                                                    (" ..." if len(xr) > 8 else "")) if xr else ""))
                raw = " ".join("%02X" % self.rd(a + k) for k in range(n))
                out.append("  %04X  %-9s %s %s" % (a, raw, mn, self.fmt_operand(mode, v, names, zp)))
                if mn in ("RTS", "RTI", "JMP"):
                    out.append("")
                a += n
            elif a in getattr(self, "inline_args", ()):
                w = self.tables[a][0]
                out.append("  %04X  %02X %02X     .addr $%04X        ; inline argument of the JSR above" % (
                    a, w & 255, w >> 8, w))
                a += 2
            elif a in self.tables:
                for i, w in enumerate(self.tables[a]):
                    out.append("  %04X  %02X %02X     .addr %s        ; [%d]" % (
                        a + 2 * i, w & 255, w >> 8, names.get(w, "$%04X" % w), i))
                a += 2 * len(self.tables[a])
            else:
                b = a
                while b <= 0xFFFF and b not in self.code and b not in self.tables and (b == a or b not in comments) \
                        and (b == a or b not in names) and b - a < 16:
                    b += 1
                if a in names:
                    out.append("%s:" % names[a])
                out.append("  %04X  .byte %s" % (a, ",".join("$%02X" % self.rd(k) for k in range(a, b))))
                a = b
        return "\n".join(out) + "\n"


def load_labels():
    p = PROJECT / "knowledge" / "labels.json"
    names, zp, comments = {}, {}, {}
    if p.exists():
        j = json.loads(p.read_text(encoding="utf-8"))
        for k, v in j.get("code", {}).items():
            names[int(k, 16)] = v
        for k, v in j.get("ram", {}).items():
            zp[int(k, 16)] = v
        for k, v in j.get("comments", {}).items():
            comments[int(k, 16)] = v
    return names, zp, comments


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT / "work" / "disasm" / "tetris.asm.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    d = Dis().run()
    names, zp, comments = load_labels()
    out.write_text(d.listing(names, zp, comments), encoding="utf-8")
    ncode = sum(1 for c in d.covered if c == 1)
    print(f"{out}: {len(d.code)} instructions, {ncode} code bytes, {len(d.tables)} jump tables, "
          f"switch helper at {[hex(x) for x in d.switch]}, subs {len(d.subs)}")


if __name__ == "__main__":
    main()
