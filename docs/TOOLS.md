# Tooling checklist (prefer existing local tools)

**2026-11-26 UTC — E024–E026 current:** original normal frames, native Ctrl/Touch sampling, right-stick/X menu navigation and audible SceAudioOut music verified on physical Vita. Original resources/GML unchanged. E026 active-scene clear/full-display PASS; original room6 stops at fifth atlas request. E027 bounded mapped-RAM overflow test pending. Original rooms run at30 Hz; no displayed60 FPS or playable Firefight claim. [Current evidence and measurements](OPENGMK_RUNTIME_PROGRESS.md). Earlier entries below are historical.

**E023 reuse/proof:** existing libvita2d clear shaders and checked direct GXM depth/viewport calls, no new shader compiler or download. Physical 32×32 depth/color/occlusion contract and original frame-zero presentation PASS. Existing Ramen caption request contract permits ignored void requests; native metadata retained with unavailable titlebar effect logged. MP3 validation merged into the original decoded length scan, PC streaming comparison PASS. Source reuse 22/22, fresh prep 202/202, unchanged Game::frame, offline PC/ARM/desktop builds and cleanup verified. [Commands/measurements/limits](OPENGMK_DRAW_PROBE.md).

**E022 existing codec reuse:** cached rmp3 0.3.1/minimp3, libc 0.2.185, cc 1.2.60; existing OpenGMK MP3 player and pure udon Source interface copied into fresh ignored build source, no libsoundio/native desktop frontend or new decoder. Scalar float native build uses existing WSL hard-float GCC plus authored `vita_wsl_ar.py`, all offline. Desktop SIMD feature retained, lock unchanged. PC contracts and first ARM build PASS; physical original-MP3 decode/registration and original Draw/depth-clear stop verified. [Exact commands, limits and failures](OPENGMK_MP3_PROBE.md).

**E021 reuse/startup proof:** no installs/downloads. Existing x86 MSVC builds an authored guarded failure fixture; only a private hash-checked reviewed priority-function slice executes, with actual Windows setters failing on invalid handles. New preparer retains E020 backend/archives and adds bounded real file/INI services plus native unsupported-effect diagnostics. PC/desktop/first ARM build, persistent native INI and exact audio stop verified; [commands, fixture scope, failures and evidence](OPENGMK_STARTUP_SERVICES_PROBE.md).

**E020 reuse/device graphics proof:** existing hard-float `libvita2d.a` and VitaSDK GXM/display/AppMgr/CommonDialog stubs, no vitaGL or downloads. Narrow C bridge compiled with GCC 15.2.0 `-Werror`; Rust uses local copied archives because its Windows bundler cannot see WSL-only paths. `prepare_graphics_native.py` records exact commands/hashes; `prepare_graphics_probe.py` attaches the backend to E019 in a fresh copy. Host/ARM/desktop/reuse checks pass; authentic-resource GPU/readback/display and memory/timing measured on Vita 1000. [Audit, archive identities, failures and reproduction](OPENGMK_GRAPHICS_PROBE.md).

**E019 reuse/device proof:** same offline toolchain; priority adapter, persistent diagnostic, optional owner High policy and ID-gated private packager added. Both revisions ran the original VM prefix on physical Vita 1000; FTP upload/retrieval and installed SELF hashes verified. No game/binary distribution in Git. [Commands, memory observations and remaining services](OPENGMK_PRIORITY_PROBE.md).

**E018 reuse:** same offline Rust/MSVC/WSL SDK; existing GNU objdump 2.46 used for complete helper inspection. `prepare_cleanmem_probe.py` reuses E017 plus E015 modal/INI patches in fresh copies; the hash-checked differential test, portable adapter and real human-dialog provider are under tools/opengmk/. PC, desktop check, ARM link and VELF conversion passed first attempts; no new crate/tool/install. [Exact commands and limits](OPENGMK_CLEANMEM_PROBE.md).

**E017 reuse:** existing private Windows Rust/Cargo 1.100.0 and WSL hard-float SDK reused entirely offline, without downloads/installations. New headless preparer, service/heap instrumentation, original-data runner and source-reuse auditor are under tools/opengmk/. Both real VM ARM build/VELF conversion and desktop library check pass. See [VM probe](OPENGMK_VM_PROBE.md) for exact commands and remaining native import obligations.

## E016 inventory update — 2026-11-24 UTC

