# The cartridge goes here

Put your own dump of the game in this directory as:

```
Contra (USA).nes
```

The file is **never committed** — `.gitignore` excludes `*.nes`.

## Hashes

| | CRC32 | SHA-1 |
|---|---|---|
| whole `.nes` file (with its 16-byte iNES header) | `C50A8304` | `C9EA66BB7CB30AD5343F1721B1D4D3219859319B` |
| headerless (the game data, what No-Intro lists) | `F6035030` | `979494E7869AC7AB4815FDBD1DC99F893F713FBF` |

To check what you have:

```
sha1sum "Contra (USA).nes"
```

## Source (local)

Found at `/extdrive/backups/SHARE/roms/nes/Contra (USA).nes`.
