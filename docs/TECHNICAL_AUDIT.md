# Technical audit — 2026-11-22

**Method:** static inspection of owner-supplied HOWaW_FirefightDemov1.zip. No execution, decompilation, Vita compilation or dynamic instrumentation performed.

| Input | Size (bytes) | SHA-256 | Assessment |
| --- | ---: | --- | --- |
| HOWaW_FirefightDemov1.zip | compressed archive | 423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62 | VERIFIED |
| HOWaW_FirefightDemov1.exe | 18,142,424 | cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f | VERIFIED |
| Music/menu.mp3 | 1,293,667 | e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0 | VERIFIED |

ZIP lists exactly the EXE and Music/menu.mp3; CRC passed.

## Verified structure
- Windows MZ/PE32 executable, Intel x86 machine value 0x014c; 9 PE sections.
- End of PE sections ~2,009,088 bytes; trailing overlay ~16,133,336 bytes (not necessarily exclusively game data).
- Embedded markers include `Game Maker`, `gamemaker_version`, `Sprite_Class`, `Room_Class`, `room_speed`, `sprite_index`, `D3DX8.dll`.
- No separate .gmk/.gm81 project or source files were provided.

## Inferences, NOT confirmation
- Strong indication of classic GameMaker runner. **GameMaker 8.x is still a hypothesis**, not exact identified version.
- Overlay may include game resources; its actual format/compression/encryption and recoverability remain unknown.
- DirectX 8 marker suggests a relevant dependency; imports and real runtime API usage still require separate inspection.

## Untested
- Exact runner version, resource counts, GML recovery, integrity of game data, Win32/D3D8/D3D8 helper/audio/input requirements, Winx86/Box86 support, OpenGMK compatibility, gameplay reconstruction, Vita performance/controls/saving.
- No recovery or compatible runtime has been demonstrated and **no VPK exists**.

## Repeatable local baseline

```powershell
python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip
```

Outputs sanitized structure/hashes to stdout; it does not extract or launch the EXE. Follow up by inspecting PE imports and determining the actual GameMaker runner build; record a separate experiment for each tool attempt.