VERIFIED existing WSL hard-float VitaSDK: GCC 15.2.0, SDK build 2026-05-24, newlib `fbb8375870d799758e0b4358d2f1708781aa26a6`, vita-toolchain `71f3789342f610a4eb3ba50fc33292c4900c6666`; SDL2/vitaGL already present in WSL soft/hard-float SDKs. Windows SDK remains soft-float and cannot link the hard-float Rust objects. Existing private Rust/Cargo 1.100.0 reused; missing rust-src/std build dependencies and target num_threads/x11-clipboard/xcb fetched. cargo-vita absent from checked paths, unnecessary for direct Cargo ELF research. Stable plus process-local RUSTC_BOOTSTRAP enables the bounded build-std test; recommended upstream nightly workflow remains separate.

Tooling incident: an initial version command without the private Rust home variables triggered an unnecessary default stable toolchain install/synchronization outside the checkout. No cleanup or other external-project edits were attempted; all later Rust commands used explicit private homes. Do not describe E016 as zero-download/zero-external-write work. Exact successful/failed commands, SDK identities, new shareable probes and limits are in [OPENGMK_NATIVE_PROBE.md](OPENGMK_NATIVE_PROBE.md); raw evidence is ignored under reports/local/native-probe-20261123/. No SDK reinstall, cargo-vita installation or VPK occurred.

**Host:** Windows development machine. Codex should inventory local utilities first; do not download or reinstall everything reflexively.

## Baseline
- Python 3 (standard library), script: `python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip`.
- 7-Zip or Python zipfile: archive inspection and isolated copying. Do not double-click unknown executables.
- PE introspection: pefile / dumpbin / llvm-readobj / Ghidra, whichever is already present.

