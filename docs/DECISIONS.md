# Architecture decision log

## ADR-000 — 2026-11-22: do not select engine yet

**Status:** Accepted for initial research (not a runtime implementation).

**Context:** Original input is a Windows x86 GameMaker-family executable with no separately supplied source project. Vita is ARMv7. A direct copy of the EXE cannot run.

**Decision:** Compare (A) Win32/x86 translation, (B) GML/game data recovery + compatible runner and (C) static recompilation using reproducible small experiments. Preserve original logic/data rather than recreate game systems.

**Not decided:** GameMaker exact version, VitaSDK backend, SDL2/OpenGMK adoption, title ID, final renderer, distribution method or performance target achievement.

**Revisit when:** successful extraction test, explicit PE imports/loader analysis and at least one genuine interaction running in a compatible runtime have been documented.

## ADR-001 — 2026-11-23 UTC: prioritize route B's PC compatibility probe

**Status:** Provisional research priority; no Vita runtime selected and no P2 authorization implied.

**VERIFIED:** strict GM8Decompiler recovery and an independent GMK reader agree on 693 sprites, 128 sounds, 181 scripts, 233 objects and 15 rooms. Original GML reaches startup in OpenGMK 0.2.0, then fails at the unsupported `show_message_ext` builtin. WinVita's host loader maps the original PE and its 535 import entries, but no guest code has run under it. D3D8 support is absent from the supplied runtime source, and its DirectDraw creation shim returns an error. See E003–E010 and [technical audit](TECHNICAL_AUDIT.md).

| Criterion | A: original x86 runner + WinVita | B: original gamedata/GML + compatible runtime | C: static runner recompilation |
| --- | --- | --- | --- |
| Reuse | Original runner, GML and assets potentially retained; loader-only proof | Game data/GML structurally recovered; original startup logic executed on PC | Potential runner reuse; no translation proof |
| Fidelity | INFERRED strongest runner-semantic potential; OS/graphics replacements still affect behavior | INFERRED good logic reuse; requires semantic, collision, font/audio and timing comparisons | UNTESTED; same OS/graphics obligations plus translation correctness |
| Concrete obstacles | D3D8/device vtables, Win32/COM breadth, MCI, DLL/exception/TLS behavior | `show_message_ext` first; native backends and x86 CleanMem API adaptation | Opaque runner, indirect dispatch and OS bridges; no measured advantage |
| Complexity | INFERRED very high, several large subsystems; multi-month planning scale for one experienced developer | INFERRED lower cost for next PC experiment; substantial Vita work remains, no reliable duration yet | INFERRED highest uncertainty; defer |
| Vita performance | UNTESTED dynarec/bridge/JIT/memory costs; no transferable Diablo FPS claim | UNTESTED; avoids translating original x86 runner but interpreter/GPU/asset costs remain | UNTESTED; static code alone does not establish speed |

**Decision:** spend the next bounded experiment on a faithful implementation of `show_message_ext` in a **private compatible-runtime source copy**, retaining the original EXE/GML. Present the actual three choices and preserve return semantics; do not hard-code a return value or delete the game's call. Run the exact original copied EXE again, recording whether it reaches its real menu or the next blocker. Obtain a matching source/toolchain only if missing; no reinstall of existing binaries is warranted. Current upstream inspection also shows this builtin unimplemented.

**Why provisional:** successful recovery is not gameplay parity. An exact vendor runner patch/build has not been established beyond verified 8.0. PC menu/arena and physical Vita tests are still absent. Route A is retained because WinVita now provides a genuine loader/translation foundation; graphics and Windows compatibility costs remain unsupported by execution.

**Licenses:** local WinVita LICENSE is MIT with separately listed third-party notices; D2Vita is GPL-3.0; inspected OpenGMK runner Cargo metadata says GPL-2.0-only; Gmk-Splitter LICENSE says GPL-3.0-or-later. These are component observations, not distribution clearance. Keep reference code, original game data and recovered GML private; review the actual versions before incorporating/distributing anything. No proprietary resources from other ports were used.

