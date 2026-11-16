# The cartridge goes here

Put your own dump of the game in this directory as:

```
Super Mario Bros. 3 (USA).nes
```

The file is **never committed** — `.gitignore` excludes `*.nes`.

This run is pinned to **PRG0**, the first US revision. PRG1 (what No-Intro calls
`(USA) (Rev A)`) is a different build: different code layout, different RAM
assumptions, and the run's per-frame trace was recorded against PRG0. Nothing
fails loudly if you hand it PRG1 — it boots, the movie plays, and the game goes
somewhere else.

## Hashes (PRG0, the target build)

| | SHA-1 |
|---|---|
| headerless (PRG + CHR, the game data No-Intro lists) | `A611B90B4833B20A364BF06EE3BE3B9093EA4DF9` |
| whole `.nes` file as No-Intro ships it (NES 2.0 header) | `5F9019040FE23CB412A484E1EF430E59E589F9B4` |

To check what you have:

```
sha1sum "Super Mario Bros. 3 (USA).nes"
tail -c +17 "Super Mario Bros. 3 (USA).nes" | sha1sum      # headerless: the hash that identifies the game
```

The headerless hash is the one that identifies the build. The whole-file hash
also covers the 16-byte header, so a dump with iNES 1.0 instead of NES 2.0 has a
different whole-file hash and is still the same game.

## Dumps in the local collection, and which one works

`/extdrive/backups/SHARE/roms/nes/` carries eight Super Mario Bros. 3 files that
differ only in name and revision. Measured, not guessed:

| file | headerless SHA-1 | works? |
|---|---|---|
| `Super Mario Bros. 3 (USA).nes` | `a611b90b4833b20a364bf06ee3be3b9093ea4df9` | **yes — PRG0, this one** |
| `Super Mario Bros. 3 (USA) (Rev A).nes` | `bb894d104c796f69ba16587eb66c0275f5c2fc02` | no — it is PRG1 |
| `Super Mario Bros. 3 (U) (PRG1) [!].nes` | `bb894d104c796f69ba16587eb66c0275f5c2fc02` | no — PRG1, byte-identical to the line above |
| `Super Mario Bros. 3 (Europe).nes` | `31144c7c436cc78d7fd3ac42b224eee3a6c2babc` | no |
| `Super Mario Bros. 3 (Japan).nes` | `81a456c15296a31ea824a95a032cbf688e81cfdb` | no |
| `Super Mario Bros. 3 (Japan) (Rev A).nes` | `e250da736512e431146750cb71feb2c37b327f32` | no |

The trap is the third column of the first two rows: the file *named* `(Rev A)` is
PRG1, and the file named `(PRG1) [!]` is the same bytes. A name promising a
revision is not evidence about which revision it is.

The local `(USA).nes` has an **iNES 1.0** header (`4E 45 53 1A 10 10 40 00 ...`),
not the NES 2.0 header No-Intro ships, so its whole-file SHA-1 is
`A03E7E526E79DF222E048AE22214BCA2BC49C449` rather than `5F901904...`. Its game data
is PRG0: the headerless hash matches.

## What that means for the checker

`verify_bk2.py` knows both hashes. A whole-file mismatch is only a warning when
the headerless hash matches:

```
WARNING: ROM is not the expected Super Mario Bros. 3 (USA) PRG0 file
(whole-file SHA-1 5f901904...); the game data matches (headerless SHA-1),
only the 16-byte iNES header differs
```

It then checks the movie's own header, and that check *is* exact: BizHawk reports
`getromhash()` over the whole file, and the script requires it to equal
`5F901904...`. With the local iNES 1.0 dump the run plays the same frames, but the
report will list the `romhash` assertion as a failure. Use a NES 2.0-header PRG0
dump if the report itself has to come out clean.
