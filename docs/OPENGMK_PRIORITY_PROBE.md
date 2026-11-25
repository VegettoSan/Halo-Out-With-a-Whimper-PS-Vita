# E019 — verified priority service and persistent native VM diagnostic

**E021 follow-up:** [Reviewed failure contract and persistent startup services](OPENGMK_STARTUP_SERVICES_PROBE.md) supersede E019's deliberately strict error boundary: the original priority procedure does not test either Windows API result or write a GML status. A hash-checked bounded original-procedure test with real API failures confirms both calls and unchanged result slot. Native completion logs unavailable effects, never scheduler success; original startup advances to sound_replace. E019's earlier runs/artifacts and their Process stop remain historical evidence.

**2026-11-24 UTC (2026-11-23 owner local). VERIFIED:** original PC startup executes **16 instructions**, including real process/thread priority changes, then stops at **`file_exists` / Files**. The same real loader/compiler/VM **ran on the owner's physical Vita 1000**: original EXE hash verified, 181 scripts / 845 events compiled, first **11 original GML instructions** to Dialog, then **15** with the owner's explicitly requested High policy to Process. Owner selected **HOWAW1178** and installed both private diagnostics via VitaShell FTP. **This is native VM-prefix execution, not a playable game VPK.**

## Contract and PC result

Static inspection of the unchanged original EXE identifies the registered function and verifies its switch table and imported API thunks. It calls **both** `SetPriorityClass(GetCurrentProcess(), ...)` and `SetThreadPriority(GetCurrentThread(), ...)`, in that order. Original GML has exactly three call sites: Low → 0, Medium → 1, High → 2. No scripts/events/resources were modified or recovered anew.

| GML integer | Windows process class | Current thread relative priority |
| ---: | --- | ---: |
| -3 | IDLE (`0x40`) | -15 |
| -2 | NORMAL (`0x20`) | -2 |
| -1 | NORMAL | -1 |
| 0 / other integers | NORMAL | 0 |
| 1 | NORMAL | +1 |
| 2 | HIGH (`0x80`) | +2 |
| 3 | REALTIME (`0x100`) | +15 |