**Revisit:** after an unmodified-data PC run demonstrates a real menu and one interaction, or a newly observed runtime limitation changes B's cost. Do not build a Vita VPK just to demonstrate a loader or placeholder screen.

## ADR-002 — 2026-11-23 UTC: route B has a real PC menu proof

**Status:** Accepted research result; final Vita architecture remains undecided.

**VERIFIED:** E011–E014 implemented the missing modal builtin in an OpenGMK working copy, tested all three button values and Escape, and ran the original EXE unchanged. The real main menu, Firefight map selection and difficulty selection responded to keyboard/mouse input. Normal window closure returned exit 0. E007's original failure and the unsuccessful first build remain in the log.

**Decision:** retain route B as the next research priority. A native Windows dialog and a successful PC renderer do not establish a Vita backend. Keep WinVita available without expanding this session into D3D8 development. No GML rewriting, binary game patching or asset substitution was needed for this milestone.

**Next discriminating test:** one original Firefight arena on PC, verifying movement, one weapon action, enemy spawning and audio, with bounded runtime-only fixes for any observed blocker. Physical Vita, performance, suspend/resume and persistent-save claims remain unsupported. No VPK packaging is justified by this menu-only result.

## ADR-003 — 2026-11-23 UTC: preliminary PC gameplay base established

**Status:** Accepted evidence for backend planning; no final Vita viability decision or phase completion.

**VERIFIED E015:** original Site 117 loads; owner-operated movement/jump, aim/fire, collisions and damage work. Enemies, projectiles, respawns, pause/resume and postgame return were observed. Original EXE/GML/resources stay unchanged. Runtime INI write-through fixes default-profile visibility and the cycling-helmet symptom; exact proprietary-runner INI behavior remains inferred. The initially reported audio cuts were not noticeable in the owner's later test, but their cause remains unresolved; no speculative audio fix is adopted.

**Decision:** OpenGMK is a credible **initial PC gameplay base** for designing native Vita rendering/input/audio/file adapters while retaining original logic. Do not interpret this as demonstrated ARM compilation, Vita RAM fit, full parity, stable frame pacing or release readiness. Keep WinVita dormant; no new renderer investigation is justified by the current evidence.

**Next gate:** restart/profile persistence, repeatable audio continuity and a bounded gameplay regression. Process memory peaks (~239–258 MiB on this Windows host) warrant measurement and allocation analysis before a native device prototype, without assuming these translate directly to Vita. Physical Escape ended computer control; the restart test was not completed. No VPK generated.

## ADR-004 — 2026-11-24 UTC: native OpenGMK subset viable; full runtime requires adapters

**Status:** accepted research direction, provisional native implementation boundary. Owner requested this feasibility work; no publication or packaging authorization implied.

**VERIFIED E016:** PC profile survives process exit/restart with new temp/profile; EVA/Elite restored, saved INI hash unchanged. Existing runtime/audio untouched. Audio underrun notifications recur (0/744 across differing workloads), so continuity remains unresolved. Strict reader/parser and independent math/RNG/atlas modules compile for Vita ARMv7; real-data diagnostic links hard-float ELF and converts to VELF. Host execution loads original data and parses 1,073 nonempty GML units with zero syntax errors. **Full VM/game ARM execution remains BLOCKED.**

**Decision:** continue route B through the existing compiler/VM and native platform services. Reuse installed hard-float WSL SDK; use scalar Rust decompression initially after measured simd-adler32 failure; disable incompatible symbol stripping for relocation conversion. Do not reinstall SDKs or require cargo-vita merely to wrap the demonstrated build. Keep source/dependency baselines and earlier failures. No final graphics backend selected: prototype a real `RendererTrait` implementation against installed vitaGL after exact shader/readback checks, with direct GXM available if that fails. No mandatory kernel plugin adopted.

