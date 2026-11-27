# Active work — autonomous continuation from E023

Keep only current work here; historical evidence belongs in EXPERIMENTS.md.

- [x] E024 code/PC: input audit, real Ctrl/Touch bindings and pressed/held/released mapper; CPU contract PASS, ARM build PASS. Physical sampling/analog transitions and >180 original frames PASS; splash/fade seen by owner. Touch/button navigation still pending.
- [x] E024: normal Game::frame/Step/Draw flow runs on Vita; next actual gate Audio/sound_loop(140).
- [x] E025: original animated menu + right-stick/X navigation and music heard on Vita. Partial options/control coverage; touch still unverified.
- [ ] Implement required graphics operations from actual traces; retain the E020–E023 backend and atlas budget.
- [x] E025: native music/SFX output with original mixer/players; CPU contracts, ARM/desktop and Vita output/cleanup PASS. Routine telemetry buffered, error checkpoints durable.
- [x] E026: real level selection reaches room loading; fix active-scene color clear, full-display mapping and camera translation. CPU/ARM/Vita clear and full-display PASS. Next atlas page2 exceeds existing64MiB cap; room6 not rendered yet.
- [x] E027: fifth atlas allocated once in16MiB main RAM,64MiB CDRAM retained. CPU pixel release and native cleanup PASS. Main-RAM sampling not yet verified; original Draw stops at sprite crop.
- [x] E028: original customization selection works on Vita; source-edge clamps pass in rooms6/16, first room6 image presented/read back. Next debug-output service and temporary vertex-pool exhaustion identified separately.
- [x] E029: rooms6/16 countdowns execute; debug sink and general culling/pool PASS on Vita. Culls>94k per run, pool peaks~50–52KiB/no failure. Next both stop at textured per-vertex color; measured~50ms frames fail30Hz budget.
- [x] E030: native corner-color shader PASS; owner enters original gameplay/moves/shoots. Next enemy-fire draw_line_width stop at1,569 frames. Last window p5066.7/p9583.4ms; stable play/performance incomplete.
- [ ] E031: general plain/gradient/width lines, circle family/default precision, separated native GPU/display waits. Eleven geometry tests, service contracts/reuse22/22 and PC/ARM/C/VELF PASS; HOWAW1178/00.32 e031-0a03bc14.vpk transferred/verified, physical combat test pending.
- [ ] Next retrieve e031 logs + installed SELF, verify combat/shapes and new boundaries. Use graphics-timing versus original-frame to choose measured performance work; real pixel reads/dynamic capture remain next unimplemented families if called.

Current verified baseline: E025 original animated menu, right-stick/X navigation and audible music on physical Vita; normal frames execute. E028 customization selection and first original room6 image PASS. E030 post-countdown original gameplay/movement/shader PASS; enemy-fire line-width stop. E031 correction/profiling delivered, awaiting hardware logs. Functional private menu diagnostic exists; playable Firefight remains unverified. HOWAW1178; direct main; previous builds preserved.

Owner preference: fill the physical display in E026. 60fps requested; original room simulation30Hz verified. Preserve Step/Draw semantics; do not claim60 through duplicate frames or silently speed up GML.
