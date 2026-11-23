# Technical audit — session 2026-11-22 local / 2026-11-23 UTC

**Scope:** VERIFIED archive/PE inspection, project recovery, independent project inventory, the initial failed OpenGMK launch, a successful modified-runtime PC menu trial and a host-only WinVita loader probe. No original Windows runner execution, ARM game execution, Vita build or device test. Detailed attempts: [EXPERIMENTS.md](EXPERIMENTS.md), E001–E014.

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

## Runner identification — VERIFIED version 8.0, patch build unknown

Independent of marker strings, `tools/inspect_pe.py` found the standard GameMaker **8.0** loading/check sequences used by [OpenGMK's format detector](https://github.com/OpenGMK/OpenGMK/blob/master/gm8exe/src/gamedata/gm80.rs):

| File offset | Observed evidence |
| --- | --- |
| `0xA49BE` | Standard 8.0 load sequence; following comparison checks magic `1234321` |
| `0xA49E2` | Version comparison checks `800` with intact conditional branch |
| `0x144AC0` | Header search pointer `0x1E8480` |
| `0x1EAB90` | Magic `1234321`, version `800`; reached after one 10,000-byte search step |

GM8Decompiler 2.2.0 independently recognized 8.0 and strictly parsed the game data without `--lazy`. This establishes the **8.0 format/runner family**, rather than 8.1. **UNTESTED:** an exact vendor patch/build beyond 8.0; no reference-runner byte comparison was available. The PE's `1.0.0.0` application version is not a runner version.

## Windows/DirectX surface — VERIFIED static dependencies

The main EXE has **26 import descriptors, 535 entries, 496 unique DLL/symbol pairs across 17 DLLs**. Repeated descriptors and duplicate entries are retained in the private report. WinVita's independent loader produced the same totals. `SizeOfImage` is 3,584,000 bytes; this is not the game's resident memory usage.

| DLL | Unique symbols | Evidence / implication |
| --- | ---: | --- |
| kernel32.dll | 119 | File/process/memory/thread/time functions, `LoadLibraryA`, `GetProcAddress` |
| user32.dll | 196 | Windows messages, controls, keyboard/mouse, dialogs |
| gdi32.dll | 93 | Windows graphics/font/bitmap operations |
| comctl32.dll | 23 | Common controls |
| ole32.dll / oleaut32.dll | 13 / 13 | COM/OLE infrastructure |
| winmm.dll | 8 | `timeGetTime`, `sndPlaySoundA`, `mciSendStringA`, `mciSendCommandA`, `mciGetErrorStringA`, `joyGetPosEx`, `joyGetPos`, `joyGetDevCapsA` |
| advapi32.dll | 7 | Windows services/registry surface; live use unmeasured |
| shell32.dll | 5 | Shell surface |
| comdlg32.dll / winspool.drv / wsock32.dll | 4 / 4 / 4 | Dialogs, printing; Winsock startup/cleanup and host-name lookup |
| version.dll | 3 | Version queries |
| d3d8.dll / ddraw.dll | 1 / 1 | **`Direct3DCreate8` / `DirectDrawCreate`**, real import-table entries |
| msimg32.dll / mpr.dll | 1 / 1 | Additional Windows surface |

Imports establish load/link requirements, not how frequently gameplay uses each API. COM graphics calls through vtables are not counted as named imports. No delay-import directory was present. `DSound.dll` and `DPlayX.dll` occur as literals: **INFERRED dynamic candidates**, not proven calls.

**VERIFIED embedded helper:** the data contains a zlib-compressed `D3DX8.dll` block at `0x1ED52B` (267,324 bytes). Inflation produced a 495,616-byte PE32 x86 DLL, SHA-256 `edfc5f86be36c2c509e4ad6ba3742bb5b2429a56de805a99771e24fec62b076a`, importing KERNEL32/USER32/GDI32. Neither this DLL nor its code is public. Dynamic graphics/helper call coverage remains UNTESTED.

## Recovery — VERIFIED structural success, fidelity not yet established

GM8Decompiler 2.2.0 (`#fb6d4d57`, built 2024-02-12) wrote a 15,998,859-byte GMK, SHA-256 `854d2644d3c2c22eabd8b3acc99e021f630d17d9fbf37faeac4519fa6a86e9c9`. Deobfuscation was disabled and broken-event preservation enabled. It is a reconstructed project, not proof of byte-identical editor source.

Gmk-Splitter 0.21's LateralGM reader independently parsed that GMK. Its standard tree export **failed on a duplicate sprite name**; the original/recovered project was not renamed or repaired. An ID-based audit used the same reader without its filename export layer:

| Resource | Existing entries VERIFIED | Table slots, including holes |
| --- | ---: | ---: |
| Sprites | 693 | 755 |
| Sounds | 128 | 141 |
| Backgrounds | 101 | 111 |
| Scripts | 181 | 200 |
| Objects | 233 | 264 |
| Rooms | 15 | 22 |
| Fonts | 7 | 9 |
| Paths | 1 | 3 |
| Timelines / triggers / constants | 0 / 0 / 0 | 0 / 0 / 0 |

Also VERIFIED: **845 object events, 875 actions, 2,120 sprite frames, 3,917 room instances, 8,123 room tiles**, room-order length 15, one included file and zero extensions. Initial decompiler “Writing N” totals count slots, not existing resources. Live-resource log counts agree with the independent reader.

Sprite pixel arrays alone total 27,451,468 RGBA bytes: a decoded-data count, **not** runtime RAM/VRAM or a Vita memory-fit result. Collision masks, font rendering, all script semantics and audiovisual fidelity have not been compared against the original runner.

The included **`CleanMem.dll`** is 1,024 bytes, PE32 x86, SHA-256 `dac23ed1af08cb7409a18dc09b0c35230e1b314ff49711394c66bd69ae86548c`. Its imports are `GetCurrentProcessId`, `OpenProcess`, `CloseHandle`, `EmptyWorkingSet`, `GetProcessMemoryInfo`. Recovered startup logic calls its two exports before the priority dialog. **INFERRED:** a small native OS adapter is needed on Vita; an x86 DLL cannot be loaded natively by an ARM OpenGMK port. Its result values were not instrumented in the PC trial.

## Initial OpenGMK PC trial — E007 FAIL before menu (retained)

Local GM8Emulator 0.2.0 read the unmodified copied EXE in strict mode and created an AMD OpenGL 3.3 context. It then panicked at `gm8emulator\\src\\gml\\kernel.rs:6609:9`: **`Called unimplemented kernel function show_message_ext`**. Recovered startup logic uses this builtin for a three-choice process-priority dialog. No game source was patched to bypass it.

- **VERIFIED working:** gamedata parsing, graphics-context initialization, execution reaching original startup GML.
- **VERIFIED failing:** `show_message_ext` in this local runtime.
- **UNTESTED:** visible menu, sprite animation, collisions, player controls, enemies, weapons, audio, arena progression, saving and timing. No game window remained when UI enumeration ran. Numeric process exit code was not captured.

The inspected upstream [kernel source](https://github.com/OpenGMK/OpenGMK/blob/master/gm8emulator/src/gml/kernel.rs) also leaves `show_message_ext` unimplemented; merely repeating the same launch or assuming a newer binary fixes it is unjustified.

## Modified OpenGMK PC trial — E014 PASS for real menu and interaction

**VERIFIED:** official source commit `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`, built in a separate private working copy, with a bounded Windows `show_message_ext` implementation. Original EXE, music and recovered GMK hashes remain unchanged. No GML call was removed or replaced. Cargo.lock is unchanged; this source build is distinct from E007's older packaged runtime.

The native modal backend respects three custom buttons, return values 1/2/3, Escape/close=0, synchronous pause and input cleanup after dismissal. A standalone real-window probe tested mouse selections 1 and 2, Tab/Enter selection 3 and Escape 0 before launching the game. The game and fixture used the same backend bytes. Native visual styling and held-input edge cases are not claimed identical to the original runner.

**Observed working:** original startup priority dialog, logo/title sequence, welcome, first-run player configuration, Save Changes, real main menu, Firefight map selection and difficulty selection. Real keyboard and mouse input drove these transitions. Alt+F4 ended with exit code 0; no further runtime error was observed along this route. Audio was not verified by listening, and configuration persistence after restart was not tested.

Rust/Cargo were installed locally because absent; existing MSVC/Windows SDK/CMake/Ninja were reused. One build failed on MSBuild tracking-file paths; a new shorter build path with existing Ninja succeeded. Exact source/build/binary identities, controlled-test output and private screenshots are recorded in [OPENGMK_PC_PROBE.md](OPENGMK_PC_PROBE.md) and E011–E014. **This is a Windows PC menu proof, not an ARM/Vita or combat proof.**

## D2Vita / newly supplied WinVita — partial evidence for route A

**VERIFIED locally:** D2Vita's `VERSION` is 0.2.3. Its archived `third_party/winx86` directory is empty. The subsequently supplied **WinVita** tree contains the PE loader, bridge, Box86-derived ARMv7 dynarec, shims and DirectSound code. Its CMake project version is 0.1.0; no source commit ID was supplied. Local README claims of “no prewritten shims” are superseded by actual shim source files in this snapshot.

The isolated **host loader probe PASS** mapped the exact EXE at entry VA `0x588750`, with 535 imports and 496 unique pairs. **No bridge linking, guest instruction, ARM execution or display was tested.** The original file must remain accessible for the runner's overlay reads.

Concrete static gaps:

- No D3D8/`Direct3DCreate8` implementation was found in the supplied WinVita `src/`; a D3D8 COM/device/texture/draw/presentation adapter is needed. D2Vita's Glide renderer is not a GameMaker renderer.
- WinVita `win32_shims_misc.cpp` registers `DirectDrawCreate` to return fixed error **`0x80004005`**. A matching name is therefore not graphics support.
- No `mciSendStringA`/`mciSendCommandA` implementation was found there. DirectSound code exists, but that does not establish GameMaker sound/music compatibility.
- Delphi/Win32 UI, exceptions/TLS, dynamic DLL resolution and the CleanMem helper need execution evidence; source components alone do not establish compatible semantics.

Name-only comparison: D2Vita's documented combined engine/game table matches **226/496** imports (270 absent). WinVita runtime-source registration candidates match **128/496** (368 absent). These are different scopes, not contradictory measurements or pass rates; neither checks execution, conditional installation or correctness. Full local lists are private.

**INFERRED effort:** A requires multiple large workstreams (Win32 behavior, D3D8, audio and guest execution), likely a multi-month engineering project for one experienced developer; this is a planning range, not a measured schedule. B has a smaller demonstrated PC blocker, but a native Vita backend and ARM extension adaptation remain substantial and unmeasured. No FPS estimate is supported. See [DECISIONS.md](DECISIONS.md).

## Remaining gates

Exact vendor patch/build, PC combat/parity, native ARM runtime/backend portability, renderer fidelity, memory/frame pacing, Vita input/scaling, audio output, suspend/resume and save persistence remain UNTESTED. PC main-menu interaction is now VERIFIED. **No functional VPK exists.** No title ID was selected or package generated.

## Repeatable local baseline

```powershell
python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip
```

This command does not extract or launch the EXE. Further repeatable commands and private evidence paths are in [EXPERIMENTS.md](EXPERIMENTS.md). Original inputs and all recovered data remain ignored and local.
