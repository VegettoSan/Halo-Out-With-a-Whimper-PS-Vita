# E018 — CleanMem contract and original startup beyond the real dialog

**E019 follow-up:** [Verified Windows process/thread priority and first physical Vita VM-prefix run](OPENGMK_PRIORITY_PROBE.md). PC reaches Files/file_exists; physical Vita executes original startup to the missing real Dialog service. E018 evidence below retains its original scope.

**2026-11-24 UTC. VERIFIED:** the reused OpenGMK VM binds both real CleanMem exports, performs the Windows cleanup, reaches the original priority dialog and resumes only after the owner's response. Startup advances from E017's 4 instructions to **15**, stopping honestly at `set_program_priority` (`Process`). The updated core builds/links for Vita and converts to VELF. **ARM execution is UNTESTED; no functional VPK exists.**

## Actual helper contract

The existing recovered helper is 1,024 bytes, SHA-256 `dac23ed1af08cb7409a18dc09b0c35230e1b314ff49711394c66bd69ae86548c`. Static inspection of the entire export code, imports and PE layout precedes its differential test: entry point zero, no TLS, two exports, no additional imported services. No original EXE was launched as a Windows program.

| Export | ABI/parameters/return | Observed implementation |
| --- | --- | --- |
| `halo_shg_clean`, RVA `0x1000` | cdecl, zero arguments, real (`f64`) | Current PID; `OpenProcess(0x1f0fff, false, pid)`; `EmptyWorkingSet`; signed BOOL converted to double; `CloseHandle`. Zero is failure. |
| `halo_shg_get_mem`, RVA `0x1030` | cdecl, zero arguments, real (`f64`) | Same process handle; `GetProcessMemoryInfo` with 40-byte counters; zero on query failure, otherwise **current WorkingSetSize**, offset 12, loaded as signed 32-bit then converted to double; close handle. Not peak/private/allocated bytes. |

**VERIFIED original call sites:** both definitions have that signature. Initialization is called at startup and shutdown/free; cleanup has three call sites (startup/game end/room end), and its return is discarded. The memory-query wrapper has **zero callers** in the recovered corpus. Startup initializes both bindings, calls cleanup and requests the priority dialog. No GML or assets were edited or added; no new recovery/decompilation was performed.

The Windows adapter performs those OS calls, closes handles and preserves the original signed-32-bit query conversion. Failed operations return their failure value and log the OS error. Unknown DLLs remain unavailable; unknown exports/wrong calling convention/return type/arity are rejected. Existing external ID allocation, argument checking, `external_call` and `external_free` remain in use. The portable runtime never loads the x86 DLL.

