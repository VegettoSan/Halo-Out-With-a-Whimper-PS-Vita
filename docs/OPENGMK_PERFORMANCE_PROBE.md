# E032 — sustained original execution and measured renderer work

2026-11-27 UTC (November26 owner-local). Original EXE/GML/resources, Game::frame and30Hz simulation retained. No new resource recovery, downloads or installations. Native graphics remain libvita2d/GXM; native audio remains the existing decoder/mixer/SceAudioOut path.

## E031 physical diagnosis, before source changes

**VERIFIED:** retrieved every available e031 log and installed SELF/SFO first. Installed HOWAW1178/00.32 SELF SHA-256 `4d22ca88dae7d2527e4575615ce4e5a6e2567932653d78df6c332a0f9f3fa2f9` matches the delivered package. Log SHA-256 `f578b66a185bbffd1cb98f7c98817a6894b443a83e35cc270edd58a057f14f97` ends at `Builtin/instruction_budget instructions=1000001`, panic/exit1. The inherited E017 guard counted all AST instructions across the session. Last completed checkpoint1920, input poll1946; exact last completed frame is not recorded. Native width-line execution is logged. Circle execution/pixel parity remain UNTESTED.

This was **not** the2700-frame normal diagnostic exit. No GXM, allocation or audio failure precedes the panic. Audio3638 blocks, drain/release/error0; native pools restore on cleanup. Exit heap17,530B. At the last checkpoints live heap~25.25MB, lifetime peak108,121,376B, resident atlas64MiB CDRAM+16MiB mapped main RAM; vertex pool peak50,432B of1MiB, failed requests0. This diagnoses this closure; it does not prove absence of other future failures.

Sparse checkpoint distributions after frame120, in milliseconds:

| Original room | Samples | Processing p50/p95/peak | EndScene+GPU wait p50/p95/peak | Swap+queue wait p50/p95/peak | Remaining main-thread wall p50/p95/peak |
| --- | ---: | --- | --- | --- | --- |
| Menu0 |16|17.551/24.073/24.073|9.608/11.242/11.242|7.040/15.568/15.568|1.317/1.558/1.558|
| Arena6 |14|50.077/100.134/100.134|10.276/10.543/10.543|10.117/15.436/15.436|37.320/82.602/82.602|

These are **sparse**, not whole-run or complete-window quantiles; individual quantiles do not add together. Limiter sleep excluded. EndScene/wait includes driver work, not pure GPU execution. Remaining time includes VM, input, CPU geometry/submission and diagnostics; E031 cannot distinguish these. Arena frame1140 processing50.043ms, frame1860 processing100.134ms while end/GPU waits remain~10.4ms: main-thread growth is measured, its GML-versus-render cause is still unresolved.

Private evidence: `reports/local/shapes-20261126/device-run-1`, `device-validation.json`; parsed sparse report `reports/local/performance-20261126/baseline-analysis.json`. Use `tools/opengmk/analyze_native_frames.py` to reproduce without publishing GML/debug text.

## Changes and contracts

- After successful original initialization, reset a **5,000,000 AST-instruction watchdog per frame**; retain startup1,000,000 and session2700 frames. Watchdog errors identify diagnostic policy instead of falsely calling it an unavailable builtin. This is not a wall-time watchdog and skips no original instruction/event.
- Exclusive main-thread wall scopes distinguish Step/Draw/other/collision GML, event dispatch, collision helpers, CPU renderer, native submission, end/GPU wait, swap/queue and diagnostics. Per-room60-frame windows retain p50/p95/peak, object counts, instruction/allocation deltas, visible/culled sprites, vertices, batches, native draws and logical shader/texture/state changes. Separate asynchronous audio histograms record mix/convert costs excluding output wait. Collection/report/fsync overhead is separately reported; probe clock overhead is not fully calibrated and remains in the instrumented timings. No hardware GPU-cycle claim.
- Reuse fixed clipping arrays and a bounded tint scratch Vec; preserve both original triangle color planes and per-sprite edge clamping. Skip redundant identical blend-state flushes and reject axis-aligned offscreen sprites before trigonometry/UV construction. No simulation object/IA/collision/GML culling.
- Remove our extra display-queue drain per frame using libvita2d's existing bounded queued presentation. **Retain rendering completion before the single vertex pool is reused.** Drain rendering/display at capture/exit/unwind before freeing resources. Native texture/state error handling stays checked. Installed library disassembly confirms sync-object-backed queueing; actual performance/lifetime behavior remains a physical test requirement.
- Lower authored repetitive state/event/audio-command traces in optimized mode; original GML debug output and errors remain complete. No texture residency increase or repeated full-frame readback.