## GameMaker investigation
- [GM8Decompiler](https://github.com/OpenGMK/GM8Decompiler): candidate, **only after** runner version detection.
- [Gmk-Splitter](https://github.com/Medo42/Gmk-Splitter): may help examine a recovered project.
- [OpenGMK](https://github.com/OpenGMK/OpenGMK): runner/backend research; check license, compiler, graphics dependencies and actual game compatibility.

## Windows EXE translation + Vita examples
- [D2Vita](https://github.com/Franckrst/D2Vita): research reference for x86-to-ARM/Windows adaptation.
- [sh3vita](https://github.com/matfsouza/sh3vita): comparison for recompilation method.
- [VitaSDK](https://vitasdk.org/) and [SDL2 Vita](https://wiki.libsdl.org/SDL2/README-vita): potential native target toolchain; not chosen architecture.
- Vita3K optional; **real Vita required** to substantiate performance/compatibility.

## Local-only directory roles
- `original/`: user-provided ZIP/EXE + music.
- `recovered/`: private recovered GML/resources.
- `local-tools/`: fetched third-party binaries/source copies.
- `reports/local/`: logs, dumps, profiles.
- `build/`: VPK/ELF outputs.

Never commit tool downloads, proprietary sources or recovered game data.

## Local inventory — VERIFIED 2026-11-23 UTC

All tools below already existed or were supplied locally during the session. **No tools were downloaded or installed.** External trees were read only; selected executables/JAR/loader sources were copied into ignored `local-tools/session-20261122/`. Absolute host paths are confined to private evidence.

| Tool | Observed identity | Use / limits |
| --- | --- | --- |
| Python | 3.14.4 | Standard-library archive, PE, hash and inventory scripts |
| GM8Decompiler, standalone | 2.2.0, i686 MSVC, built 2024-02-12, `#fb6d4d57` | Used successfully; SHA-256 below |
| GM8Decompiler, bundled | File version 2.1.1 | Present in OpenGMK bundle; not retried after 2.2.0 succeeded |
| OpenGMK / GM8Emulator | Bundle v0.2.0, file version 0.2.0, i686 Windows MSVC | One strict PC trial; fails at `show_message_ext` |
| Gmk-Splitter | Folder v0.21; JAR 1,560,428 bytes | Reader works; standard export rejects duplicate resource name |
| Java / javac | Temurin 25.0.4.1 | Process-local preferences used to avoid host registry writes |
| Ghidra | 12.1.4 PUBLIC; application revision `8b6bbb857accdfa20dc5b2f5dea471178c2e9fbc` | Inventoried from application.properties; not launched or needed for these probes |
| VitaSDK, Windows | GCC 10.3.0; SDK built 2026-03-29 14:00:17 | `--version` works; toolchain commit `71f3789342f610a4eb3ba50fc33292c4900c6666`; no Vita build |
| VitaSDK, Ubuntu WSL | version_info built 2026-03-29 13:52:56; same toolchain commit | Present; cross-compilation not tested |
| D2Vita | VERSION 0.2.3 archive | Architecture/shim source reference; winx86 submodule empty |
| WinVita, supplied later | CMake version 0.1.0; MIT LICENSE; no git revision available | Includes Box86-derived sources and actual shims; host PE loader tested on copy |
| WSL host compiler | g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0 | Built only host metadata probe; QEMU ARM not found by `command -v` |

Cargo/rustc were not on the Windows PATH or in the checked user cargo bin directory. No OpenGMK source tree was located in the supplied tool directory. No SDL2 or vitaGL library matched the inspected Windows VitaSDK target-library paths; this does not prove absence elsewhere. No installation or broad system search was performed.

Binary/JAR identities (SHA-256):

| Artifact | SHA-256 |
| --- | --- |
| GM8Decompiler 2.2.0 | `ab39dc7a9013ecec9084de86fa220e25bb2f583edcd526370963bac78572d0f0` |
| Bundled GM8Decompiler 2.1.1 | `f863ca48fc67ebdf6383fe16769fa043fc778ac739a593ddabde9fa5e32f7977` |
| GM8Emulator 0.2.0 | `85d271874b4b7d10f813d59f951a10977754aa415d95e747d45348b06b9083c9` |
| gmksplit.jar | `319b9b0bf7a724059a18dfbe167b4057ec9d32d8269bf5ff4e0b2a6aed5ad3ed` |
| WinVita pe_image.cpp | `3675715e9e1dd109aa9580e799ee03d29df84c08cbb4f5fd11a174fa275fa371` |
| WinVita win32_shims_misc.cpp | `4250f2c5ccf4fccf757e7f7703bf0e65287f5215bca08b61add67df9dd420709` |
| D2Vita docs-site/shims.md | `c042ba1cf821dca68f99972939647309edb7f032f80dc5cd9e92992c4ea697fa` |

**Trust assessment:** Windows EXEs were unsigned. File versions, hashes, packaged readme and official project/release documentation were inspected; reproducible-build/provenance equivalence was not verified. The decompiler consumes data; it does not run the game. The one OpenGMK game trial was a host process, **not a security VM**. GML external/OS-call candidates and the tiny included DLL's imports were inspected first; paths and temporary outputs were redirected to fresh private copies. No original game EXE was launched as a Windows process.

Shareable probes added in this session: `tools/inspect_pe.py`, `tools/GmkAudit.java`, `tools/MemoryPrefsFactory.java`, `tools/probe_winvita_loader.cpp`. Their outputs may contain private resource names/GML: keep output under ignored paths. The Java reader uses the separately supplied JAR; the C++ probe uses separately supplied WinVita loader source. Neither third-party dependency is committed.

## PC menu session additions — VERIFIED 2026-11-23 UTC

The earlier inventory's absence findings were bounded, not machine-wide: existing MSVC `14.50.35717`, Windows SDK, CMake and Ninja were located under the Visual Studio Build Tools installation and reused. Rust/Cargo were absent from the checked host paths; the existing local rustup-init `1.29.3 (edbc831ce 2026-11-02)` installed a minimal private toolchain, Rust `1.100.0` / Cargo `1.100.0`, plus `i686-pc-windows-msvc`. RUSTUP_HOME/CARGO_HOME are inside ignored local-tools; `--no-modify-path` avoided persistent PATH edits. No Visual Studio components were installed.

OpenGMK source was missing locally and obtained from its official repository at `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`, then cloned locally to a separate working copy. Cargo fetched dependencies using the unchanged lockfile. The older local executables and source reference trees remain untouched. Build recipe, compiler identities, resulting binary hash and private evidence paths: [OPENGMK_PC_PROBE.md](OPENGMK_PC_PROBE.md). Native dialog backend and controlled fixture are shareable source under `tools/opengmk/`; integration diff is under `patches/opengmk/`. Publication/licensing review remains separate.

## Arena session — E015, no installation/download

Reused the compiled runtime first, then built one separate INI/diagnostic source copy offline after concrete visual/audio reports. Existing MSVC builds `audio_session_meter.cpp`; the existing Cargo cache supplies the udon copy pinned at `1ae3cdce620acdaa7996315c05a98a0f12ed8745`. Prior caches/source/binaries are preserved. `run_pc_probe.py` logs Windows process memory/exit and redirects the child's profile/temp. `audio_recovery_probe.rs` and `check_audio_recovery.py` exercise recovery using only a synthetic audio fixture, never suspending the game. All raw outputs remain ignored. Source patches 0002/0003 and [E015](OPENGMK_FIREFIGHT_PROBE.md) record the runtime change, diagnostics and unsuccessful hypotheses; no new dependency version or Vita build was introduced.
