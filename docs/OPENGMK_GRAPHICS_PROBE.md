# E020 — native libvita2d/GXM renderer attached to the existing VM

**2026-11-25 UTC / 2026-11-24 America/Bogota. VERIFIED:** initial libvita2d/GXM backend **renders the authentic engine-loaded game logo on the owner's physical Vita 1000**, including scale, rotation, transparency and batching, without vitaGL. Owner observation, GPU readback, persistent log and installed SELF identity agree. The strict loader, original compiler/VM, collision masks and event trees are retained. **Native startup still stops at `Process/set_program_priority` after 15 instructions; no playable/functional game VPK or original-menu execution is established.** Private diagnostic identity: **HOWAW1178 / 00.21**.

## What the game requires

`RendererTrait` at pinned upstream `9e4282e6d19f4dd00961811840ddc3e11da6dd5a` has **108 methods: 103 required, five defaults**. It includes much more than this game's current evidence justifies implementing. `audit_graphics.py` examines the existing recovered-code inventory without exporting or printing GML. **VERIFIED static presence:** 1,622 graphics-related call sites across 24 functions:

| Operation | Static call sites | Initial backend / remaining work |
| --- | ---: | --- |
| `draw_sprite`, `draw_sprite_ext`, `draw_sprite_part` | 216 / 582 / 36 | Atlas lookup, crop, origin, scale/mirror, rotation, uniform tint/alpha and contiguous batching implemented |
| Background / tiled / tiled-ext | 4 / 17 / 1 | Existing sprite/tile defaults reused; view/presentation integration still required |
| Text / coloured text | 220 / 9 | Existing engine glyph-to-sprite path retained; original menu needs view/state and colour-gradient coverage |
| Rectangle / coloured rectangle | 106 / 70 | Explicit unsupported stop; no placeholder success |
| Line / width / width-colour | 11 / 1 / 2 | Explicit unsupported stop |
| Coloured circles | 5 | Explicit unsupported stop |
| Blend mode / draw alpha | 44 / 78 | Default libvita2d alpha blend only; additive switching remains required |
| Pixel reads; screenshot; background from screen | 5 / 1 / 1 | Explicit unsupported stop; diagnostic readback is separate |

Colour/font/alignment setters account for the other sites. No direct `d3d_*`, surface or custom primitive calls were found in this lexical scan. **This is not runtime coverage or proof that those features can never be needed.** Engine default object/tile/particle drawing, DnD actions, indirect calls and actual blend arguments need execution evidence. Existing E015 PC gameplay is preserved, not rerun or used as a device-performance claim.

## libvita2d versus direct GXM

| Concern | Installed libvita2d | Direct SceGxm |
| --- | --- | --- |
| Initial 2D sprite path | Existing shaders, texture allocation, tint, textured arrays, normal/additive blend and display lifecycle | Requires shader/patcher setup, buffers, synchronization and display lifecycle |
| Batching | One textured triangle-array call per contiguous atlas/tint group; preserve draw order | More control over vertex formats and per-vertex tint, potentially fewer state changes |
| Memory | Existing display/ring/pool overhead; mapped texture allocations can be measured | Could reduce overhead after measurements justify the added ownership/cleanup code |
| Missing fidelity | Arbitrary blend factors, gradients and engine framebuffer/view semantics need extensions | Full control, with more implementation and validation work |

**INFERRED choice:** libvita2d over GXM is the smallest maintainable initial backend. No measured comparison establishes it as the fastest final backend. The C ABI is narrow enough to add direct GXM operations where real menu traces require them. No vitaGL, SDL renderer, new crate, runtime download, proprietary shader compiler or external-project modification is used.