**VERIFIED PC:**12 geometry/profiler tests;2000 deterministic cases produce exactly the baseline f32 vertices, colors, UVs and clip decisions. Three optimized i686 geometry benchmark rounds of5000 calls: old32.758/31.710/30.776ms, new22.575/24.620/23.789ms;475,000 allocations each round become0 after warmup. This is a CPU kernel benchmark, **not** Vita FPS or whole-game improvement. Native audio WAV/mix/loop/stop/histogram, input, real debug sink and watchdog/flag contracts PASS. Watchdog test passes over1.1million cumulative instructions across resets and deliberately catches its next limit panic. VM audit22/22; original Game::frame byte-identical, timing probes are the only normalized event/collision/execute additions; GML inventory hash unchanged. Preparation initially FAIL from an incorrect feature-list assumption, preserved and corrected before fresh final preparation. Final host1m16s/ARM1m38s/C-Werror/VELF PASS. No Vita performance PASS from compilation.

## One binary, physical A/B protocol

Private **HOWAW1178/00.33** `e032-ed8caf61.vpk`: VPK SHA-256 `ed8caf6117d3f77dd5b672bb83d9a6de8f9e7345f88389a9fcc85022f2f41ec0`; SELF `e6f40c6f7d902d316c204f238bffa735dce1adc7e64a0d8ef55dc7a6883dc212`. Package contains SELF/SFO only; original EXE remains external. Previous builds/data preserved. Transfer and remote original EXE/VPK hashes PASS.

Regular diagnostic flag `ux0:data/howaw/e032-baseline.flag` selects **baseline**: old allocating tint, full cull computation, redundant state flush, per-frame display drain and prior verbose traces. Both modes use identical profiler, watchdog, original VM/resources and fixed2700-frame bound. Without the flag, **optimized** selects the changes above. A directory or unreadable flag fails honestly. Only our known diagnostic flag is created/archived; original INI/resources are preserved. Log `perf-policy` verifies the selected mode.

1. Install once; baseline mode first. Check menu/customization, same character/room6, movement/shooting and wait for enemies; leave running to normal bound or actual failure.
2. Retrieve all e032 logs plus installed SELF/SFO, validate identity/termination. Archive only the owned flag, preserving it. Relaunch the same installed executable, choose the same scenario, repeat and retrieve again.
3. Analyze each log with `analyze_native_frames.py --installed-self ... --sfo ... --package build/performance32-device/package.json --version 00.33 --output ...`. Compare reports with `compare_native_profiles.py baseline.json optimized.json --output ...`, all files under ignored reports/local.

Reports retain each measured window rather than averaging quantiles. Suggested candidate windows share room,60samples and object/instruction p50 within10%; inspect visible workload, batches and peaks as well. Live controls/enemy state are not deterministic replay, candidates may reuse a window, and cannot establish a controlled causal speedup. Need actual native low/high-load distributions before targeting VM/collision changes. Physical E032 execution, sustained gameplay and before/after improvement are **UNTESTED pending owner runs**.

## Reproduce / pending

Sources `4953d81`, `2d1c5c4`, `af24fbe`; `python tools/opengmk/prepare_performance_probe.py --source local-tools/menu-probe-20261122/OpenGMK --output local-tools/performance-final-20261126/OpenGMK --udon-source local-tools/arena-probe-20261122/udon-work/src/source.rs`. Native bridge: `python tools/opengmk/prepare_graphics_native.py --input --audio --output build/performance32-final-native`. Exact offline host/ARM commands in `local-tools/performance-final-20261126/{host-build,arm-build}.cmd`; private commands, contracts, benchmark, SDK synchronization audit and parser fixtures in `reports/local/performance-20261126/`. Rust/Cargo1.100.0, MSVC14.50.35717, GCC15.2.0, same hard-float SDK/libvita2d/SDL shader rodata as E030, scalar ARM/no NEON. Preserved build/performance32-*; packaged final native ELF/VELF in build/performance32-final-arm, manifest in build/performance32-device.

**PASS:** exact E031 closure classification, native line execution, CPU contracts/allocation reduction, offline builds and private transfer. **FAIL:** E031 original30Hz processing budget. **BLOCKED:** physical E032 A/B comparison and dominant GML/render/collision attribution. Native optimization success and closure removal remain UNTESTED until logs show sustained execution and correct exit. Next: retrieve baseline, archive flag, optimized run; investigate the dominant measured high-load stage or first real error without altering original gameplay.