This table is **VERIFIED from this runner**, not a guess from the dialog labels. The [original GM8 manual, mirrored](https://documentation.help/Game-Maker-8/403_11_misc.html) describes the -3…3 range; Microsoft's [process](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setpriorityclass) and [thread API contracts](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setthreadpriority) distinguish the two operations. Existing GML argument conversion/arity validation is retained; float/coercion equivalence to every proprietary-runner edge case is not newly established.

The typed `PlatformServices` operation performs both OS calls and reads back both properties. Any API failure, partial effect or readback mismatch is an error; GML default return is produced only after verified work. Vita explicitly returns `SERVICE_UNAVAILABLE/Process`; **no process-class/thread-priority equivalence is invented**. The preserved desktop E015 path is unchanged; upstream's old desktop no-op is not used by this diagnostic provider.

**PASS Windows service test:** 0 → `(32,0)`, 1 → `(32,1)`, 2 → `(128,2)`, through PlatformServices in a bounded child; previous `(32,0)` restored and read back. Other table entries checked without applying real-time scheduling. **PASS original startup**, `03:59:32.125–04:00:00.669Z`: owner selected High/result 3; modal counter 11→11 during 26,728 ms; original GML passed 2; actual readback `(128,2)`; **16 instructions / 6 traced service calls**, then honest `Files/file_exists` stop. Child exit 2, launcher 0; persisted log independently passes the same checks. No automatic answer or file result supplied.

## Persistent diagnostic and ARM evidence

The diagnostic creates a fresh `ux0:data/howaw/diagnostics/e019-NNN/run.log` and workspace for every launch, preserving prior logs/temp data. Each record writes and `sync_all`s the file. **VERIFIED:** native newlib `fsync` invokes `sceIoSyncByFd`, and the first physical log was retrieved after application exit. Failure to open/write/synchronize is not counted as diagnostic success.

Records cover: VitaSDK CRT reaching Rust main; explicit existing-default **128 MiB newlib heap configuration**; NET module load/status (required retained imports); kernel/IO/RTC/RNG import obligations; original EXE open/size/**SHA-256** before interpretation; loader and script/event compilation stages; VM counts; external binding/results; real dialog/priority requests; requested heap peaks and allocation failures; separate SDK free-memory snapshots; exact errors/panic location and exit. SHA-256 uses the existing input buffer without copying it; three known vectors and the full original EXE hash pass on PC. Panic-abort still invokes the persistent hook; crashes before Rust/log creation cannot be diagnosed by that hook. No socket stack, graphics or audio success is simulated.

- **PASS** first PC build 59.37 s; first ARM build/link 1m14s; default desktop check 23.88 s. Same offline Rust/Cargo 1.100.0, MSVC 14.50.35717, Python 3.14.4 and WSL hard-float VitaSDK GCC 15.2.0/settings as E018; no downloads/installations/new crate.
- **PASS** reuse audit 22/22; pristine compiler/events/collisions and original VM plus existing counter; unchanged lockfile; fresh preparation matches all **189** tested files. Modal/INI patches and E015 playable binary unchanged; audio unchanged, continuity uncertainty retained.
- **PASS** ELF32 ARMv7 EABI5 hard-float/Thumb-2 and `vita-elf-create -v`: ELF **4,514,548 B**, SHA-256 `0b122d798cb38cea218672f8864eea01ea52d0330c677a309c0cf5fb6155bcc2`; VELF **5,322,870 B**, `de124dd57882bc5f597cf84cc37362e23fc94afab45679d36d861253708c9444`. **77 native import stubs / 10 libraries**; includes the real synchronization/module/free-memory APIs. Imports are obligations, not exercised coverage.
- **PASS private packaging only:** safe SELF **5,326,966 B**, SHA-256 `ba1dc242d4b4d2ca31b667bbe0b59295e8bb4711a2401252901d79bcd3e780ca`; owner-ID VPK **2,171,594 B**, `0aba2bbe659b573526630c5c1182d996fb6c4d94fe814a594d96661a9e137f99`. ZIP CRC/member/SFO review passes: only `eboot.bin` and `sce_sys/param.sfo`, TITLE_ID HOWAW1178, no game data. Missing-ID packaging was rejected before owner selection; no arbitrary ID used.
- **PC memory only:** requested Rust heap peak **108,105,286 B (~103.1 MiB)**, compiled Game 93,998,148 B, stop 94,000,173 B, 165,859 allocations / one >=4 MiB; unchanged pending CPU textures 71,602,980 B. Excludes C/allocator overhead, stacks and GPU. Neither this nor configured heap size establishes Vita use/fit.

## Reproduce and first physical test

Use fresh directories. `prepare_priority_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/priority-probe-20261123/OpenGMK` reuses E018 from pinned pristine upstream. Reuse [E018's exact environment/build commands](OPENGMK_CLEANMEM_PROBE.md#reproduce-without-repeating-baseline-setup), substituting this manifest, new build/priority19-* target directories, and host `--bin priority-contract-probe` in place of the CleanMem contract bin. ARM still builds `--bin howaw-vm-probe` with no default features, headless and build-std=std,panic_abort. No baseline rebuild is required for deployment.

```powershell
build/priority19-host/i686-pc-windows-msvc/release/priority-contract-probe.exe
python tools/opengmk/run_vm_probe.py --runtime build/priority19-host/i686-pc-windows-msvc/release/howaw-vm-probe.exe --input-dir recovered/native-probe-20261123/pc-profile --run-name startup-interactive --experiment priority-probe-20261123 --interactive-dialog --require-persistent
python tools/opengmk/package_priority_probe.py --prepare --elf build/priority19-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.elf --velf build/priority19-arm/howaw-vm-probe.velf --output build/priority19-device
python tools/opengmk/package_priority_probe.py --package --output build/priority19-device --title-id HOWAW1178
```

**Justified diagnostic goal:** install the private package via VitaShell, place the owner's unchanged EXE at `ux0:data/howaw/HOWaW_FirefightDemov1.exe` (SHA-256 `cf0661731e049371f30d2e953dcbad7236eb83c93f0b615fa819dbe913d8773f`), and run the real VM. There is no rendered frontend; return to LiveArea does not by itself mean success. Retrieve `ux0:data/howaw/diagnostics/e019-NNN/run.log` through FTP. Firmware/model and actual results must be recorded before device conclusions.

**Expected, INFERRED from PC:** native SHA/strict load and compilation of 181 scripts / 845 event trees; CleanMem explicitly reports unsupported Windows trim/failure 0 with separate free-memory diagnostics; VM executes original startup until the real `show_message_ext` request at 11 instructions, then returns explicit Dialog unavailability. Native priority must stay unavailable. A module/load/allocator/path failure is useful FAIL/BLOCKED evidence, not a successful boot. No graphics/menu/playability claim follows from this diagnostic VPK.

## First physical execution — PASS bounded prefix, BLOCKED real dialog

**VERIFIED:** uploaded EXE/VPK hashes checked through FTP; owner installed/launched on Vita 1000 and reported black screen followed by closure. Retrieved the persisted log after exit and independently verified the installed SELF hash matches `ba1dc242d4b4d2ca31b667bbe0b59295e8bb4711a2401252901d79bcd3e780ca`. Firmware not reported. Retrieval/validation finished `04:10:36.749Z`. Log SHA-256 `27c4a8a3ab8a1489028ec4c34eedadf69598ebe62cded5aedb090b0aae72cdcd`.

Native log confirms Rust entry/CRT, NET module load result 0 and loaded status 0, unchanged EXE SHA-256, strict load, 181 scripts / 1,661 top-level script instructions / 233 objects / 845 event trees, both CleanMem bindings and its explicitly unsupported cleanup return 0. VM executes **11 instructions / 4 traced calls** and returns `show_message_ext: SERVICE_UNAVAILABLE/Dialog`, **DIAGNOSTIC_END exit_code=2**. No panic/allocation-failure marker appears. Thus closure is the planned service stop, not evidence of a crash or a menu boot. Native priority remains unimplemented and was not reached in this first run.

**Measurements on Vita, distinct from PC:** requested Rust heap peak **108,104,996 B (~103.1 MiB)**; compiled Game **93,983,612 B**, stop **93,985,445 B**, 166,459 allocation requests / one >=4 MiB. SDK free-memory queries return rc=0: user **125,829,120 B (120 MiB)**, CDRAM **117,440,512 B (112 MiB)**, physical-contiguous **27,262,976 B (26 MiB)** at recorded boundaries. These are system-free counters, not process consumption or mutually additive application budgets. Constant readings while malloc requests change are consistent with the inspected reserved newlib heap; total process RAM/allocator overhead/GPU headroom are not measured. No rendered frame/audio output or full-game fit claim.

The original `Music/menu.mp3` was subsequently copied separately at the owner's request and remote SHA-256 verified (`e2ef65a3cceea8d26bbf69a036372cf50889fc439b06f61026b9673a0a0a65d0`). File availability does not supply the still-missing native audio backend.

**Owner-requested follow-up policy:** after the first physical run the owner explicitly selected **High/button 3** as an automatic diagnostic response. A separately prepared revision (`--owner-dialog-high`) records `OWNER_POLICY_HIGH` and answers only the first real startup dialog; empty/missing third button or subsequent dialog is rejected. Default preparer/PC manual mode remain unchanged. This intentionally configured response is not described as manual UI or original interaction parity. The next expected native stop is the still-unavailable Process priority service. First-run evidence/artifacts are retained.

**VERIFIED follow-up:** policy host build 59.11 s, ARM 1m14s, ELF inspection and VELF conversion PASS first attempts. PC `04:15:47.638–04:15:49.467Z` uses `--owner-dialog-high` (no `--interactive-dialog`), persistent policy log + actual Windows priority readback, 16 instructions, same Files stop. Reuse audit 22/22; fresh policy preparation matches **190** files. No extra desktop change or repeated gameplay trial.

Owner installed/launched **00.20**, which was retrieved/validated by `04:18:13.333Z`: installed SFO HOWAW1178/00.20 and SELF SHA-256 match; native policy log SHA-256 `021ea5b8af850777e643c8ad66d027cd99bd0d6baeceaed26a43c7a609ccde1b`. **15 instructions / 5 calls**, owner High result 3 at instruction 11, real priority request 2; honest `SERVICE_UNAVAILABLE/Process` stop and exit 2, no panic/allocation failure or false OS-success marker. Native heap peak remains **108,104,996 B**, stop live **93,985,641 B**, 166,463 allocations; SDK free counters unchanged. No additional physical rerun is needed to establish this bounded result.

Final preserved artifacts under `build/priority19a-*`: ELF **4,515,192 B**, SHA-256 `4de8783238e485882249f77a56a05c6b236a8e1b724a3a5daa6d9394b7b174a4`; VELF **5,323,778 B**, `7d1854d0a64d38d8d2b697002dd5da2366a32fe467cc592ce15117205c2dae5c`; SELF **5,327,874 B**, `d285501fc7e8e441c2b9526f4f94eec6ac41ccc5edf70b6781c91ce78310b4cb`; private VPK **2,172,024 B**, `4bdda7c380c52315da314fc0a4f6030e9a14c46fedfc3e4adbfaee754275663a`. Reproduce this revision with preparer `--owner-dialog-high`, fresh policy output/target directories, launcher `--owner-dialog-high --expected-service Files --expected-operation file_exists --require-persistent`, and package `--app-version 00.20`. The VPK contains only SELF/SFO; original MP3/EXE are separate private device data.

Next PC gate is `file_exists`/save-path semantics. Next native gate after policy validation is a genuine dialog/control frontend and an honest priority-service policy, followed by useful rendering/audio. Do not infer playability from the diagnostic installation or native prefix.

Private evidence: `reports/local/priority-probe-20261123/` static contract/PE audit, builds, contract result, both PC startup captures, reuse audits, ELF/VELF/fsync inspection, package review, device uploads, **device-run-1/** and **device-run-2/** logs, installed-binary validation and final-summary.json. Original and policy SELF/SFO/VPK remain in separate ignored build directories. FTP NLST initially returned 502; supported LIST succeeded, without runtime change. No private logs/binaries were committed. **New recovered resources zero**; original hashes/GML and prior 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms preserved.
