# E021 — original startup through priority and persistent INI services

**E022 follow-up:** [sound_replace now actually decodes/registers the original MP3 on PC/Vita](OPENGMK_MP3_PROBE.md), superseding the current audio-replacement gate below while preserving E021 evidence. Existing profile retained byte-for-byte; original VM reaches Game::draw (65 instructions on that profile). Native stop is clear_zbuf before object Draw/presentation; native audio output is still unavailable, not represented by a fake playing handle.

**2026-11-25 UTC / 2026-11-24 America/Bogota. VERIFIED:** PC and physical Vita 1000 execute **38 original VM instructions / 28 traced service calls**, passing E020's 15-instruction priority gate and the subsequent real file/INI requests. Native execution stops at **`Audio/sound_replace`**, exit **2**. Installed **HOWAW1178 / 00.22** SELF, persisted log and saved INI independently verified. **No original menu frame or playable/functional game VPK exists.** E020's backend and original assets/GML remain unchanged; its logo fixture was removed from this diagnostic.

## Priority: procedure completion is not scheduler success

**VERIFIED static:** the reviewed original procedure at `0x56a5d8` calls process-class and current-thread setters in that order, does not test their returns, and never writes its caller-supplied GML result slot. E019's exception on unavailable priority was a deliberately strict diagnostic boundary, not established original-runner failure behavior.

**VERIFIED bounded execution:** `priority_failure_contract.c` loads only the **246-byte reviewed procedure**, SHA-256 `0b30b33d3350705161ee6222311935c170a0300c5741f94521e1b11d10053002`, in its own x86 child. Hash/bounds/relocation guards precede execution. Both imported setters are routed to the actual Windows APIs with NULL handles, producing **ERROR_INVALID_HANDLE / 6**. For each real game argument **0, 1, 2**, both calls execute once and the GML result slot remains unchanged. The original EXE entrypoint/runner is not launched. The fixture supplies an integer-only conversion helper; arbitrary fractional conversion, whole-runner execution and other priority arguments are outside this test.

The adapter therefore records **two independent effects** and completes the GML procedure with the existing VM default value, which is **not a success flag**. Vita records `process=Unavailable thread=Unavailable`, explicitly states that no equivalent scheduling change was made, and continues. It does not invent a Vita priority mapping or report an applied effect. Windows executes both real calls even if the first fails, records their actual errors/effects and reads back current priorities. This supersedes only E019's priority error boundary; it does not authorize success stubs for audio, graphics or files. High/button 3 remains the separately logged owner dialog policy.