**Concrete blockers:** full runner's clipboard/X11/xcb dependency fails the Windows cross-build; ramen has no Vita host; GL 3.3/GLSL330/GLX cannot be treated as compatible with vitaGL; libsoundio has no Vita sink; non-x86 CleanMem calls would launch a wow64/Wine helper. `Game` couples compiler/VM to these services, so the full interpreter is not yet an independently compiled library. Keep original room/object/weapon/collision logic; change the host seams, not GML.

**Memory:** 83.2 MiB original payload and 80 MiB candidate sprite/background atlas capacity establish a concrete peak-allocation risk, not Vita RAM consumption or a failed fit test. Measure allocation lifetime and device headroom before asset changes. No performance estimate or phase completion is justified.

**Next gate:** compile the unchanged scripts/events and execute original startup through explicit native host services to the actual modal request, capturing first unsupported call/heap peak; then attach useful native graphics/input/audio. [Evidence, reproducible commands and staged prototype plan](OPENGMK_NATIVE_PROBE.md). A/C remain alternatives without new execution evidence. No functional VPK exists.

## ADR-005 — 2026-11-24 UTC: original compiler/VM builds for Vita; service boundary is explicit

**Status:** accepted bounded technical result; no device compatibility or final graphics/audio architecture selected.

**VERIFIED E017:** upstream compiler/action/event/collision code is reused (22/22 preservation checks); the same headless core compiles/links for ARMv7 and converts to VELF. On PC it compiles 181 scripts / 845 event trees and executes four original startup instructions, stopping at CleanMem.dll's first external binding request. No invented DLL result or skipped call; the initial dialog is not reached. Default desktop library compilation passes; E015's already adapted runner remains untouched.

**Decision:** continue route B using existing VM plus typed platform boundaries. Keep deferred CPU textures/encoded media distinct from unavailable GPU/audio operations, and explicitly reject missing services. No backend may report false upload/playback success. The first native integration obligation is the helper's actual external contract, before a modal/dialog implementation can be exercised. Retain existing INI/dialog compatibility patches for later integration; the inspection provider is not a full game frontend.

**Limits:** ARM execution, native filesystem/save behavior, module initialization, window/control presentation, renderer/audio output and device memory/frame pacing remain untested. Retained network/std imports are real link obligations, not measured usage. Host Rust heap peak (~103.1 MiB) is not Vita consumption. No phase exit, VPK/title ID or public game distribution is justified by this result.

**Next gate:** establish and implement honest native CleanMem service semantics, rerun unchanged startup to its next real request, and only then attach useful graphics/input/audio and test on hardware. [Evidence and reproducible code](OPENGMK_VM_PROBE.md).

## ADR-006 — 2026-11-24 UTC: measured helper adapter, explicit native failure and human dialog

**Status:** accepted bounded implementation. No successful native working-set cleanup or hardware execution established.

**VERIFIED E018:** complete helper export inspection establishes cdecl/zero-argument/real contracts for Windows working-set trim and signed32 current WorkingSetSize (zero on failure). Differential testing performs real current-process OS operations, observes matching queries and successful trims, and preserves handle count. Original startup binds/calls through OpenGMK's external registry. The existing real Windows dialog waits for the owner, whose High/result-3 response advances original VM execution from 11 to 15 instructions, then explicitly blocks at `set_program_priority`. Compiler/events/collisions remain unchanged, source audit passes 22/22. Updated ARM build/link and VELF conversion pass; E015 dialog/INI patches are preserved and desktop library compilation passes.

**Decision:** retain typed external/dialog services and reject unsupported signatures/services. Windows reproduces actual helper operations; Vita returns the original failure contract for unsupported Windows working-set operations, with separately labeled SDK free-memory diagnostics. This is justified failure behavior, not equivalent successful cleanup. The inspected newlib heap-break path does not release the reserved kernel block; `malloc_trim` is therefore not adopted as an unproven physical working-set substitute. Original startup ignores the cleanup result; no GML change or automatic dialog answer is needed.

