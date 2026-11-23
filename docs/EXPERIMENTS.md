# Experiments and findings

Record **every meaningful attempt, including failures**. Do not mark a test PASS on the basis of a plan or apparent compatibility.

## E000 — Initial static archive / PE audit

- **Date:** 2026-11-22 UTC (date of owner-supplied inspection)
- **Input:** HOWaW_FirefightDemov1.zip, SHA-256 `423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62`.
- **Method:** Python ZIP/PE static read; header/section/marker analysis, no game execution.
- **Expected:** determine architecture and basic archive integrity.
- **Observed:** CRC pass, PE32 x86, nine PE sections, GameMaker-related marker strings; no separate source project.
- **Result:** PASS for static format identification only. Exact runner build/compatibility: UNTESTED.
- **Evidence:** docs/TECHNICAL_AUDIT.md and reproducible tools/inspect_input.py.
- **Next:** identify exact GameMaker runner version and verify extractor compatibility.

## Session baseline and evidence keys — 2026-11-23 UTC

Owner-local date: 2026-11-22 (America/Bogota). All E001–E010 attempts below occurred on **2026-11-23 UTC**. Environment: Windows NT 10.0.26200, PowerShell 7.6.9, Python 3.14.4; Java Temurin 25.0.4.1 where noted; Ubuntu WSL/g++ 15.2.0 for E009. No tool downloads/installations, original-runner launch, Vita build or device test occurred.

Hashes used as input references below:

| Key | Artifact | SHA-256 |
| --- | --- | --- |
| H_ZIP | Original ZIP | `423838aadf1436412b42cb5a70a75262ad8a471b8c9cad99ac97354d093ade62` |
| H_EXE | Original EXE and every test copy | `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f` |
| H_MUSIC | menu.mp3 | `e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0` |
| H_GMK | Reconstructed project | `854d2644d3c2c22eabd8b3acc99e021f630d17d9fbf37faeac4519fa6a86e9c9` |
| H_CLEAN | Included CleanMem.dll | `dac23ed1af08cb7409a18dc09b0c35230e1b314ff49711394c66bd69ae86548c` |

Private evidence root **R = `reports/local/session-20261122/`**, recovery root **D = `recovered/session-20261122/`**, copied tools **T = `local-tools/session-20261122/`**. Paths below are repository-relative; aliases in prose denote those directories, not extra files. Full logs, GML, host paths and third-party binaries are ignored. Public summaries are in [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md); component versions/hashes are in [TOOLS.md](TOOLS.md). No log or game data is staged for publication.