Primary references: [original GM8 manual, mirrored](https://documentation.help/Game-Maker-8/403_11_misc.html), [Windows SetPriorityClass failure contract](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setpriorityclass). The manual alone does not establish failure behavior; the reviewed procedure and bounded failure test supply that evidence.

## Real file/INI operations

`file_exists`, `ini_open`, `ini_close`, string/real reads/writes and key/section existence reuse existing argument conversion and INI behavior, including E015's write-through fix. Writes and close synchronize the actual file; errors propagate. A directory is not a file, missing entries use the original supplied defaults, and no file is manufactured by an existence query.

Logical INI names resolve into a stable **`e021-profile/` beside the copied EXE**; on Vita this is `ux0:data/howaw/e021-profile/`. Other permitted relative existence queries address the unchanged asset directory. Original saves/data are not overwritten or migrated. Drive-qualified, absolute, parent-traversing and NUL-containing GML paths explicitly block until a mapping is justified. The actual startup uses a relative INI name and passes this mapping. These bounds are not claimed as complete Windows filesystem compatibility; case/encoding/error parity beyond the tested calls remains open.

**PC PASS:** missing file, directory rejection, missing-key default, real/string write-through and reopen, path rejection, and write/close failure with a missing parent. The explicit fixture uses its own files and does not execute synthetic GML or advance the original VM counter. A second process reuses the actual game INI without rewriting it: SHA-256 unchanged, **27 instructions / 17 calls**, same audio stop. That process also applies Windows High and verifies `(128,2)`. First-run native-policy mode instead logs both effects unavailable and executes 38 instructions. Different counts reflect the original first-profile branch.

## Where execution stops, and the real menu path

**VERIFIED dynamic:** `Game::init` enters the first original room through unchanged `load_room`. **VERIFIED static:** the recovered-code inventory's sole `sound_replace` call is in original object **1**, Other event **2 / Game Start**. **INFERRED correlation:** the service trace and unique call site locate the current stop in that event. This corrects the initial PC interpretation that it stopped before room loading. Object Create processing, Game Start, room creation and room-start processing precede the engine's first automatic Draw; reaching room loading is not a rendered menu.

The blocked request is replacement of sound **140** from the actual **`Music/menu.mp3`**, kind **3**, preload **true**. No audio decode, loaded handle or playback success is reported. The current sound representation is **Deferred**, not a successfully decoded sound. Simply enabling the desktop `sound_replace` body would be unsafe: its non-None branch can clear an existing sound and return 1, while Deferred only means pending original bytes. Do not use that branch to fabricate native replacement success.

`Game::init` still attempts the original startup flow and propagates this real error. Calling `game.draw()` after it failed would bypass required initialization and would not establish the original menu; this diagnostic does not do that.

| Next graphics requirement | Evidence / present status |
| --- | --- |
| Pre-Draw readback coupling | `load_room` currently calls `get_pixels` before testing whether an FFmpeg recorder exists. After the audio gate, distinguish a real recording requirement from this unused readback; do not supply invented pixels. |
| Viewport and presentation | Original first room 640×325, speed 30; `draw_view` first calls `set_view`, then clears depth/colour. E020's fixed 960×544 presentation needs actual view/framebuffer integration. |
| Rectangles / gradients | Original menu object 0 has 84 rectangle and 55 coloured-rectangle call sites. Unsupported in E020. |
| Text | 100 `draw_text` sites, 29 font-setting sites; retain original engine glyph drawing, add the required state/view support. |
| Sprites/backgrounds | 106 sprite + 82 sprite-ext sites; tiled background and three ordinary background sites. Reuse E020 texture/batch path. |
| Blending | Two menu blend-setting sites; real state changes/flush ordering required. |

Counts are **static menu-object call sites**, not operations reached in E021 or complete transitive script coverage. Game Start currently blocks before Draw requests. No speculative backend functions were added: all four E020 backend files are **byte-identical**. This prevents an isolated replacement renderer and avoids spending GPU memory before the real flow requests graphics.

The later window-title call is also still an explicit frontend boundary. Resolving audio alone therefore does not imply that viewport, readback, window or presentation already work for the original menu.

## Physical result and memory

Owner installed/launched 00.22 and observed opening followed by closure without an image. Retrieved/validated **2026-11-25 02:41:32 UTC**. The log confirms **38 instructions**, owner High policy, two unavailable priority effects, INI existence **false → true**, real writes/readback, then `sound_replace: SERVICE_UNAVAILABLE/Audio`. **No panic/allocation-failure marker; exit 2 is the planned service stop.** Model: same owner Vita 1000 as E019/E020; firmware unreported.

The post-exit INI is **152 B, two sections / ten keys**, SHA-256 `c02d3b0c610bd3d95f56e6e1c8f059108fa92811a652522d1c032ff3f4bf3018`. Its parsed contents equal the PC-generated 165-byte file; platform line endings account for the byte difference. This verifies native durable output after exit; a second native-process read is **UNTESTED**. PC restart read is separately verified.

| Native boundary | Measured result |
| --- | --- |
| Requested Rust live heap at stop / lifetime peak / exit | **94,021,738 / 108,104,996 / 1,130 B** |
| CPU texture payload / GPU texture allocation / uploads | **71,602,980 B / 0 B / 0** |
| Sprite submissions / batches / frames | **0 / 0 / 0**; no repeated logo test |
| System free user / CDRAM / physical-contiguous at stop | **124,780,544 / 117,440,512 / 27,262,976 B**; each query rc=0 |
| Original startup interval | **2,309,970 µs**, including actual INI synchronization and diagnostic I/O; not gameplay FPS |

No GXM initialization or simultaneous six-atlas upload occurred. E020's measured residency limit remains relevant after startup is unblocked. Rust request counters exclude C allocations/allocator overhead/stack/GPU; system-free pools are separate, non-additive measurements. No full-game memory-fit claim.

## Reproduction, failures and preserved evidence

Existing offline Rust/Cargo **1.100.0**, Python **3.14.4**, x86 MSVC toolset **14.50.35717**, WSL VitaSDK hard-float GCC **15.2.0**; no installation/download. Reuse E020's private Rust homes, scalar/no-LTO/no-strip environment, WSL linker and **unchanged** `build/graphics20-native-v2` archives. Pinned upstream `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`. Original ZIP/EXE/MP3/GMK/GML and E015/E020 artifact hashes rechecked unchanged; no decompilation/recovery repeated.

```powershell
python tools/opengmk/prepare_menu_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/menu21-20261124/OpenGMK
cl /nologo /W4 /O2 tools/opengmk/menu/priority_failure_contract.c /Fe:build/menu21-priority-contract.exe /Fo:build/menu21-priority-contract.obj
build/menu21-priority-contract.exe private/menu21-20261124/priority-reviewed.bin
cargo build --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --manifest-path local-tools/menu21-20261124/OpenGMK/Cargo.toml
python tools/opengmk/run_vm_probe.py --runtime build/menu21-host/i686-pc-windows-msvc/release/howaw-vm-probe.exe --input-dir recovered/native-probe-20261123/pc-profile --run-name startup-final --experiment menu21-20261124 --owner-dialog-high --native-priority-contract --files-contract --expected-service Audio --expected-operation sound_replace --require-persistent --diagnostic-prefix e021
cargo check --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --lib --manifest-path local-tools/menu21-20261124/OpenGMK/Cargo.toml
cargo build --offline --locked --release -Z build-std=std,panic_abort --target armv7-sony-vita-newlibeabihf -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --manifest-path local-tools/menu21-20261124/OpenGMK/Cargo.toml
```

Use fresh output directories. C fixture input is the private reviewed slice from the hash-verified EXE; it is never committed. Exact environment/wrappers and extraction evidence stay private. **PASS:** failure contract 3/3; actual file/INI fixture; PC restart/readback; desktop check **29.24s**; ARM first build **1m20s**; VELF conversion; reuse **22/22**; fresh preparation **197/197**, E020 backend **4/4 identical**, unchanged lockfile. Final host build **47.21s** after hardening/fixture additions.

**Failures retained:** first host build had an extra generated brace; second exposed a moved input path, corrected without copying game buffers. Third passed **37.46s**; fourth added filesystem contracts/desktop preservation and passed **39.98s**; final added exact request/timing diagnostics. The first C fixture assertion rejected an incorrect switch-table relocation offset **before execution**; corrected checked offset passes. Discovery launcher expected `sound_add`, but captured `sound_replace`: its expectation check failed, while persistence/progress succeeded; captured evidence was reassessed without repeating that run. Initial FTP connection timed out until owner re-enabled VitaShell.

Package uses SDK `vita-elf-create INPUT.elf OUTPUT.velf`, then `package_priority_probe.py --prepare --experiment E021 --elf INPUT.elf --velf OUTPUT.velf --output build/menu21-device` and `--package --experiment E021 --output build/menu21-device --title-id HOWAW1178 --app-version 00.22`. Only SELF/SFO, CRC/identity verified; original EXE/MP3 remain separate private data. ELF **4,726,100 B**, SHA-256 `84968e0a1795cc2e6d2a544dbcb31098bdae12bb424900f4680be3fa54c6ab3f`; VELF **5,578,542 B**, `2179374e4987dac2ac19847b5ba62d04611b100dcf45655a4c98b3da1ca250af`; VPK **2,281,341 B**, `02b9d6b2eeb00837c25dcad10474857c1e27bc7cc1df2d4977297832131ce9a1`. Installed SELF `fbdf711f8185fba18e28e8cb91de2e230eecefd8d2e2a8091f7e22e51d06abb5`; device log `5ef888ca3e1625f84fd166bd8b5cb2fbf4b5419438441e4f59ff543e7b3caeb2`.

Evidence: ignored `reports/local/menu21-20261124/` build attempts, guarded failure test, startup/fixture/restart captures, source/renderer audits, package/upload, device log/installed SELF/SFO and saved profile. New source/builds under `local-tools/menu21-20261124/` and `build/menu21-*`; older artifacts preserved. **New recovered resources: zero**; prior 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms preserved.

**Result:** PASS priority failure semantics and real persistent startup files on PC/Vita; BLOCKED native audio replacement, first original menu Draw and gameplay. Route B with the unchanged E020 libvita2d/GXM backend remains best supported. **Next one high-information experiment:** prove real ARM MP3 decoding/handle registration for the existing menu file, measure its memory, then adapt `sound_replace` with correct Deferred/None ownership and failure results. Only actual supported replacement may report success; subsequent original Game Start/room/Draw requests will determine the next service. No partial-init draw or fake audio handle.