**Limits:** Vita operation/metric equivalence remains BLOCKED; even the new diagnostic import has not executed on hardware. Do not map Windows priority classes to Vita threads or inherit upstream's priority no-op without a measured contract. Native graphics, audio, modal controls, files/saves, module initialization, memory fit and suspend/resume remain open. Host requested heap (~103.1 MiB peak) is not native RAM usage. Route B remains best supported; no phase exit, final backend, title ID or functional VPK follows from link success.

**Next gate:** measure and implement `set_program_priority` through the same boundary on PC, then resume unchanged startup to the next request. Before hardware, add persistent diagnostics to the real-data ARM executable and establish an owner-approved deployment method/identity; verify actual data/VM prefix and explicit native failures without a fictitious screen. [Contracts, exact commands, artifacts and diagnostic plan](OPENGMK_CLEANMEM_PROBE.md).

## ADR-007 — 2026-11-24 UTC: real native VM prefix and explicit owner diagnostic policy

**VERIFIED E019:** original runner static analysis shows priority changes BOTH process class and current thread; actual game uses 0/1/2. Windows PlatformServices performs both and verifies readback, then original startup reaches Files/file_exists at 16 instructions. Native ELF/VELF/SELF runs on the owner's physical Vita 1000: unchanged EXE hash, 181 compiled scripts / 845 event trees, 11 executed instructions to Dialog. Persistent log and installed SELF identity verified after exit; no crash marker. Native heap-request/free-memory counters are measured independently of PC figures.

**Decision:** continue the existing ARM compiler/VM with explicit services. Keep native priority unavailable until its contract can be justified; no Windows process-class/Vita-thread equivalence is asserted. Owner selected HOWAW1178 before private packaging and later explicitly requested **High/button 3** as a diagnostic default. Implement that opt-in preparer revision only, label its response as owner policy rather than real UI/manual input, reject subsequent dialogs, and retain original GML/data. Its same route passes on PC and on Vita: **15 instructions**, then honest Process/set_program_priority stop, exit 2. This narrowly authorized policy supersedes the earlier no-automatic-answer requirement for this diagnostic, not other service failures.

**Limits/next gate:** private VPK installation and native VM-prefix execution are verified, not graphical/gameplay compatibility. Native render/input/audio, files/saves, suspend/resume and full-game memory fit remain open. Original MP3 copied/verified on device; audio output still absent. Next discriminating experiment: resolve the actual native priority failure/service policy without false scheduling success, then advance this same original startup to its next service; retain real frontend work as a separate gate. [Full evidence/reproduction](OPENGMK_PRIORITY_PROBE.md).

## ADR-008 — 2026-11-25 UTC: initial native libvita2d/GXM backend, original VM stop retained

**VERIFIED E020:** the owner-requested initial backend attaches at the real `Game::launch`/`RendererTrait` atlas handoff, and the same Game's original logo renders on physical Vita 1000 with scale, rotation, alpha and batching. Installed HOWAW1178/00.21 SELF, original data/resource hashes, persistent VM/GPU/memory/timing log and owner's screen observation agree. Original GML/compiler/events/collisions remain preserved (22/22 audit); desktop check passes. Native VM still stops honestly at Process after 15 instructions before the diagnostic draw; this is not original menu execution.

**Decision:** use libvita2d over GXM provisionally for the initial 2D backend, without vitaGL. This supersedes ADR-004's proposed vitaGL-first renderer experiment, following the owner's explicit direction and this actual hardware proof. Keep the adapter narrow and add direct GXM only for measured requirements. Static game calls justify sprites/crops, scale/rotation/alpha, text, tiled backgrounds, 2D shapes and blend switching; absence of static 3D calls is not complete runtime coverage. Unsupported operations continue to fail explicitly. Route B remains best supported; no final full-game architecture or P2 exit is declared.

**Memory/performance limits:** one cached 16 MiB GPU page, 15,247,072 CPU pixel bytes released, 360 diagnostic frames / 600 batches, median wait-inclusive 16.680 ms. These are not gameplay/displayed FPS. All six current pages would total 96 MiB against 90 MiB measured free CDRAM after graphics init; simultaneous residency is not assumed viable. Measure the actual menu/arena page working set before choosing compaction/backing/eviction. Native input/audio, filesystem/INI behavior, viewport/state/primitive/gradient/blend completeness and suspend/resume remain open; no playable game VPK exists.

