# Active work — E032 sustained gameplay and measured performance

Historical stages and artifacts: OPENGMK_RUNTIME_PROGRESS.md / EXPERIMENTS.md.

- [x] Retrieve E031 physical log and installed SELF/SFO before changes. HOWAW1178/00.32 verified; closure is cumulative diagnostic instruction cap1,000,000, panic at1,000,001. Not frame2700, GXM, audio or memory failure.
- [x] Baseline sparse samples: upper-median residual main-thread wall1.317ms menu /37.320ms room6; separate GPU/display waits available. No old object/phase distributions: GML-versus-render cause unresolved.
- [x] Explicit5million AST-instruction watchdog per frame after successful init; preserve original VM and2700-frame diagnostic bound. Guard/flag PC contract PASS.
- [x] Bounded exclusive phase windows, object/render/heap/audio counters; Game::frame byte-identical, audit22/22 timing-only event/collision/VM probes PASS.
- [x] Tint scratch/fixed arrays, redundant-state flush avoidance and earlier conservative culling.2000 baseline-equivalent geometry cases PASS;475,000→0 allocations per5000-call CPU benchmark, no native FPS claim.
- [x] Installed libvita2d queue/sync audit; retain GPU lifetime fence, explicit drain on capture/exit/unwind. Native correctness/performance still requires hardware.
- [x] Final PC/ARM/C-Werror regressions; one private HOWAW1178/00.33 e032-ed8caf61.vpk transferred/hash verified. Baseline flag active; same binary supports both modes, no reinstall needed between runs.
- [ ] Retrieve E032 baseline log/installed SELF/SFO, classify termination and full low/high-load windows. Archive only own diagnostic flag to activate optimized mode.
- [ ] Owner repeats same character/room6/route with optimized mode; retrieve and compare objects/instructions/visible draws, exclusive timings/audio/memory. Do not infer global quantiles or controlled speedup from unmatched live gameplay.
- [ ] Target dominant measured CPU/GPU/diagnostic stage or first real service/fault. No original AI/collision/event changes without faithful contracts and measured need.

Direct main; no branches, originals/builds/data preserved. Same original30Hz simulation; no disabled objects/events/AI/collisions or fabricated FPS. Latest proven E031 combat proceeds until diagnostic cap; E032 physical A/B pending. [Measurements, protocol and exact next test](OPENGMK_PERFORMANCE_PROBE.md).
