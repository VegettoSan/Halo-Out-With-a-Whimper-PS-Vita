# E017 — original OpenGMK compiler/VM behind explicit service boundaries

**2026-11-23 local / 2026-11-24 UTC. VERIFIED:** the actual compiler, action system and VM now build/link for Vita ARMv7; the same source executes original startup in a PC headless process. It stops at the real `external_define` request for CleanMem, without fabricating an external ID or skipping the call. **ARM execution remains BLOCKED/UNTESTED on hardware. No functional VPK exists.** Base main: `c013982`.

## Implemented and tested

- `prepare_vm_probe.py` copies only pristine pinned OpenGMK `9e4282e6d19f4dd00961811840ddc3e11da6dd5a` to a **new ignored directory**. Its `headless` feature excludes desktop/TAS/X11/window/audio-output dependencies, retaining the engine library and original function table. `desktop` remains the default; selecting both frontends is an error. No alternative parser, compiler, VM, gameplay code or GML is supplied.
- `PlatformServices` receives explicit operation/argument requests; the inspection provider returns `SERVICE_UNAVAILABLE`, never a synthetic success value. The existing `RendererTrait` remains the graphics boundary. Its inspection implementation exposes real prepared CPU texture metadata; native upload/draw/readback operations stop explicitly.
- CPU resource preparation is separate from GPU upload. Original pixel buffers move into pending storage; no texture cloning or GPU allocation is introduced. Encoded sound data has an explicit `Deferred` variant, preserving bytes without claiming successful decoding/playback. Any unavailable audio request stops. Desktop audio code and the existing E015 playable PC executable remain untouched.
- The loader reads through `DataFiles`; GML file/INI operations remain explicitly unavailable in this inspection provider. This is **not** a completed virtual filesystem. PC runs are confined to fresh copies under `recovered/`; included-file export and process-local temp/profile stay there. The full native path/flush/save adapter remains work ahead.
- The original `external_define` argument/signature validation is retained. The external manager rejects the unsupported binding before reaching upstream dummy DLL success paths or wow64/Wine. The first requested DLL is **CleanMem.dll**, before the initial dialog. Its original bytes are not executed or changed.

**Reuse audit PASS 22/22:** compiler/context/value, action trees, events/movement, instance structures, sprite/room/object code are byte-identical to upstream; seven collision functions are unchanged. `runtime.rs` differs only by one feature-gated instruction counter. Cargo.lock and all dependency identities remain byte-identical. A fresh preparer output matched every file in the final tested working source. This verifies reuse, not full semantic/gameplay parity of the unavailable services. Unsupported-capability gates intentionally stop rather than certify those APIs.

This experiment starts from E016's pristine source baseline. It does not replace E015's dialog/INI/audio-adapted Windows runner or retest its established gameplay. Keep those existing adapter patches for subsequent native integration; E017's default-desktop compilation check is not a new interactive regression of that modified runner.

## PC execution and memory

Final host binary: i686 MSVC, **2,873,856 B**, SHA-256 `b154f8ec4ba6c28fc919b2189fc33eb053aa59d6c4ed8306b3c67f64a6fa7e39`. Actual copied EXE retains SHA-256 `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f`.

**VERIFIED final run:** 181 compiled scripts / 1,661 top-level script instructions, 233 objects / 845 compiled event trees. `Game::init` follows the original library/room/instance-event initialization and the existing VM executes **four instructions** before the first unsupported external binding. Child exit **2**, `SERVICE_UNAVAILABLE/External`; the Python test returns 0 only when that expected stop, nonzero instruction count and unchanged input are confirmed. This is a **PASS for the bounded startup-prefix test**, with further startup BLOCKED. It is not a menu/arena boot. Room creation-code errors retained lazily by upstream are not certified for every other room.

| Final 32-bit host allocator observation | Bytes / count |
| --- | ---: |
| Input buffer stage | 18,142,546 B live |
| After strict reader, EXE buffer released | 89,875,942 B live |
| Pending texture payload (original + runtime default font/particle data) | 71,602,980 B / 3,003 entries |
| Compiled Game | 93,997,779 B live (~89.6 MiB) |
| Peak requested Rust heap | **108,104,954 B (~103.1 MiB)** |
| Allocation requests / requests >=4 MiB | 165,765 / 1 |

Counters cover Rust allocator requests, not direct C allocations, allocator overhead/fragmentation, stacks, OS/driver allocations or GPU memory. Phase snapshots are aggregate lifetime measurements, not per-subsystem attribution. No textures were uploaded; no audio was decoded/output by the inspection frontend. These are **PC measurements, not Vita RAM usage or a fit/performance claim**. E016's atlas-capacity estimate is not a GPU allocation made in E017.

## ARM build and real dependencies

Reused E016's **private Windows Rust/Cargo 1.100.0 + WSL Ubuntu hard-float VitaSDK GCC 15.2.0** (toolchain `71f3789342f610a4eb3ba50fc33292c4900c6666`, newlib `fbb8375870d799758e0b4358d2f1708781aa26a6`). All builds offline, no downloads/installations or external toolchain changes. The previously proven scalar flag, no-LTO, no-symbol-strip and WSL linker settings were reused.