Shareable probe revisions (SHA-256 of this session's source): `inspect_input.py` = `1d9e805781a14fe7c07289f948174efb36f36147f2e27c07b878bd6843ae6dec`; `inspect_pe.py` = `7bc6760faaaa0c589bb52be847db124194c1f975e8098047c3fac913a7c9a74f`; `GmkAudit.java` = `85c1cc6aee478e8a5c520d3258f418607e31dd4adf4f1d075374313bc0de3b3f`; `MemoryPrefsFactory.java` = `8dcd652dfe170626b77c6b6a8b2f374cd8ecb9456103fc52cc6470deead1c1fb`; `probe_winvita_loader.cpp` = `74e29ef6704ff0316362226655359727a44e8c0c851117d4400d33b381e9c033`.

### E001 — Inventory existing local tools

- **UTC:** 2026-11-23. **Input:** local tool metadata/hashes (no game execution; H_EXE only a later comparison input).
- **Tools/commands:** PowerShell `Get-ChildItem`, `Get-Command`, `Get-Item`, `Get-FileHash -Algorithm SHA256`, `Get-AuthenticodeSignature`; `python --version`, `git --version`, `java --version`; copied `gm8decompiler.exe --help` and `gm8emulator.exe --help`; Vita GCC `--version`; `wsl --list --quiet`. Exact host-path discovery/launch commands are recorded privately in R/commands.txt. Consolidation: `python reports/local/session-20261122/summarize.py`.
- **PASS rule:** locate and identify existing tools before downloading anything.
- **Observed VERIFIED:** GM8Decompiler 2.2.0 and bundled 2.1.1, GM8Emulator 0.2.0, Gmk-Splitter 0.21, Ghidra 12.1.4, Windows/WSL VitaSDK and D2Vita 0.2.3. WinVita supplied later is covered in E008/E009. WSL list initially returned access denied; authorized read-only retry succeeded. Decompiler help waits for a key; no repeated decompilation was performed because of that pause.
- **Result: PASS** for bounded inventory, not a full-machine absence audit or toolchain build validation. Tools are unsigned local inputs; provenance equivalence to upstream binaries remains UNTESTED.
- **Evidence:** R/inventory.json, R/emulator-help.txt, R/gcc-host-version.txt; TOOLS.md. Absolute source locations remain private.
- **Next discriminating test:** verify archive identity before recovery (E002).

### E002 — Recheck the owner ZIP and extracted inputs

- **UTC:** 2026-11-23. **Inputs:** H_ZIP, H_EXE, H_MUSIC. **Tool:** Python 3.14.4, unchanged `tools/inspect_input.py` hash above.
- **Exact command:** `python tools/inspect_input.py original/HOWaW_FirefightDemov1.zip` (also captured to R/baseline.json).
- **PASS rule:** ZIP baseline match, CRC pass, exact two file hashes.
- **Observed:** first attempt returned “Missing input or too large”: only an extracted folder existed. Recovery was paused. Owner then supplied the ZIP; the same command reported `matches_baseline=true`, `crc_ok=true` and both expected entry hashes. Existing extracted EXE/music hashes also matched. No substitute/repacked ZIP was used.
- **Result: initial BLOCKED, then PASS** after owner supplied the missing input. Original bytes remained untouched.
- **Evidence:** R/baseline.json, R/baseline-after.json and R/inventory.json; audit hash table. Final recheck confirmed ZIP hash/CRC, original EXE/music and reconstructed GMK hashes unchanged.
- **Next:** loading signatures/imports on a private copy (E003).

### E003 — Verify 8.0 loading/header structure and PE imports

- **UTC:** 2026-11-23. **Input:** private copy H_EXE. **Tool:** Python 3.14.4 / `tools/inspect_pe.py` session revision above; detector offsets compared with official OpenGMK `gm8exe/src/gamedata/gm80.rs`.
- **Exact command:** `python tools/inspect_pe.py recovered/session-20261122/HOWaW_FirefightDemov1.exe > reports/local/session-20261122/pe.json`.
- **PASS rule:** intact 8.0 loading/version checks plus matching data header, rather than a string-only guess; enumerate import descriptors/symbols.
- **Observed VERIFIED:** matching sequences at `0xA49BE` and `0xA49E2`, magic `1234321`, version `800` at `0x1EAB90`; pointer/search behavior agrees with detector. 26 import descriptors / 535 entries / 496 unique pairs / 17 DLLs, including D3D8 and DirectDraw creation, WinMM MCI/joystick/timing. PE application metadata says 1.0.0.0, not the runner build.
- **Result: PASS** for GameMaker 8.0 format and static dependencies; **BLOCKED/UNTESTED** for exact vendor patch/build and actual dynamic API usage. E004 and E009 provide independent parser checks.
- **Evidence:** R/pe.json; audit tables; [detector source](https://github.com/OpenGMK/OpenGMK/blob/master/gm8exe/src/gamedata/gm80.rs).
- **Next:** strict 8.0-compatible decompilation (E004).

### E004 — Recover GMK without altering original logic

- **UTC:** 2026-11-23. **Input:** H_EXE after E002 passed. **Tool:** GM8Decompiler 2.2.0 i686 MSVC, built 2024-02-12, `#fb6d4d57`, SHA-256 in TOOLS.md.
- **Exact command:** `.\local-tools\session-20261122\gm8decompiler.exe recovered/session-20261122/HOWaW_FirefightDemov1.exe -v -d off -p -o recovered/session-20261122/HOWaW.gmk > reports/local/session-20261122/decompiler.txt 2>&1`.
- **PASS rule:** strict data parse and completed project write; do not count an empty/partial output as recovery.
- **Observed VERIFIED:** “Successfully parsed game” and “Successfully written gmk”; completed with exit 0 after its final key prompt. Output H_GMK, 15,998,859 bytes. No lazy checks, deobfuscation or event repairs. Slot counts: 755 sprites, 141 sounds, 111 backgrounds, 3 paths, 200 scripts, 9 fonts, 264 objects, 22 rooms, one include, zero extensions. These counts include deleted holes.
- **Result: PASS structural recovery**, not project/editor identity or gameplay fidelity. No fallback decompiler was needed.
- **Evidence:** R/decompiler.txt; D/HOWaW.gmk; R/decompiler-live-counts.json.
- **Next:** independent reader/ID-based inventory (E005/E006).

### E005 — Standard Gmk-Splitter export: two concrete obstacles

- **UTC:** 2026-11-23. **Input:** H_GMK. **Tools:** Gmk-Splitter 0.21 JAR (hash in TOOLS.md), Temurin Java/javac 25.0.4.1.
- **First exact command:** `java -jar local-tools/session-20261122/gmksplit.jar --preserve-ids all recovered/session-20261122/HOWaW.gmk recovered/session-20261122/split` (stdout/stderr in R/splitter.txt).
- **Observed:** Java preferences initialization attempted to access its host registry node and failed with access denied. **BLOCKED** before file read; no permission/settings changes were made.
- **One environment correction:** compiled a process-local `MemoryPrefsFactory` in T, then ran `java '-Djava.util.prefs.PreferencesFactory=MemoryPrefsFactory' -cp 'local-tools/session-20261122;local-tools/session-20261122/gmksplit.jar' com.ganggarrison.gmdec.GmkSplitter --preserve-ids all --charset windows-1252 recovered/session-20261122/HOWaW.gmk recovered/session-20261122/split` (R/splitter-memoryprefs.txt).
- **PASS rule:** export without modifying names, IDs or data.
- **Observed VERIFIED:** reader completed, export rejected a duplicate sprite name with `IllegalArgumentException`. The name and stack trace are private. No renamed project or partial tree was treated as valid output.
- **Result: FAIL for standard tree export**. This does not invalidate GMK parsing; no repeat of the same export was attempted.
- **Evidence:** R/splitter.txt, R/splitter-memoryprefs.txt; original GMK hash unchanged.
- **Next:** use the existing reader directly, bypassing filename export rather than changing game resources (E006).

### E006 — Independently count existing resources/events by ID

- **UTC:** 2026-11-23. **Input:** H_GMK. **Tools:** same JAR/Java as E005, `GmkAudit.java` and `MemoryPrefsFactory.java` hashes above.
- **Exact successful commands:**

```powershell
javac -sourcepath tools -cp local-tools/session-20261122/gmksplit.jar -d local-tools/session-20261122 tools/MemoryPrefsFactory.java tools/GmkAudit.java
java '-Djava.util.prefs.PreferencesFactory=MemoryPrefsFactory' -cp 'local-tools/session-20261122;local-tools/session-20261122/gmksplit.jar' GmkAudit recovered/session-20261122/HOWaW.gmk recovered/session-20261122/audit
```

- **PASS rule:** independent reader parses project, retains duplicate names/IDs and yields counts agreeing with live-entry decompiler logs.
- **Observed VERIFIED:** 693 sprites / 2,120 frames, 128 sounds, 101 backgrounds, 181 scripts, 233 objects, 845 events, 875 actions, 15 rooms, 1 path, 7 fonts, 3,917 room instances, 8,123 tiles. Zero timelines/triggers/constants, one included DLL, zero packages. No duplicate object names; one duplicate sprite-name group. Initial helper compilation failed on an ambiguous Java `Path` import and attempted recompilation of JAR-embedded legacy sources; explicit Path import and `-sourcepath tools` corrected those build-only issues. Successful audit exit 0.
- **Result: PASS for inventory**, not full semantic/asset parity. The audit writes GML/includes only into ignored D/audit, never back into the GMK. Sprite RGBA payload count 27,451,468 bytes excludes other runtime costs.
- **Evidence:** D/audit/counts.txt, resources.tsv, code.txt, rooms.tsv; R/gmk-audit.txt; R/decompiler-live-counts.json. No proprietary code copied into public documents.
- **Next:** one PC run of original data after inspecting external/OS-call candidates (E007).

### E007 — OpenGMK 0.2.0 strict PC execution: first original-code blocker

- **UTC:** 2026-11-23. **Inputs:** H_EXE + H_MUSIC in fresh D/pc-run; H_CLEAN exported by the runtime. **Tool:** local GM8Emulator 0.2.0, SHA-256 in TOOLS.md; AMD OpenGL driver reported 3.3.0 Core Profile / 26.11.2.261112.
- **Exact child command:** copied `gm8emulator.exe HOWaW_FirefightDemov1.exe -s -v`, working directory `recovered/session-20261122/pc-run`. Child TEMP/TMP pointed to `recovered/session-20261122/pc-temp`. PowerShell `Start-Process -WindowStyle Hidden` redirected stdout/stderr into R/opengmk-stdout.txt and R/opengmk-stderr.txt; full launch statement is in R/commands.txt. Windows UI enumeration used the computer-use skill; no remaining game window was returned.
- **Trust/environment:** host process, not a VM. Static GML call scan and H_CLEAN imports were inspected first. No original Windows runner process was launched. No source changes, dialog bypasses, stubs or asset substitutions were used.
- **PASS rule:** original data reaches a real menu and one genuine interaction without a missing-builtin crash.
- **Observed VERIFIED:** gamedata parsing completes and a real OpenGL context initializes. Original startup GML reaches `show_message_ext`, then Rust panics at `gm8emulator\\src\\gml\\kernel.rs:6609:9` (“Called unimplemented kernel function show_message_ext”). Process terminates before a menu. Numeric exit code was not captured. Reaching the prompt after CleanMem calls suggests they returned, but their effects/values are **INFERRED/unmeasured**.
- **Result: FAIL for playable PC compatibility**. Parsing/context/startup reach are partial successes. Menu, audio, controls, animation, combat, collisions, progression and saving are UNTESTED, not passed or individually proven broken.
- **Evidence:** R/opengmk-stdout.txt, R/opengmk-stderr.txt, D/audit/code.txt. Upstream source inspection also shows the builtin unimplemented: [kernel.rs](https://github.com/OpenGMK/OpenGMK/blob/master/gm8emulator/src/gml/kernel.rs).
- **Next:** implement the actual three-choice dialog in a private runtime source copy and rerun unchanged data; do not repeat the failing binary as-is.

### E008 — D2Vita / subsequently supplied WinVita: source-level API gaps

- **UTC:** 2026-11-23. **Input:** H_EXE import report; local D2Vita 0.2.3 archive and owner-supplied WinVita CMake 0.1.0 snapshot. Source commit IDs unavailable; identifying hashes in TOOLS.md and R/winvita-coverage.json.
- **Exact analysis commands:** `python reports/local/session-20261122/summarize.py`; `python reports/local/session-20261122/winvita-audit.py`. These private, nonmutating scripts compare imports against D2Vita's documented table and WinVita runtime-source registration candidates. The second reuses the local `tools/shim_seq.py` parsing functions without invoking its obsolete `rt_boot.cpp` entry point or writing external caches.
- **PASS rule:** identify actual missing/unsupported interfaces rather than extrapolate from Diablo II compatibility.
- **Observed VERIFIED:** D2Vita's archived winx86 directory is empty, but newly supplied WinVita has loader/bridge/ARM dynarec sources. Source scan finds no D3D8 bridge; `DirectDrawCreate` is explicitly an error-returning shim; MCI functions are absent. DirectSound code and TLS/scheduler facilities exist, with HOWaW behavior UNTESTED. Local WinVita README's no-shims claim conflicts with its actual files; code was used as evidence.
- **Name counts:** D2Vita combined documentation: 226/496 matching, 270 absent. WinVita source candidates: 128/496 matching, 368 unmatched. Scope differs; these are **not** semantic coverage rates, unresolved-at-runtime counts, or an instruction to implement every imported API before tracing which are used.
- **Result: PASS for static gap identification; guest execution UNTESTED**. Initial missing-submodule build prerequisite was partially resolved by the supplied standalone tree. No download, external modification or Vita packaging.
- **Evidence:** R/d2-coverage.json, R/winvita-coverage.json; [TECHNICAL_AUDIT.md](TECHNICAL_AUDIT.md). Original source files/paths remain local.
- **Next:** minimal host-only PeImage probe (E009), not a new speculative VPK.

### E009 — WinVita loader maps the actual PE on a PC host

- **UTC:** 2026-11-23. **Inputs:** H_EXE; copied WinVita pe_image.cpp SHA-256 `3675715e9e1dd109aa9580e799ee03d29df84c08cbb4f5fd11a174fa275fa371`, header identity in R/winvita-coverage.json; original probe source hash above.
- **Environment/tools:** Ubuntu WSL, g++ 15.2.0-16ubuntu1. No full WinVita build, ARM CPU or Windows APIs linked.
- **Exact commands inside WSL, repository working directory:**

```sh
g++ -std=c++17 -O2 -Wall -Wextra -Ilocal-tools/session-20261122/winvita/src tools/probe_winvita_loader.cpp local-tools/session-20261122/winvita/src/runtime/pe_image.cpp -o build/session-20261122/probe_winvita_loader
build/session-20261122/probe_winvita_loader recovered/session-20261122/HOWaW_FirefightDemov1.exe
```

- **PASS rule:** real PeImage::load succeeds with real imports, without claiming guest execution.
- **Observed VERIFIED:** build exit 0, no diagnostics; probe exit 0: `LOAD_PASS file_bytes=18142424 image_bytes=3584000 entry_va=0x588750 import_entries=535 unique_imports=496`; `NO_GUEST_EXECUTION`. Import totals agree with E003. Probe executable SHA-256 `0b03237df4a5d3da4551cf569d6f75a0e984ef1912574d8457d6d4cf6edfd644`.
- **Result: PASS for PE mapping/import parsing only**. Import linking, entry-point execution, overlay reads through a guest filesystem, graphics, sound, ARM translation and Vita performance remain UNTESTED.
- **Evidence:** R/winvita-loader.txt, R/winvita-build.txt, R/gcc-host-version.txt; ignored build/session-20261122/probe_winvita_loader.
- **Next:** retain route A as fallback; first resolve route B's much smaller observed startup blocker (ADR-001).

### E010 — Embedded graphics helper and included x86 DLL

- **UTC:** 2026-11-23. **Inputs:** H_EXE / H_GMK and H_CLEAN. **Tools:** Python 3.14.4 `struct`/`zlib`/`hashlib`, inspect_pe.py revision above; Java audit already described in E006.
- **Exact PE commands:** `python tools/inspect_pe.py recovered/session-20261122/audit/include-0.bin > reports/local/session-20261122/cleanmem-pe.json`; `python tools/inspect_pe.py recovered/session-20261122/embedded-D3DX8.bin` (FAIL: not MZ); after one zlib inflation, `python tools/inspect_pe.py recovered/session-20261122/D3DX8-inflated.dll > reports/local/session-20261122/d3dx8-inflated-pe.json`. Exact original extraction/inflation Python statements are retained in R/commands.txt.
- **PASS rule:** verify actual PE artifacts/imports, not just DLL-name strings; never load the helpers to inspect them.
- **Observed VERIFIED:** CleanMem is PE32 x86, 1,024 bytes, with five KERNEL32/PSAPI imports listed in the audit. Reading the graphics block directly as PE failed because it was compressed; its `78 9c` header justified one bounded standard-library inflation. Compressed block at `0x1ED52B`: 267,324 bytes, SHA-256 `a12747c50792a8386b74a73e6b9471f78e5833565eba08afb08ff4ddee03c35a`. Inflated DLL: 495,616 bytes, SHA-256 `edfc5f86be36c2c509e4ad6ba3742bb5b2429a56de805a99771e24fec62b076a`, PE32 x86; 76 KERNEL32, two USER32, 13 GDI32 import entries. No helper execution occurred in this static probe.
- **Result: initial FAIL for raw-block-as-PE assumption, then PASS for compressed helper identification**. Actual D3DX8 dynamic calls remain UNTESTED. Prior empty/failed report was retained; successful inflation used a new file/report.
- **Evidence:** D/embedded-D3DX8.bin, D/D3DX8-inflated.dll, R/d3dx8-inflated-pe.json, R/cleanmem-pe.json; no DLL committed.
- **Next:** route B's faithful missing-dialog experiment, with future native adaptation of the two CleanMem exports recorded as an ARM blocker.

## PC menu session — 2026-11-23 UTC (owner date 2026-11-22)

Private evidence root **M = `reports/local/menu-probe-20261122/`**. Original input hash keys H_ZIP/H_EXE/H_MUSIC/H_GMK above are unchanged. Existing E007 remains a failed baseline; these entries do not replace it. Source/build reproduction: [OPENGMK_PC_PROBE.md](OPENGMK_PC_PROBE.md). Exact local host setup and launch commands are retained in M/commands.txt; paths in public documents remain sanitized.

### E011 — Missing-source/toolchain prerequisite and bounded working copy

- **UTC:** 2026-11-23. **Inputs:** official OpenGMK commit `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`; local rustup-init SHA-256 `38027d51d69a5d05493627a0634dbea52d6cd793c8f072d2373d3f4163eec7db`, version `1.29.3 (edbc831ce 2026-11-02)`.
- **Environment:** Windows NT 10.0.26200 / PowerShell 7.6.9. MSVC tools 14.50.35717 and Windows SDK/CMake/Ninja located in the existing Visual Studio Build Tools tree. Rust/Cargo and OpenGMK source absent in the checked local locations.
- **Exact core commands:** `git ls-remote https://github.com/OpenGMK/OpenGMK.git HEAD refs/tags/v0.2.0`; `git clone --depth 1 https://github.com/OpenGMK/OpenGMK.git local-tools/menu-probe-20261122/OpenGMK`; `git clone --local --no-hardlinks local-tools/menu-probe-20261122/OpenGMK local-tools/menu-probe-20261122/OpenGMK-work`. The existing rustup-init ran with `-y --no-modify-path --profile minimal --default-toolchain stable --target i686-pc-windows-msvc`, with RUSTUP_HOME/CARGO_HOME pointing inside ignored local-tools. `cargo +stable fetch --locked --target i686-pc-windows-msvc --manifest-path local-tools/menu-probe-20261122/OpenGMK-work/Cargo.toml` fetched missing dependencies.
- **PASS rule:** reuse existing compiler/SDK, obtain only absent prerequisites, retain pristine source and change a separate working copy.
- **Observed VERIFIED:** Rust `1.100.0 (0ef1bc386 2026-11-09)` / Cargo `1.100.0 (3acc79c0c 2026-11-05)` installed in the checkout, with no persistent PATH edit. MSVC was reused; no VS installation. Upstream still contains an unimplemented `show_message_ext`. Upstream's 1.77 toolchain pin is overridden by the recorded stable toolchain; no claim about Windows 7 support. Cargo.lock remains SHA-256 `8a10301053ade07fb5991594b4108024da5c21fb16843c61e59708a31e3428b1` in both clones. Pristine clone status stays clean.
- **Result: PASS.** The source commit differs from the old packaged 0.2.0 binary; no direct performance comparison or other upstream-change attribution is made.
- **Evidence:** M/source-clone.txt, work-copy.txt, rust-install.txt, cargo-fetch.txt; private source clones and recipe.
- **Next:** implement and independently exercise the real modal UI (E012).

### E012 — Real three-button modal probe before game execution

- **UTC:** 2026-11-23. **Input:** own Windows backend `tools/opengmk/message_dialog.rs`, SHA-256 `b898c2f5efabb2c0fb742cc64ea138cf26acd96ea74d5c21a34ee8fdb0cd96c0`; controlled fixture `dialog_probe.rs`, SHA-256 `43c42cfb6901ef3ad66220f8c495e7ddf2ffc7bde8af51266cfc915ed2be12d3`. No game assets or GML used.
- **Tools/environment:** Rust 1.100.0, MSVC x86 target. Exact build wrapper: `cmd /d /c local-tools\menu-probe-20261122\build.cmd probe`; core compiler command `rustc --edition 2021 --target i686-pc-windows-msvc tools/opengmk/dialog_probe.rs -o build/menu-probe-20261122/dialog_probe.exe` under RUSTUP_TOOLCHAIN=stable. Windows GUI actions used the computer-use skill.
- **PASS rule:** actual controls produce 1/2/3; Escape produces 0; call does not return before dismissal. No fixed-result test mode or synthetic GML bypass.
- **Observed:** initial launch with `Start-Process -WindowStyle Hidden` gave a pending call but no usable visible fixture; the fixture process alone was stopped and relaunched for interactive UI observation. Alpha click returned 1; Beta click returned 2; Tab/Tab/Enter selected Gamma and returned 3; Escape returned 0. Logged pending durations: 17,977 / 24,122 / 40,908 / 12,971 ms. `DIALOG_PROBE_PASS`, empty stderr. These durations are user/agent wait times, not performance measurements. Same backend bytes were copied into the runtime and compared for equality.
- **Implementation VERIFIED:** modal DialogBoxIndirectParamW with private button IDs (101–103), distinct cancellation path, OS message pumping and blocking caller. Runtime integration drains owner events and clears keyboard/mouse state after return. This supports the required pause/input behavior; edge cases with held buttons and exact original visual styling remain UNTESTED.
- **Result: initial GUI visibility BLOCKED, then PASS for the controlled four-case probe.**
- **Evidence:** M/dialog-probe-build.txt, dialog-probe-stdout.txt (initial pending launch), dialog-interactive-stdout.txt, dialog-interactive-stderr.txt; fixture binary hash `3b4132ccd0512884c27ba8ea211fe4d5ec4a859e80af86e06abe6b2de9a92d2c`.
- **Next:** compile the runtime with this backend and unchanged game data (E013/E014).

### E013 — Runtime compilation: retained MSBuild failure, Ninja success

- **UTC:** 2026-11-23. **Inputs:** E011 source/lockfile; E012 backend; `patches/opengmk/0001-show-message-ext.patch` SHA-256 `33b5d137650f44cde585f8c11020eba7836161bef526cbee3ccdefb37d157bf6`. Integration changes only platform-module wiring and the builtin handler; no game data changed.
- **Tools:** Rust/Cargo 1.100.0, MSVC tools 14.50.35717, existing VS CMake/Ninja, target i686-pc-windows-msvc.
- **Exact core command:** `cargo build --locked --release --target i686-pc-windows-msvc -p gm8emulator --manifest-path local-tools/menu-probe-20261122/OpenGMK-work/Cargo.toml`. Actual wrapper `cmd /d /c local-tools\menu-probe-20261122\build.cmd runtime` loads existing VsDevCmd x86/host x64 and private Rust/Cargo homes. Environment variants and paths are in M/commands.txt.
- **PASS rule:** produce real modified runtime, retaining lockfile and game hashes; do not count successful dependencies as a complete build.
- **First outcome FAIL:** libsoundio-sys CMake compiler check invoked VS/MSBuild and failed with FTK1011 tracking-log creation errors inside deeply nested paths. **INFERRED:** Windows tracking/path-length behavior; not a demonstrated missing SDK or game-code failure.
- **One motivated correction:** selected existing `CMAKE_GENERATOR=Ninja` and new shorter `CARGO_TARGET_DIR=build/mp`, preserving the failed build tree. No dependency reinstall or cleanup. Second build exit 0, optimized profile completed in 1m49s, with 48 compiler warnings (including upstream deprecations/extern declarations), not zero-warning claims.
- **Result: first build FAIL, corrected build PASS.** Output 5,335,552-byte runtime SHA-256 `02de3629b99b4382030fb2484b8e950be617c5b524643f0ecc976e84a87407a2`. `git apply --check` against pristine source passed; Cargo.lock unchanged.
- **Evidence:** M/runtime-build-1.txt and runtime-build-2.txt, ignored build trees, shareable backend/patch and reproduction recipe.
- **Next:** execute the original EXE copy after controlled probe PASS (E014).

### E014 — Original main menu and genuine interaction on PC

- **UTC:** start/end recorded in M/game-1-process.json and game-1-exit.json; ended `2026-11-23T04:39:10.014722+00:00`.
- **Inputs:** H_EXE + H_MUSIC copied into fresh `recovered/menu-probe-20261122/run-1/`; H_CLEAN exported by the original game data. Modified runtime hash from E013. ZIP and recovered H_GMK were read/hash-checked only; no re-decompilation or data edits.
- **Environment/tools:** Windows NT 10.0.26200, AMD OpenGL 3.3.0 Core Profile / driver 26.11.2.261112, i686 MSVC runtime built in E013. Original Windows runner was not launched.
- **Exact launcher:** `python reports/local/menu-probe-20261122/launch_runtime.py`. Child command `gm8emulator.exe HOWaW_FirefightDemov1.exe -s`, cwd `recovered/menu-probe-20261122/run-1/`, private TEMP/TMP `recovered/menu-probe-20261122/temp-1/`, RUST_BACKTRACE=1. CREATE_NO_WINDOW suppresses the console only; native game/dialog windows are interactive.
- **PASS rule:** unchanged original data displays the real main menu and responds to one genuine interaction; identify the first runtime error if any.
- **Observed VERIFIED:** native original-text Low/Medium/High priority dialog appears. Its actual game selection was not instrumented; E012 separately verifies each result. After dismissal: original logo/title prompt, Enter → welcome, Enter → player configuration, click Save Changes → actual **Firefight / Forge / Armory / Exit** menu. Click Firefight → three original scenario previews; select first scenario → Easy/Normal/Heroic/Legendary difficulty selector. Keyboard/mouse input and animated rendering worked on this route. Alt+F4 then closed the process with captured **exit code 0**; no further runtime error/panic observed.
- **Result: PASS for PC menu and genuine interaction.** No combat was started; weapons, enemies, collisions, audio output, save persistence after restart and Vita execution remain UNTESTED. No additional runtime correction was justified by this menu-only run.
- **Evidence:** M/game-1-stdout.txt, game-1-stderr.txt, game-1-process.json, game-1-exit.json; private main-menu.png, firefight-selector.png, difficulty-selector.png. Hash audit M/input-audit.json confirms original ZIP/EXE/music, recovered GMK and copied EXE unchanged. The runtime implementation and controlled test source contain no game GML.
- **Next discriminating test:** one bounded original Firefight arena on PC, recording movement, a weapon action, enemy spawning, audio and first failure. **No functional Vita VPK exists; none was generated.**

## Template (copy for E015+)

```markdown
### E015 — <one hypothesis>
- Date (UTC):
- Input hashes:
- Environment/tool version:
- Exact command/config:
- Hypothesis and PASS/FAIL rule:
- Observed outcome:
- Result: PASS / FAIL / BLOCKED
- Sanitized evidence:
- What changed / what's still unknown:
- Next discriminating test:
```