Primary references: [pinned OpenGMK renderer trait](https://github.com/OpenGMK/OpenGMK/blob/9e4282e6d19f4dd00961811840ddc3e11da6dd5a/gm8emulator/src/render.rs), [libvita2d textured arrays](https://github.com/xerpi/libvita2d/blob/master/libvita2d/source/vita2d_texture.c), [libvita2d lifecycle](https://github.com/xerpi/libvita2d/blob/master/libvita2d/source/vita2d.c). The installed archive has no established source commit: **local header/API, symbols and stride disassembly verified; exact equivalence to current upstream source UNTESTED.** Header SHA-256 `9711db79dc78a4264e3f467444423aee3d664b79fb713a1b5a1425269ea3a5d9`; archive `c5857b65ea7a93f6ff37f29abd84ed2fe1d6faca9bcf9a83a60e33e110b69e99`.

## Actual integration and startup obligations

`prepare_graphics_probe.py` reproduces E019 with its existing owner-selected High policy in a **fresh** tree. Feature `vita2d` selects the new `RendererTrait` implementation at the same `Game::launch` atlas handoff. The original sprite/background builtins reach that trait under the new feature; the desktop path and original GML are preserved. Seven required trait methods are implemented; **96 required operations still stop explicitly**, alongside unsupported presentation/crop/colour cases in implemented methods. Five upstream defaults are retained; some reach unsupported methods, such as `dump_sprite_part`.

The diagnostic calls unchanged `Game::init` first and records its exact result. **It neither bypasses the priority call nor resumes the failed VM.** After the stop, it accesses original sprite 0/frame 0 in that same `Game`, checks its prepared bytes and draws through `game.renderer`. Thus this is an engine-resource/backend test, **not execution of the menu's Draw events**. Removing this diagnostic harness later does not require replacing the renderer or resource IDs.

Host **VERIFIED:** 181 scripts, 1,661 top-level script instructions, 233 objects / 845 event trees; 16 VM instructions, real Windows High readback `(128,2)`, then Files stop. Original sprite 0 is **343×76**, origin **171,38**, `AtlasRef(110)`, page 0; 104,272 BGRA bytes, **22,028 nonopaque pixels**, SHA-256 `95d23a60b97a0004f32d86c437bb26523becf9f8d741b9ad8ce735620d79963b`. Host GPU execution explicitly unavailable; no substitute renderer runs.

Menu integration sequence remains concrete: resolve the Process contract without claiming a Windows scheduler equivalent; service real file/INI requests with preserved data; supply real window/input/audio services; then unchanged `load_room`/Create/Draw events reach `RendererTrait`. The first room is **640×325, speed 30** in the original data. Its view/framebuffer mapping, state queries, rectangles, text and blend transitions must be supported before claiming the original menu. The current diagnostic accepts only a native 960×544 presentation with `Scaling::Fixed(1)`; matrices, viewport mapping, dynamic textures, surfaces and readback builtins still block. Neither 30 FPS nor menu scaling is achieved by selecting the display size.

## Resource ownership and diagnostics

- Retain the upstream atlas packing and `AtlasRef` metadata. Initially **3,003 entries / 71,602,980 CPU pixel bytes**; the collision data remains independent and unchanged.
- Allocate a GPU page only when first drawn. Validate every source length and rectangle before writing directly into its mapped texture, converting **BGRA to RGBA** row-by-row with the actual stride. No temporary atlas-sized buffer or second decode is made.
- Release that page's CPU payloads only after successful allocation/copy. Cache the mapped texture by page; repeated sprites use the same allocation. No eviction policy or all-game memory-fit claim yet.
- Batch consecutive triangles by page and uniform tint; do not sort transparent draws. At most 256 quads per batch, 256 KiB libvita2d temporary pool; pool exhaustion is an error. Finish GPU/display work before pool reuse or texture release. This intentionally conservative synchronization is a correctness baseline to measure, not a performance optimization claim.
- Capture errors from wrapped GXM initialization, texture initialization, scene begin/draw/end, queue submission and display framebuffer assignment. Some internal libvita2d initialization calls still discard status; its success return alone is insufficient evidence. Pool/texture/null/bounds errors stop. No universal GXM error coverage is claimed.
- Persistent new `e020-NNN/run.log` records original startup, heap/system-free memory, mapped texture size, page uploads, batches, GPU framebuffer hashes/non-clear pixels and wait-inclusive frame times. GPU readback and submitted frames do not establish physical display observation or gameplay FPS.

The visual diagnostic submits 120 frames with the original sprite at native scale, followed by 240 with four instances using half-scale, rotation and alpha 0.5. It uses no replacement art or fabricated menu. First upload/log time is included in the first frame sample; readback is outside samples.

## Physical test — PASS bounded graphics, startup remains BLOCKED

Owner installed/launched 00.21 and reported the game logo, then four differently transformed copies. FTP retrieval after exit and independent validation completed **2026-11-25 02:17:02 UTC**. Installed SFO **HOWAW1178 / 00.21** and SELF SHA-256 match the package. Persistent log SHA-256: `2b94b1bdc1143395db45dc5a32ae0ec5731cf39843822cbb20744dbd24c56340`. Firmware unreported; model is the owner's Vita 1000 established in E019.

**VERIFIED:** strict EXE hash, 181 compiled scripts / 845 events, same owner High policy, **15 original VM instructions / five traced calls**, honest Process error before graphics. The original resource hash matches PC. Native graphics init reports rc=0; GPU readbacks contain **12,625** and **12,337** non-clear RGB pixels, hashes `13fe4c52ff110f535f5606066d45f58507ebf71937cc635f7c8e6e634ab84a5d` / `3ced5610711e44a40fa845386c35c5ea1015de48c67ad5c05fa431a2b544993f`. These plus the owner's visual report establish useful native rendering; pixel-perfect parity with the original Windows runner is **UNTESTED**.

| Device measurement | Observed value / scope |
| --- | --- |
| Submitted visual frames / sprite submissions / sprite batches | **360 / 1,080 / 600**; original gameplay frames not executed |
| Atlas page uploads | **1**, across the whole test; six packed pages exist, five remain unallocated on GPU |
| GPU texture mapped allocation | **16,777,216 B (16 MiB)**, queried through the kernel |
| CPU texture bytes before → after | **71,602,980 → 56,355,908 B**; **15,247,072 B** released after upload |
| Requested Rust heap at startup stop → visual end | **94,016,533 → 78,772,341 B**; lifetime peak **108,104,996 B (~103.1 MiB)** |
| System free user before GXM → after GXM / visual end | **124,780,544 → 115,343,360 B**; down 9 MiB |
| System free CDRAM before GXM → after init → after page upload | **117,440,512 → 94,371,840 → 77,594,624 B**; init down 22 MiB, texture another 16 MiB |
| System free physical-contiguous | **27,262,976 B** at recorded boundaries |
| Wait-inclusive frame time min / median / p95 / max | **12.536 / 16.680 / 16.720 / 1,050.490 ms**; max includes initialization/upload/logging |
| Entire visual interval | **8,391,316 µs**, including out-of-sample hash/readback/log work |

These are measured **diagnostic submission/wait times**, not displayed FPS, game frametimes or a 30/60 FPS gameplay result. Rust counters exclude C allocations, allocator overhead and GPU allocations; free kernel pools are separate, non-additive figures. At teardown system free user/CDRAM return to **124,780,544 / 117,440,512 B** and requested Rust live heap to **1,088 B**. This supports resource cleanup for **one launch**, not an extended leak/stability claim.

**Important capacity limit, INFERRED from verified packing/free-memory:** all six 2048² RGBA pages would require **96 MiB** of texture allocation. This run has only **90 MiB free CDRAM after GXM initialization**, before textures. The current backend's lazy cache fits this test, but cannot be assumed to keep every page resident at once. Measure the original menu/arena page working set before deciding on compaction, backing storage or eviction; no game assets have been reduced or discarded. No all-pages allocation/failure trial was performed.

The log ends with `VISUAL_PROBE_COMPLETED`, the preserved Process stop and **DIAGNOSTIC_END exit_code=2**. No graphics failure, panic, allocation failure or false native priority-success marker appears. Closing after the visual sequence is the documented startup stop, not evidence of a menu boot or crash.

## Reproduce and checks

Same offline Rust/Cargo **1.100.0**, Python **3.14.4**, MSVC **14.50.35717**, WSL hard-float VitaSDK GCC **15.2.0** as E019. Existing private Rust homes and WSL linker are reused; external SDKs remain read only. Use fresh output directories:

```powershell
python tools/opengmk/audit_graphics.py --code recovered/session-20261122/audit/code.txt --source local-tools/menu-probe-20261122/OpenGMK --report reports/local/NEW/graphics-audit.json
python tools/opengmk/prepare_graphics_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/NEW/OpenGMK
python tools/opengmk/prepare_graphics_native.py --output build/NEW-native
```

`prepare_graphics_native.py` records the exact C compile/archive/copy commands and hashes privately. It uses `-mfloat-abi=hard -std=c11 -O2 -Wall -Wextra -Werror`; required archives are copied locally because Windows rustc cannot bundle files visible only inside WSL. Shared-framebuffer imports are in **SceAppMgr**, not a separate SceSharedFb archive. Set `HOWAW_GRAPHICS_LIB_DIR` to the absolute NEW-native output. Reuse E019's process-local Rust homes, scalar ARM/no-LTO/no-strip/WSL-linker settings, with fresh target directories:

```powershell
cargo build --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --manifest-path local-tools/NEW/OpenGMK/Cargo.toml
cargo build --offline --locked -Z build-std=std,panic_abort --release --target armv7-sony-vita-newlibeabihf -p gm8emulator --no-default-features --features vita2d --bin howaw-vm-probe --manifest-path local-tools/NEW/OpenGMK/Cargo.toml
cargo check --offline --locked --release --target i686-pc-windows-msvc -p gm8emulator --lib --manifest-path local-tools/NEW/OpenGMK/Cargo.toml
```

Original-data test used:

```powershell
python tools/opengmk/run_vm_probe.py --runtime build/graphics20-host/i686-pc-windows-msvc/release/howaw-vm-probe.exe --input-dir recovered/native-probe-20261123/pc-profile --run-name startup-owner-high --experiment graphics-probe-20261124 --owner-dialog-high --expected-service Files --expected-operation file_exists --require-persistent --diagnostic-prefix e020
```

CPU contracts use the same existing x86 MSVC environment:

```powershell
rustc --test --edition 2021 --target i686-pc-windows-msvc tools/opengmk/graphics/geometry.rs -o build/graphics20-native/geometry-tests.exe
build/graphics20-native/geometry-tests.exe
```

**PASS:** two CPU contracts (crop/origin/rotation/mirror and BGRA/stride/alpha/padding), C hard-float compile with `-Werror`, first host build **1m36s**, original-data host run (child 2 / launcher 0), source-reuse audit **22/22**, final fresh preparation **194/194 identical files**, default desktop library check **31.35s**, ARM ELF/link and VELF conversion. Lockfile unchanged. Initial reproduction exposed only a stale copied bridge source and a whitespace difference; corrected final reproduction is byte-identical.

**Failures retained:** ARM attempt 1 failed because Windows rustc could not find the WSL `vita2d` archive. Attempt 2 failed on the incorrectly assumed `SceSharedFb_stub`; local symbol inspection identified SceAppMgr as the provider. Attempt 3 passed (**46.90s** incremental); a final bin rebuild (**15.33s**) corrected the timing-label wording before packaging. No failed build is presented as a successful device run.

Private package commands use existing WSL `vita-elf-create INPUT.elf OUTPUT.velf`, then:

```powershell
python tools/opengmk/package_priority_probe.py --prepare --experiment E020 --elf build/graphics20-arm/armv7-sony-vita-newlibeabihf/release/howaw-vm-probe.elf --velf build/graphics20-arm/howaw-vm-probe.velf --output build/graphics20-device
python tools/opengmk/package_priority_probe.py --package --experiment E020 --output build/graphics20-device --title-id HOWAW1178 --app-version 00.21
```

VPK **only SELF + SFO**, no original game data. ELF **4,631,232 B**, SHA-256 `e45761bcdaa48d5360cc782647d0b2eebdc52d1efe40bb0937ebf6bab2fd258f`; VELF **5,460,994 B**, `9ca700fd5c5e256e01f5b08b193d6ef1ff588c438bb6a287ec483cd12931942c`. VPK **2,231,083 B**, SHA-256 `9726020a1ccbb198f0015b07376dd07386fa8b0e65c501db60992535b2ab09b5`; SELF `c90425199e65bc58d1a7810f89ba929044bf37f38df5a1ec932abb2f98f65cd2`. FTP transfer/remote input hash and installed SFO/SELF identity **PASS**. Owner installed/executed; previous VPKs, EXE, MP3, saves and diagnostic directories preserved.

Ignored evidence: `reports/local/graphics-probe-20261124/`, `build/graphics20-*`, fresh source `local-tools/graphics-probe-20261124/`. **New recovery: zero**; prior 693 sprites / 128 sounds / 181 scripts / 233 objects / 845 events / 15 rooms preserved. No public binary/asset distribution or phase advancement.

**Next one high-information experiment:** resolve the native priority failure contract against the reviewed original routine, which issues both Windows priority calls without checking their return values. Determine how to represent an unsupported native effect under the actual GM8 void/return contract, with an explicit capability/result log and no claim of successful scheduling; validate that contract before resuming unchanged startup to the next real service. Until justified, keep the current Process error. This is the gate to real room/Create/Draw execution; do not repeat the already successful logo test. Native file/save, window/input/audio and the renderer's view/primitive/gradient/blend gaps remain required for the original menu.
