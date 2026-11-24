# E016 — persistence and first native ARM feasibility probe

**E017 follow-up:** [The actual compiler/VM now also build/link for ARM](OPENGMK_VM_PROBE.md); original startup executes on PC until CleanMem external binding is explicitly blocked. This supersedes E016's compiler/VM build absence, retaining its historical failures. ARM execution remains untested.

**2026-11-23 local / 2026-11-24 UTC.** VERIFIED: profile persistence on PC; real OpenGMK reader/parser compilation and ELF → VELF conversion for Vita. **Full interpreter/game execution on ARM is BLOCKED**, not demonstrated. No functional VPK exists and none was generated. Base `main` was `3925148`; the remote main hash matched before changes.

## PC persistence and audio

Reused E015 runtime `5d8f24087ad253952910964a967cccf9a4ad9939769c202ee859629cf0253f6e`. Copied the previous run's EXE, music and INI into a new private directory; previous files remain untouched. Real UI input selected EVA helmet (`Helmet=3`) and Elite (`Race=1`), then Save Changes. Process 2876 exited normally with code 0 at `2026-11-24T02:22:07Z`.

A new process, 12476, started at `02:23:02Z`, using the same saved game directory and a **different empty process-local temp/profile directory**. It displayed Elite. Switching the unsaved preview to Spartan and opening Helmet showed **EVA Equipped**. Alt+F4 closed this process with code 0 at `02:27:19Z`. The saved INI hash remained `41d5ca4cfbf68461a3f2072826da129d242d1b344304f7f9e4bd2c4f591410e2` before/after restart and final close. **PASS for these profile selections/settings**; this does not test every save/INI edge case. No further adapter or GML correction was needed.

Audio remained unchanged, with diagnostics enabled and default latency. Run 1 ended with **0 underrun notifications**, maximum reported callback CPU duration 781 μs; run 2 ended with **744**, maximum 602 μs. A five-second process-specific meter in run 2 confirmed nonzero signal. Concurrent compilation/startup and different workloads prevent a causal comparison. **VERIFIED recurrence of underrun notifications; audible cut duration/cause and continuity remain UNTESTED in this session.** No listening claim, speculative buffer tweak or audio patch is adopted. E015's earlier recovery tests were not repeated.

Exact PC launches, repeated with `N=1,2` and their separate temp/report directories:

```powershell
python tools/opengmk/run_pc_probe.py --runtime build/ap/i686-pc-windows-msvc/release/gm8emulator.exe --game-dir recovered/native-probe-20261123/pc-profile --report-dir reports/local/native-probe-20261123/pc-N --temp-dir recovered/native-probe-20261123/temp-N --audio-diagnostics
build/arena-probe-20261122/audio_session_meter.exe 12476 5
```

## What actually compiles

Upstream source is unchanged commit `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`. A fresh ignored source copy adds only a diagnostic workspace member. Original game input is read as data; no original EXE process, GML rewriting, embedded game asset or fictional room is used.

| Component | VERIFIED result / boundary |
| --- | --- |
| Rust `core`, `alloc`, `std`, panic support | Built for `armv7-sony-vita-newlibeabihf`; final native link and relocation conversion PASS. API/device behavior not tested. |
| `gm8exe` 0.2.0 | Real strict PE/GM8 reader compiles for ARM and is used by the linked diagnostic. |
| `gml-parser` 0.2.0 | Lexer/AST parser, including `runner-serde-derives`, compiles for ARM. Parsing is not executing GML. |
| Independent emulator modules | Unchanged `math.rs` (`Real`), `gml/rand.rs` and `render/atlas.rs` typecheck for ARM. Atlas code is exercised by the diagnostic on host; unused math/RNG code may be removed by the optimizer. |
| Dependencies | byteorder 1.5.0, serde 1.0.228, rect_packer 0.2.1, getrandom 0.2.17, flate2 1.1.9, miniz_oxide 0.8.9, rayon 1.10.0 / rayon-core 1.12.1 compile in this ARM probe. Rayon workers and entropy API behavior were not exercised on Vita. |
| Whole `gm8emulator` | FAIL/BLOCKED: `clipboard` selects X11 for Vita's `cfg(unix)`; xcb 0.8.2's build script uses host `std::os::unix`/`MetadataExt::mtime`, unavailable on Windows. Compilation stopped there; downstream success is not claimed. |