The cleanup operation removes pages from a Windows working set; it does not delete game resources or prove a reduction in committed heap. [Microsoft's API contract](https://learn.microsoft.com/windows/win32/api/psapi/nf-psapi-emptyworkingset) and [counter definitions](https://learn.microsoft.com/en-us/windows/desktop/api/psapi/ns-psapi-process_memory_counters) support this distinction.

## Vita behavior: explicit failure, separate diagnostic

**VERIFIED SDK/link inspection:** no equivalent Windows paged working-set API was found in the installed public SDK. Newlib `malloc_trim` exists, but the preserved linked `_malloc_trim_r`/`_sbrk_r` code shows a break adjustment inside a reserved heap block, without kernel block release on that path. Substituting it would not reproduce or prove `EmptyWorkingSet`'s physical working-set effect. This is a bounded implementation inspection, not a claim about all possible Vita allocators. [Newlib documents its allocator interface](https://sourceware.org/newlib/libc.html).

Consequently the native binding reports **unsupported Windows cleanup / unsupported WorkingSetSize**, returns the helper's defined **failure value 0**, and never reports a successful cleanup or a fabricated process-memory quantity. This is an explicit failure-contract adaptation, **not a successful native cleanup implementation**. The original startup ignores cleanup failure, so binding/calling the actual helper contract can proceed without altering GML. Full native equivalence remains BLOCKED.

`sceKernelGetFreeMemorySize` is linked for a separate diagnostic (`rc`, free user/CDRAM/physical-contiguous memory). These system-free-memory fields are never substituted for WorkingSetSize. Its execution/values on hardware remain **UNTESTED**. No speculative allocator/cache purge was added.

## PC evidence

All commands use fresh ignored copies and the existing private toolchain. Both bounded startup tests exit **2** for the unavailable service; their launcher exits **0** only after checking that expected stop, VM progress and unchanged copied EXE.

| Test | Measured outcome |
| --- | --- |
| Differential helper test, 03:36:39.851–03:36:39.949Z | **PASS.** Reviewed copied DLL and adapter query both reported 23,633,920 B. Original cleanup returned 1, then working set 241,664 B. After retouching the 16 MiB fixture: 17,018,880 B; adapter cleanup returned 1, then 237,568 B. Handles 75 → 75. |
| Signature/binding lifetime | **PASS.** Reject bad ABI/return/arity/unknown export; unknown DLL not adapted; distinct IDs; `external_free` removes both bindings. |
| Noninteractive original startup, 03:36:39.856–03:36:40.292Z | **PASS bounded prefix / BLOCKED dialog.** Two real bindings, actual cleanup result 1, real `show_message_ext` request at instruction **11**; no automatic response. |
| Interactive startup, 03:37:22.671–03:39:07.749Z | **PASS bounded prefix / BLOCKED Process.** Owner chose **High**, result **3**. VM counter remained **11 → 11** while modal waited **104,690 ms**. Original GML resumed to **15** instructions / 5 traced calls, then `set_program_priority: SERVICE_UNAVAILABLE/Process`. |
| Source preservation | **PASS 22/22** E017 reuse audit; unchanged compiler/actions/events/collisions, VM only existing feature-gated counter, lockfile byte-identical. Fresh preparer output matched all **185** files of tested source. |
| Windows regression | **PASS** default desktop library `cargo check` (28.32 s), including preserved E015 dialog + INI patches. Modal backend byte-identical to E015. Existing playable E015 binary hash unchanged; no repeated arena/persistence trial. |

The differential test touches only its own child process and uses an allocator fixture, not invented game content. The completely reviewed helper is copied and hash-checked before loading; this is process isolation, not a security VM. Its code/disassembly and GML audit stay private.

The typed `PlatformServices::show_message_ext` receives the actual decoded text and three button captions. Windows uses the existing real modal implementation: blocking user choice, return 1–3 for buttons or 0 for close, then existing keyboard/mouse clear behavior. There is no answer flag or injected click. Vita's missing dialog frontend remains explicit. The next priority service is **not bypassed**: upstream's default desktop implementation is already a no-op, but the native inspection provider continues to reject it rather than silently inherit that behavior.

Audio code, latency and E015 runner were untouched. E016's underrun/cut uncertainty remains open; no new audible-cut reproduction, audio fix or continuity claim is made.

## ARM artifacts, dependencies and memory

Existing private **Windows Rust/Cargo 1.100.0, MSVC 14.50.35717, Python 3.14.4**, WSL Ubuntu hard-float VitaSDK **GCC 15.2.0** reused. SDK identities: toolchain `71f3789342f610a4eb3ba50fc33292c4900c6666`, newlib `fbb8375870d799758e0b4358d2f1708781aa26a6`. Static helper inspection uses existing WSL GNU objdump **2.46**. Builds offline; no install/download/toolchain edits.

| Artifact/check | VERIFIED result |
| --- | --- |
| PC VM + differential binary | Build PASS first attempt, 50.31 s |
| ARM real compiler/VM + adapter | Build/link PASS first attempt, 1m22s |
| ELF inspection | ELF32 ARMv7 EABI5, hard-float, Thumb-2; **4,492,908 B**, SHA-256 `256c8f840c9fd1f4170079866b20d603de36a2c33cfb75a1e7ff9a62b8ad69ea` |
| VELF conversion | `vita-elf-create -v` exit 0; **5,294,094 B**, SHA-256 `3a9999943300d20004b9bef4b3a67088a32f59a786447f9d1707441a64b23b55` |

Artifacts remain under `build/cm18-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.elf` and `build/cm18-arm/howaw-vm-probe.velf`. PC VM SHA-256 `c2a75122fb1d77c87aebf73e5d4b0e218541fc48d527ef7a6cc06af4ea907090`; differential binary `6cdf11d513f972453f6b923b30f214ee4020de0722498a66530bda582b0ed56c`. All earlier artifacts remain intact.

**76 native import stubs / 10 libraries:** SceRtcUser 6, SceSysmem 4, SceThreadmgr 15, SceThreadmgrCoredumpTime 1, SceIofilemgr 5, SceLibKernel 31, SceLibRng 1, SceNet 10, SceNetCtl 1, SceSysmodule 2. Only one new import versus E017: `sceKernelGetFreeMemorySize`. These are link obligations, not exercised service coverage; module initialization/network/std behavior needs hardware evidence. Desktop window/clipboard/GL/libsoundio/wow64/libffi dependencies remain excluded as in E017; lockfile unchanged, no new crate.

**Interactive 32-bit PC requested Rust heap:** compiled Game **93,997,804 B**, startup stop **93,999,838 B**, lifetime peak **108,104,966 B (~103.1 MiB)**; 166,517 allocation requests, one >=4 MiB; exit live 1,024 B. Pending CPU texture payload **71,602,980 B / 3,003 entries**. No texture copy/upload or audio decode/output was added. Counters exclude C allocations, allocator overhead, stacks, drivers/GPU. These and the Windows working-set numbers above are **not Vita memory measurements or fit claims**. Native headroom/heap limits remain unknown.

## Reproduce without repeating baseline setup

Use new output/run names; existing directories are refused. Keep the pinned pristine upstream `9e4282e6d19f4dd00961811840ddc3e11da6dd5a`:

```powershell
python tools/opengmk/prepare_cleanmem_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/cleanmem-probe-20261123/OpenGMK
```

Reuse [E017's explicit process-local Rust homes, scalar/no-LTO/no-strip settings and hard-float WSL linker](OPENGMK_VM_PROBE.md#reproduce); no default rustup or installation. Set fresh `CARGO_TARGET_DIR` for host/ARM/desktop. Exact build commands:

```powershell
cargo build --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --no-default-features --features headless --bin howaw-vm-probe --bin cleanmem-contract-probe --manifest-path local-tools/cleanmem-probe-20261123/OpenGMK/Cargo.toml
cargo check --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --lib --manifest-path local-tools/cleanmem-probe-20261123/OpenGMK/Cargo.toml
cargo build --offline --locked -Z build-std=std,panic_abort --target armv7-sony-vita-newlibeabihf --release -p gm8emulator --no-default-features --features headless --bin howaw-vm-probe --manifest-path local-tools/cleanmem-probe-20261123/OpenGMK/Cargo.toml
python tools/opengmk/run_cleanmem_contract.py --probe build/cm18-host/i686-pc-windows-msvc/release/cleanmem-contract-probe.exe --dll recovered/vm-probe-20261123/startup-final/CleanMem.dll --run-name contract-1
python tools/opengmk/run_vm_probe.py --runtime build/cm18-host/i686-pc-windows-msvc/release/howaw-vm-probe.exe --input-dir recovered/native-probe-20261123/pc-profile --run-name startup-1 --experiment cleanmem-probe-20261123 --expected-service Dialog --expected-operation show_message_ext
python tools/opengmk/run_vm_probe.py --runtime build/cm18-host/i686-pc-windows-msvc/release/howaw-vm-probe.exe --input-dir recovered/native-probe-20261123/pc-profile --run-name startup-interactive --experiment cleanmem-probe-20261123 --interactive-dialog
python tools/opengmk/audit_vm_probe.py --source local-tools/menu-probe-20261122/OpenGMK --work local-tools/cleanmem-probe-20261123/OpenGMK --report reports/local/cleanmem-probe-20261123/reuse-audit.json
```

For ELF inspection/conversion use the existing WSL SDK's `arm-vita-eabi-readelf -h -A INPUT.elf` and `vita-elf-create -v INPUT.elf OUTPUT.velf`. Full private commands/paths and outputs are preserved in `reports/local/cleanmem-probe-20261123/`; public examples deliberately omit machine-specific paths.

## Next implementation and useful hardware diagnostic

**Next one experiment:** implement a measured `set_program_priority` contract through `PlatformServices`, validating its actual argument and OS result in PC before considering Vita thread/scheduler mapping; resume the same original startup to its next real request. Do not inherit the upstream no-op or invent a Vita process-class equivalent. Keep the real modal and owner response.

For the first native run, add a bounded diagnostic file sink and platform initialization to this **existing real-data executable**, then use an owner-approved execution method/title ID. Load the owner-supplied unchanged EXE from `ux0:data/howaw/`, recording hashes, loader/compiler stages, allocation peak and OS-free-memory snapshots. Acceptance: original data compiles and native VM executes the same prefix; CleanMem logs explicit unsupported failure; the real dialog request stops with its contract intact. This would be a useful hardware test even before graphics, but it has **not been packaged or executed**. No VPK is justified until diagnostics and deployment identity/method exist.

After that evidence, attach a minimal genuine dialog frontend using Vita controls and a real rendering path, preserving the 0/1/2/3 contract and owner selection. Window/input, rendering, audio output, save/filesystem mapping, suspend/resume and memory headroom remain integration work. Route B is best supported by current reuse/build evidence; device viability and backend choice remain open.

Private evidence includes `contract-analysis.json`, `cleanmem-objdump.txt`, `vita-sbrk-r.txt`, `vita-trim-r.txt`, `contract-1/`, both startup captures, all three successful build logs, `reuse-audit.json`, `arm-readelf.txt`, `vita-elf-create.txt`, postprocessed checks and `summary.json`. ZIP/EXE/music/GMK/GML/helper hashes and E015 binary remain unchanged. **New resources recovered: zero**; prior 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms preserved.