**Next one experiment:** establish the native representation of the original priority failure/void contract (reviewed routine does not check either Windows API return) without claiming successful equivalent scheduling, then resume the unchanged VM to its next real service. Preserve the current explicit Process error until that contract is justified. Do not rerun the already successful logo diagnostic merely to repeat its result. [Renderer design, exact tests, failures, hardware metrics and menu integration](OPENGMK_GRAPHICS_PROBE.md).

## ADR-009 — 2026-11-25 UTC: priority procedure completion and real persistent INI, audio remains explicit

**VERIFIED E021:** the reviewed original priority procedure executes both Windows calls even when actual invalid-handle requests fail, leaves the GML result slot unchanged, and returns normally for the game's 0/1/2 arguments. The bounded fixture executes only that hash-checked slice with integer-conversion/import substitutions, not the original runner startup. Original PC/Vita startup reaches **38 instructions / 28 calls** after real file/INI writes/readback; second PC process retains the profile and reaches the same sound_replace gate in 27 instructions. Native installed HOWAW1178/00.22 SELF/log/152-byte INI independently verified. Renderer unchanged, no logo repeat or GPU allocation.

**Decision:** supersede the strict native Process exception with explicit unavailable-effect records plus normal GM8 procedure completion. This return is not scheduler success; no Vita class/thread equivalence is invented. Windows records both actual API outcomes. Keep owner High policy separate. Reuse E015's INI write-through semantics with durable sync, dedicated persistent profile and real path/error/existence behavior; original inputs/saves remain untouched. Desktop behavior preserved; source audit 22/22 and fresh preparation 197/197.

**Limits/next experiment:** dynamic first-room entry is verified; unique static sound_replace site locates the Game Start stop, before successful menu Draw. Do not render partial state after an exception or treat Deferred sound as a decoded handle. Next prove real ARM MP3 decode/handle registration and memory for the original menu file, then adapt replacement with honest failure/success semantics. Original menu view/state/shapes/text/blend/presentation, controls, audio output and atlas working-set residency remain open. Route B/E020 backend retained; no P2 exit or functional game VPK. [Full E021 evidence](OPENGMK_STARTUP_SERVICES_PROBE.md).

## ADR-010 — 2026-11-25 UTC: reuse existing MP3 player/codec; registry success separate from playback

**VERIFIED E022:** original sound 140 replacement decodes and registers the actual hash-matching MP3 on PC/Vita. Reuse OpenGMK's streaming player and rmp3 0.3.1; detach only udon's pure Source interface from its unconditional libsoundio frontend. Actual sample counts/signal summaries match; valid Deferred/None/Mp3 transitions, failed-candidate retention, shared compressed ownership and release pass CPU contracts. Physical 00.23 reaches original Game::draw at 65 instructions on preserved profile; fresh PC profile reaches 76. No native playback or presented menu claimed.

**Decision:** keep this portable decoder/player path, retaining compressed bytes and bounded PCM scratch rather than a full-song float allocation. Box the player to avoid inflating unrelated sound slots; initialize scratch storage. Only successful decode/registration returns replacement success. Failure leaves the old asset intact as an explicit defensive policy whose exact vendor failure-side ownership remains unproven. Keep audio output services unavailable until a real sink exists. Desktop renderer/audio path and SIMD feature preserved; no new dependency versions or downloads.

**Graphics/next gate:** remove only the unused no-recorder framebuffer readback, retaining real recording's path. Extend E020 with the observed full-frame aspect mapping and clean teardown of an unpresented scene. The current depth-only clear still returns an explicit error; no pixels or clears are fabricated, no forced Draw after failed init. Next implement/verify a real depth-only GXM clear that preserves colour, then follow original Draw to its next operation. Decoder proof takes 6.846 s on this Vita and currently scans twice; startup optimization, audio output, object drawing, controls and full-game memory fit remain separate work. No P2 exit or functional game VPK. [Evidence/reproduction](OPENGMK_MP3_PROBE.md).

