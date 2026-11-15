# The cartridge goes here

Put your own dump of the game in this directory as:

```
Tetris (USA).nes
```

The file is **never committed** — `.gitignore` excludes `*.nes`.

## Hashes

| | SHA-1 |
|---|---|
| headerless (PRG + CHR, the game data No-Intro lists) | `FD9079CB5E8479EB06D93C2AE5175BFCE871746A` |
| whole `.nes` file as No-Intro ships it (NES 2.0 header) | `3026D28B63D94C921FE58364F8B0659D10B5A0AC` |

To check what you have:

```
sha1sum "Tetris (USA).nes"
tail -c +17 "Tetris (USA).nes" | sha1sum      # headerless: the hash that identifies the game
```

The headerless hash is the one that matters: a dump with an iNES 1.0 header instead of
NES 2.0 has a different whole-file hash and is still the same game. The harness checks
the headerless one.

## Where the harness looks

`harness/tet/rom.py` does not read this directory. It reads **`harness/Tetris (USA).zip`**
— a one-file zip of the same dump, in memory, never extracted to disk — and refuses it
unless the headerless SHA-1 above matches:

```
cd tetris
cp "/path/to/Tetris (USA).zip" harness/       # one .nes inside; game data SHA-1 FD9079CB...
```

That zip is a ROM as much as the `.nes` is, so it is gitignored too. The standalone
checker is the other consumer and takes a plain `.nes`:

```
python verify_bk2.py --bizhawk /path/to/BizHawk-2.11.1 --rom roms/"Tetris (USA).nes"
```

## Source (local)

Found at `/extdrive/backups/SHARE/roms/nes/Tetris (USA).nes` (49,168 bytes, iNES 1.0
header, whole-file SHA-1 `77747840541BFC62A28A5957692A98C550BD6B2B`, headerless
`FD9079CB5E8479EB06D93C2AE5175BFCE871746A`). The `Tetris (USA).zip` beside it in the
same folder holds the identical file as its single entry.