The [Rust target documentation](https://doc.rust-lang.org/rustc/platform-support/armv7-sony-vita-newlibeabihf.html) classifies Vita as Tier 3, with no distributed precompiled std and partially supported APIs; process spawning is unsupported. Local matching Rust source confirms Vita filesystem/pthread branches. Native std compilation is **not** proof that all its APIs work on device. Use serial game loading initially (`from_exe(..., true, false)`); std's source default minimum worker stack is 2 MiB, relevant to a future Rayon/thread budget.

## Retained failures and concrete corrections

1. Offline ARM build BLOCKED: missing `rust-src`/std dependency cache. Added missing `rust-src` and std dependencies to the existing private Rust 1.100.0/Cargo 1.100.0 installation. No Rust/SDK reinstall was needed for the experiment.
2. Default ARM build FAIL: simd-adler32 0.3.9 enables ARM NEON intrinsics without the required unstable feature gate. **Scalar research build PASS** with `RUSTFLAGS=-C target-feature=-neon`. No speed claim; a crate-specific fix/validation can replace this conservative switch later.
3. First executable link FAIL: Windows GCC could not open very long LTO-generated object paths. `CARGO_PROFILE_RELEASE_LTO=false` exposed the next error. Failed build artifacts/logs remain.
4. Windows SDK link FAIL: SDK is soft-float; Rust target objects use VFP arguments/hard-float. Reused **existing WSL hard-float SDK**, GCC 15.2.0, built `2026-05-24 12:26:53`, newlib `fbb8375870d799758e0b4358d2f1708781aa26a6`, vita-toolchain `71f3789342f610a4eb3ba50fc33292c4900c6666`. No SDK was installed or modified.
5. WSL link FAIL with upstream `strip=true`: linker reported `final link failed: invalid operation`. `CARGO_PROFILE_RELEASE_STRIP=none` produced a valid ELF. [cargo-vita documents the relocation requirement and incompatibility of symbol stripping](https://github.com/vita-rust/cargo-vita#notes).
6. Whole-runtime check initially BLOCKED offline by missing num_threads 0.1.7. Fetched only the missing target dependencies (num_threads, x11-clipboard 0.3.3, xcb 0.8.2); retry FAIL at xcb as above. Did not patch X11 into a fake Vita backend or repeat the unchanged failure.

**Tooling incident:** an initial version query invoked rustup before private-home variables were set and automatically installed/synchronized an unnecessary default stable toolchain outside this checkout. This was an error, not a project requirement. No external cleanup was attempted; subsequent commands explicitly used the existing private homes. This session therefore cannot claim zero downloads or zero external toolchain writes.

`cargo-vita` was absent from the checked Windows private/global paths and WSL executable paths. It is a build/package wrapper, not a replacement backend. The direct Cargo build below tests its underlying native compilation/link path; installing this wrapper or another Rust toolchain was unnecessary. [Upstream recommends nightly](https://github.com/vita-rust/cargo-vita#usage); this bounded experiment uses existing stable plus process-local `RUSTC_BOOTSTRAP=1` for `build-std`, without claiming a supported stable release workflow.

## Reproduce the useful probe

`prepare_native_probe.py` requires a pristine checkout at the stated source revision and a **new** output directory under ignored `local-tools/`. It copies source, adds the harness, and preserves upstream dependency versions; Cargo.lock gains only the probe entry (hash `472e2e0dccb09004ae83e1a3711e45094389e5e72788491b85f420288142df12`). No third-party source is committed here.

```powershell
python tools/opengmk/prepare_native_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/native-probe-20261123/OpenGMK
$env:RUSTUP_HOME=(Resolve-Path local-tools/menu-probe-20261122/rustup).Path
$env:CARGO_HOME=(Resolve-Path local-tools/menu-probe-20261122/cargo).Path
$env:RUSTUP_TOOLCHAIN='stable'
$env:RUSTC_BOOTSTRAP='1'
$env:CARGO_TARGET_DIR=Join-Path (Get-Location) build/arm16-scalar
$env:RUSTFLAGS='-C target-feature=-neon'
$env:CARGO_PROFILE_RELEASE_LTO='false'
$env:CARGO_PROFILE_RELEASE_STRIP='none'
New-Item -ItemType Directory -Force $env:CARGO_TARGET_DIR | Out-Null
@'
@echo off
python "%~dp0..\..\tools\opengmk\vita_wsl_link.py" %*
'@ | Set-Content build/arm16-scalar/wsl-link.cmd
$env:CARGO_TARGET_ARMV7_SONY_VITA_NEWLIBEABIHF_LINKER=(Resolve-Path build/arm16-scalar/wsl-link.cmd).Path
$env:PATH="$env:CARGO_HOME/bin;$env:PATH"
& "$env:CARGO_HOME/bin/cargo.exe" build --offline --locked -Z build-std=std,panic_abort --target armv7-sony-vita-newlibeabihf --release -p howaw-native-probe --manifest-path local-tools/native-probe-20261123/OpenGMK/Cargo.toml
```

The successful ELF is **1,212,932 bytes**, SHA-256 `57d46b6b64c2d378440311473eecfd314051eab18d8ca8b8f503a1998474178f`. `arm-vita-eabi-readelf -h -A` verifies ELF32 ARM EABI5 hard-float / Thumb-2, VFP register arguments. SDK code can still contain NEON; the scalar flag disables the problematic Rust crate path.

Using the existing WSL hard-float SDK, run `vita-elf-create INPUT.elf OUTPUT.velf` (WSL paths required). **Exit 0**, VELF **1,374,246 bytes**, SHA-256 `4450a172b21c872e6bf58089aa3964b212eb8c11e04d772ac1b14e1a2feb3093`. Readelf and conversion logs are private. No title ID, fself/VPK packaging, installation, boot or Vita execution occurred.

The same harness built offline for i686-pc-windows-msvc using the existing MSVC developer environment. Command: `cargo build --offline --locked --release --target i686-pc-windows-msvc -p howaw-native-probe --manifest-path local-tools/native-probe-20261123/OpenGMK/Cargo.toml`, with target directory `build/native16-host`. Run:

```powershell
build/native16-host/i686-pc-windows-msvc/release/howaw-native-probe.exe recovered/native-probe-20261123/pc-profile/HOWaW_FirefightDemov1.exe
```

**PASS, exit 0:** strict GameMaker 8.0 load; 693 sprites, 128 sounds, 101 backgrounds, 181 scripts, 233 objects, 15 rooms, 7 fonts. **1,073 nonempty GML units parsed, zero syntax failures**, including 179 nonempty scripts and original event/room/instance/library code; 603,129 source bytes, 5,622 top-level statements. This is original-data loading/syntax parsing on PC, **not bytecode interpretation on ARM**. ARM diagnostic expects a private copy at `ux0:data/howaw/HOWaW_FirefightDemov1.exe`; its execution is BLOCKED pending a device environment and native host integration. No game data is embedded in ELF/VELF.

## Memory evidence and estimate

| Original data / host diagnostic | Bytes | Meaning |
| --- | ---: | --- |
| Sprite RGBA frames | 27,451,468 | VERIFIED payload |
| Background BGRA | 43,569,908 | VERIFIED payload, previously not counted in sprite-only estimate |
| Collision bool arrays | 2,668,863 | VERIFIED payload |
| Encoded sound files | 13,460,384 | VERIFIED; not a promise of decoded audio/cache footprint |
| Font alpha maps | 105,344 | VERIFIED; excludes rendered default font |
| Above payload total | 87,255,967 (~83.2 MiB) | Data count; excludes container/code/instance overhead |
| Reader peak requested Rust heap | 108,104,832 (~103.1 MiB) | Measured in 32-bit Windows harness, includes EXE buffer; excludes allocator overhead, direct C allocations, stack/GPU |
| Sprite/background atlas at 2048 | 83,886,080 (80 MiB), five pages | Unchanged CPU packer; all 2,221 images fit, zero rejected. No GPU allocation test. |

**INFERRED budget pressure:** retaining all decoded image bytes (~67.7 MiB) while allocating those atlas pages could temporarily exceed 147 MiB for image payload plus texture capacity alone. Add collision/audio, GML/objects/instances, std/thread heaps, font/particle atlases, GPU alignment and surfaces. At design resolution 960×544, one RGBA32 color plane is ~1.99 MiB; a same-size 32-bit depth plane doubles that. These are arithmetic estimates, not Vita usage. Upstream upload discards CPU image staging afterward; measure the peak and investigate upload/release ordering before reducing fidelity. The probe atlas excludes fonts, built-in particles/white pixel, dynamic surfaces, mipmaps and render targets. No Vita RAM-fit or FPS result is supported.

## Concrete adapter work and first native prototype

| Boundary | VERIFIED source obstacle → INFERRED implementation plan |
| --- | --- |
| GML core / frontend | Reader/parser are separate crates; compiler/runtime/kernel depend directly on `Game`, which owns `ramen::Window`, renderer and audio. Preserve compiler/VM/actions/collision/room code; introduce platform services and feature-gate desktop UI/recording. There is no already independent full interpreter crate to claim portable. |
| Window / dialogs / input | ramen `ef715f6` implements Windows/Linux only. Vita is Unix but not Linux. Replace its frontend references with a Vita host and feed existing virtual-key/mouse state from pad/touch/analog; preserve key-press/release and dialog results 1/2/3/cancel 0. Draw real modal choices, pause stepping and clear held input. Mapping, scaling and deadzones require device validation. Remove X11 clipboard from Vita dependencies; offer an explicit supported local text-entry path where actually needed. |
| Graphics | Existing `RendererTrait` is a useful seam, but constructor/context are desktop-coupled. GL 3.3 core, GLSL 330/std140 UBOs, VAO/VBO, FBO/readback and GLX/WGL are real dependencies. Implement a Vita renderer under that trait; validate original sprite batching, alpha/blend, fonts, clipping, surfaces/readback and room scaling. Installed vitaGL headers declare UBO/VAO/blit APIs but **lack `glGetTexImage`**, used upstream. API declarations are not semantic support. [vitaGL supports a subset and describes experimental GLSL UBO translation](https://github.com/Rinnegatamante/vitaGL); shader compatibility/build flags are UNTESTED. Test exact engine shaders or adapt their backend representation; retain a direct GXM backend as a fallback. Check shader-compiler availability/licensing before selecting a runtime dependency; no mandatory kernel plugin adopted. |
| Audio | Keep existing mixer, WAV/MP3 player/resampling semantics. udon currently opens libsoundio; its supplied C backend has no Vita output driver. Add sceAudioOut or existing SDL2 output at the sink, with measured queue/underrun behavior. C/C++ decoder portability and hardware streaming remain UNTESTED; do not silence or replace original sound calls. |
| Files / externals | Use explicit `ux0:data/howaw/` save/temp roots and packaged read-only vs owner-supplied data paths. Retain INI write-through; validate rename/flush/error behavior. Non-x86 externals currently try a wow64 helper/Wine process, incompatible with Vita. Map the actual CleanMem exports to measured native semantics/OS memory queries, never invent successful DLL returns. Audit other OS/process calls as reached. |
| Other crates / device lifecycle | image 0.25.6, imgui 0.12.0, lzzzz 2.0.0, rmp3 0.3.1 and time 0.3.41 are not certified by this subset build. Gate desktop debugger/capture and cross-compile retained C/C++ sources with hard-float SDK; review target vs host `cfg!` in build scripts. Measure heap, load peak, frame pacing, audio, save paths and suspend/resume on hardware. |

**Next one high-information experiment:** extract the existing compiler/VM-to-`Game` host boundary in a new source copy, with real Vita filesystem/external services and explicit capability errors. Compile the unchanged original scripts/events and execute the real startup until its actual modal request, logging the first unsupported call and allocator peak. Then attach useful native rendering/input/audio to this same engine path for the original menu; a fake menu or empty VPK is not an acceptable substitute. The current source diagnostics are a foundation, not that interpreter prototype. Owner selects title ID before packaging; distribution approval remains separate.

Private evidence: `reports/local/native-probe-20261123/` contains summary/identities, PC process/exit/audio/memory, restarted-EVA screenshot, host-data result, all failed/successful build logs and ELF inspection/conversion. Original ZIP/EXE/music/GMK hashes still match baseline. **New recovered resources: zero; no decompilation repeated.** Prior corpus remains 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms.
