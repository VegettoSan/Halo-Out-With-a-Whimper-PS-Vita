# Active work — collision cost after verified E032

Current evidence: [performance report](OPENGMK_PERFORMANCE_PROBE.md). Historical stages remain in EXPERIMENTS.md.

- [x] E031 latest physical log/installed identity analyzed before code. Cause: inherited cumulative AST diagnostic cap, not2700-frame normal exit or observed graphics/audio/memory failure.
- [x] E032 one HOWAW1178/00.33 e032-ed8caf61.vpk, baseline and optimized same-binary physical runs each2700 frames/exit0, cumulative>1million, native pools restored/audio errors0. Owned baseline flag archived; installed mode is optimized.
- [x] Exclusive timings and geometry/allocation/state/queue changes validated. Early comparable arena processing49.982→43.571ms p50; combat still~100ms with collision dominant. No stable30Hz/FPS claim or phase completion.
- [x] E033 CPU/ARM cached-box candidate:20000 result+bbox-side-effect cases PASS, original fallback preserved, delta audit25/25, integrated CPU kernel~7–11% faster. No second VPK; candidate is not included in installed00.33.
- [ ] Measure collision-method mix (pair/point/line/rectangle/ellipse/solid/any), cached-box rejection rate and native profiler overhead. Preserve original iteration order and dynamic invalidation; distinguish helper cost from collision-event GML spikes.
- [ ] Use those measurements to select a further faithful optimization. Cached-box candidate source is local-tools/collision-20261126/OpenGMK; it still carries E032 markers and must receive a new diagnostic identity before any future packaging. Never overwrite00.33/older artifacts.
- [ ] Next separately versioned device experiment: same character/room6 low/high combat load, original30Hz frame loop, explicit bound/exit classification; compare original candidate toggles with method counts and calibrated instrumentation. Do not generate another VPK in the completed E032 comparison round.
- [ ] Confirm remaining coverage explicitly: customization regression in new revision if not established, additional rooms, long play beyond2700frames, suspend/resume and persistence. Pixel read/dynamic texture/arbitrary state services remain honest boundaries if requested.

Direct main; originals/builds/local data preserved. No disabled AI/collisions/events/projectiles, altered GML/resources or room_speed change. Route B/original OpenGMK VM + native libvita2d/GXM remains best supported; full Firefight parity and performance are incomplete.