| Artifact/check | Result |
| --- | --- |
| Core + original compiler/VM, PC | PASS final build, 46.54 s |
| Same core, `armv7-sony-vita-newlibeabihf` | PASS final build/link, 56.29 s; **no ARM execution** |
| ELF inspection | PASS ELF32 ARM EABI5 hard-float / Thumb-2 |
| `vita-elf-create -v INPUT.elf OUTPUT.velf` | PASS exit 0; no packaging/installation |
| Default desktop library, i686 | PASS `cargo check`, 28.55 s; not an interactive run |

ELF **4,483,936 B**, SHA-256 `49ecd8138ea240291587bae8ebe43640d3e6563329a285ebace13130e519e86d`, under `build/vm17-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.elf`. VELF **5,282,678 B**, SHA-256 `7b68b8d773cc3f38414be3b43296486748d32a8df6bca18c34305ca4c3ebc068`, under `build/vm17-arm/howaw-vm-probe.velf`. Earlier E017 revisions and every E016 build are preserved.

The target dependency tree excludes **ramen, clipboard/xcb, imgui, udon/libsoundio, rmp3, lzzzz and libffi**. Retained dependencies include the real reader/parser, image codecs, serde/bincode, indexmap/phf, rust-ini, time, getrandom and newlib/pthread-backed std. Exact unchanged versions are in the preserved lockfile/tree. This is no longer merely a reader/parser build.

VELF conversion identifies **75 native import stubs across 10 libraries**: SceRtcUser (6), SceSysmem (3), SceThreadmgr (15), SceThreadmgrCoredumpTime (1), SceIofilemgr (5), SceLibKernel (31), SceLibRng (1), SceNet (10), SceNetCtl (1), SceSysmodule (2). These are link obligations, not measured call coverage. Network functionality remains linked through retained code/std and has not been exercised; module initialization and runtime behavior need device evidence. No GXM or audio-output backend is implemented. The original EXE/GML/game assets are not embedded in ELF/VELF; the runtime's existing licensed default font/particle data is retained.

## Reproduce

Use a new output name if the example directory already exists. The source must remain pristine:

```powershell
python tools/opengmk/prepare_vm_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/vm-probe-20261123/OpenGMK
```

Reuse E016's private RUSTUP_HOME/CARGO_HOME, process-local `RUSTUP_TOOLCHAIN=stable`, `RUSTC_BOOTSTRAP=1`, `RUSTFLAGS=-C target-feature=-neon`, `CARGO_PROFILE_RELEASE_LTO=false`, `CARGO_PROFILE_RELEASE_STRIP=none` and its WSL hard-float linker wrapper. Set `CARGO_TARGET_DIR` to a **new** ignored build directory. Actual ARM command:

```powershell
cargo build --offline --locked -Z build-std=std,panic_abort --target armv7-sony-vita-newlibeabihf --release -p gm8emulator --no-default-features --features headless --bin howaw-vm-probe --manifest-path local-tools/vm-probe-20261123/OpenGMK/Cargo.toml
```

For PC, use the existing x86 MSVC developer environment, a separate target directory, and the same command without `-Z build-std=std,panic_abort`, target `i686-pc-windows-msvc`. For desktop compile regression, replace headless/bin switches with `--lib` and use `cargo check`. Existing private wrappers in `local-tools/vm-probe-20261123/` capture the exact environment/commands; no new compiler setup is required.

```powershell
python tools/opengmk/run_vm_probe.py --runtime build/vm17-host/i686-pc-windows-msvc/release/howaw-vm-probe.exe --input-dir recovered/native-probe-20261123/pc-profile --run-name startup-final
python tools/opengmk/audit_vm_probe.py --source local-tools/menu-probe-20261122/OpenGMK --work local-tools/vm-probe-20261123/OpenGMK --report reports/local/vm-probe-20261123/reuse-audit-final.json
```

The run name must be fresh. The launcher verifies ZIP/EXE SHA-256, copies inputs, captures exit/heap/service evidence and checks the bounded outcome. It never supplies GML, fakes a DLL return or changes original data. On Vita, the diagnostic expects owner-supplied data at `ux0:data/howaw/HOWaW_FirefightDemov1.exe`; native stdout/log capture and device setup remain untested. No title ID was assigned and no VPK was generated.

## Failures retained and next experiment

The first PC build failed on the generated renderer signature scanner's array-return semicolon; the second exposed residual replay/LZ4/wow64 coupling and an AtlasRect conversion located inside the GL backend. These were corrected by parsing the signature, gating desktop replay compression/IPC, and moving the **unchanged** CPU conversion into common atlas code. Subsequent PC/ARM builds passed. Review refinements retained original external argument validation and split CPU preparation from GPU upload; their earlier binaries/logs are preserved. No failed attempt was discarded and no upstream interpreter algorithm was replaced.

**Next one high-information experiment:** inspect the actual CleanMem export/signature contract, implement an honest native external-service binding with measured OS semantics, then rerun this unchanged startup until the next real request (potentially the initial dialog). Do not answer the helper or dialog with a fixed value to advance. Rendering/input/audio/file/INI services and real Vita execution remain required before a graphical prototype. Route B is still best supported; physical compatibility/performance remains uncertain.

Evidence: ignored `reports/local/vm-probe-20261123/` contains all build attempts, final PC result/stdout/stderr, source-reuse audit, dependency tree, native imports/ELF inspection and identities in `summary.json`. ZIP/EXE/music/GMK hashes match baseline. **New recovered resources: zero; prior corpus unchanged (693 sprites, 128 sounds, 181 scripts, 233 objects, 845 events, 15 rooms).**