## ADR-011 — 2026-11-26 UTC: faithful 2D depth guard and original frame presentation

**VERIFIED E023:** upstream clear_zbuf makes the 2D menu call a no-op; E022's unconditional service stop was overstrict. A genuine color-mask-NONE GXM depth primitive separately passes physical depth/color/occlusion tests (all 1,024 samples). Original object Draw events run and Game::init completes at 105 instructions. One actual engine-generated frame is presented, with 10 sprites, one rectangle and five batches. Its 112 nonblack pixels do not establish a complete visible menu. The first caption failure remains recorded; revised execution stops at Window/poll_events before Game::frame.

**Decision:** retain RendererTrait/libvita2d, original atlas/event flow and ordered demand loading. Use direct GXM for the missing depth primitive/viewport, keeping unused 3D unavailable. Correct the additive preset to SRC_ALPHA/ONE; exact fractional-alpha/raster parity remains untested. Limit atlas residency to 64 MiB, with unsupported eviction explicit. Store asynchronous caption requests as metadata and log unavailable native titlebar effects, without claiming OS changes. Present only after successful original initialization; stop at the missing input pump instead of skipping it or inventing input.

Validate MP3 during the existing decoded length scan: PC scan/stream comparison passes and each candidate still decodes with errors checked. Native measured interval falls from 6.846 s to 3.630 s, without full-song PCM retention or playback claims. Existing VM/objects/events/collisions and Game::frame remain original; inputs/lock unchanged, recovery zero. Next actual input/event polling and normal frame progression; no functional game VPK, native audio output, full-menu claim or P2 exit. [Evidence](OPENGMK_DRAW_PROBE.md).

## ADR-012 — 2026-11-26 UTC: original frame flow, native audio and measured atlas overflow

**VERIFIED E024–E026:** reuse the complete original normal run loop after successful Game::init, with genuine Vita Ctrl/Touch snapshots feeding existing Input. Original Step/Draw/order and30Hz room speeds remain unchanged. E025 owner confirms animated original menu, right-stick/X navigation and audible music; native SceAudioOut counters/cleanup verify actual PCM submission. E026 owner confirms full-screen mapping; real active-scene color/depth clear passes1,024+1,024 GPU pixel checks and advances to requested room6, where a fifth16MiB atlas exceeds the existing64MiB cap. Native free-user110MiB/free-CDRAM26MiB measured; no arena frame completed.

**Decision:** keep RendererTrait/libvita2d/GXM and reuse original Mixer/MP3/WAV/transforms with bounded alternating native output buffers. No replacement menu, GML edits, scheduler-success claim or mandatory vitaGL. Preserve30Hz simulation;60Hz presentation requires separate timing/design evidence and must not double original Step/Draw effects. Full960×544 stretch follows owner preference and uses corresponding touch conversion. GPU overflow pages may use bounded32MiB native uncached main RAM, retaining64MiB CDRAM and allocation headroom. Narrow owned texture allocation checks exact SDK pool/base/size/map errors; existing libvita2d drawing/free remain. Release CPU pixels only after successful direct upload, without eviction, redecoding or duplicate residency.

**Limits/next:** E027 pool/input/audio CPU contracts, host/ARM/C bridge compile PASS; E027 actual fifth-page allocation/CPU payload release and native cleanup PASS in two Vita runs. Mapped-RAM sampling/arena display remain UNVERIFIED: Draw next stops at source crop; customization separately requests an outline. E028 implements those two measured contracts, PC/ARM PASS and physical test pending. All options/controls, touch observation, suspend/resume, pixel parity, long-session stability and Firefight playability remain open. Continue the next actual service without bypassing original room/events; only add residency/culling work if measured. [Compact evidence](OPENGMK_RUNTIME_PROGRESS.md), [active plan](ACTIVE_PLAN.md).
